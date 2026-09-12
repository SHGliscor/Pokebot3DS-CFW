from pathlib import Path

root = Path(__file__).resolve().parents[1]
main_path = root / "Sources" / "Main.cpp"
overlay_path = root / "Sources" / "BridgeOverlay.hpp"
main = main_path.read_text(encoding="utf-8")
overlay = overlay_path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}: {old[:140]!r}")
    return text.replace(old, new, 1)


# v0p10 hardware finding:
# v0p9's bounded SHARED/ALIASED region search still never observed physical
# A/START, despite ORAS responding to the physical buttons. Stop searching the
# game's virtual address space. Instead open hid:USER manually, request the HID
# shared-memory object, and map a SECOND read-only view for diagnostics.
#
# IMPORTANT: this deliberately does NOT call hidInit(), and therefore never
# initializes ir:rst. That follows the raw-3GX approach used by CTRComposer for
# New-3DS-safe touch/input access.

main = replace_once(
    main,
    "#include <3ds.h>\n",
    "#include <3ds.h>\n#include <3ds/allocator/mappable.h>\n",
    "mappable include",
)

main = replace_once(
    main,
    "using namespace CTRPluginFramework;\n\n",
    "using namespace CTRPluginFramework;\n\n"
    "extern \"C\" volatile u32 gPokebotManualHidReady = 0;\n"
    "extern \"C\" volatile u32 gPokebotManualHidResult = 0;\n"
    "extern \"C\" volatile u32 gPokebotManualHidAddress = 0;\n"
    "extern \"C\" volatile u32 gPokebotManualHidIndex = 0;\n"
    "extern \"C\" volatile u32 gPokebotManualHidKeys = 0;\n"
    "extern \"C\" volatile u32 gPokebotPhysicalPad = 0;\n\n",
    "manual HID diagnostic globals",
)

# Put the manual HID state next to the existing bridge globals.
main = replace_once(
    main,
    "    static volatile bool gRunning = false;\n",
    "    static volatile bool gRunning = false;\n"
    "    static Handle gManualHidService = 0;\n"
    "    static Handle gManualHidMem = 0;\n"
    "    static Handle gManualHidEvents[5]{};\n"
    "    static vu32 *gManualHidMap = nullptr;\n",
    "manual HID handles",
)

helpers = r'''    static u32 ReadPhysicalPadRegister()
    {
        // Same uncached physical mirror used by Luma/raw 3GX plugins.
        volatile u32 *reg = reinterpret_cast<volatile u32 *>(0x10146000u | (1u << 31));
        return ((*reg) ^ 0x0FFFu) & 0x0FFFu;
    }

    static void CleanupManualHidReadOnly()
    {
        if (gManualHidMap != nullptr && gManualHidMem != 0)
            svcUnmapMemoryBlock(gManualHidMem, reinterpret_cast<u32>(gManualHidMap));

        if (gManualHidMem != 0)
        {
            svcCloseHandle(gManualHidMem);
            gManualHidMem = 0;
        }

        for (u32 i = 0; i < 5; ++i)
        {
            if (gManualHidEvents[i] != 0)
            {
                svcCloseHandle(gManualHidEvents[i]);
                gManualHidEvents[i] = 0;
            }
        }

        if (gManualHidService != 0)
        {
            svcCloseHandle(gManualHidService);
            gManualHidService = 0;
        }

        if (gManualHidMap != nullptr)
        {
            // libctru's mappableFree() currently only releases allocator bookkeeping.
            // The C-style void* cast intentionally drops volatile for that API.
            mappableFree((void *)gManualHidMap);
            gManualHidMap = nullptr;
        }

        gPokebotManualHidReady = 0;
        gPokebotManualHidAddress = 0;
        gPokebotManualHidIndex = 0;
        gPokebotManualHidKeys = 0;
    }

    static Result InitManualHidReadOnly()
    {
        CleanupManualHidReadOnly();
        gPokebotManualHidResult = 0;

        Result rc = srvGetServiceHandle(&gManualHidService, "hid:USER");
        if (R_FAILED(rc))
            rc = srvGetServiceHandle(&gManualHidService, "hid:SPVR");
        if (R_FAILED(rc))
        {
            gPokebotManualHidResult = static_cast<u32>(rc);
            return rc;
        }

        // HID GetIPCHandles command. Reply[3] is sharedmem; [4..8] are events.
        u32 *cmd = getThreadCommandBuffer();
        cmd[0] = 0x000A0000u;
        rc = svcSendSyncRequest(gManualHidService);
        if (R_SUCCEEDED(rc))
            rc = static_cast<Result>(cmd[1]);
        if (R_FAILED(rc))
        {
            gPokebotManualHidResult = static_cast<u32>(rc);
            CleanupManualHidReadOnly();
            return rc;
        }

        gManualHidMem = static_cast<Handle>(cmd[3]);
        for (u32 i = 0; i < 5; ++i)
            gManualHidEvents[i] = static_cast<Handle>(cmd[4 + i]);

        // A second read-only view is enough to prove the live PAD ring. No
        // service takeover and no ir:rst initialization is involved.
        gManualHidMap = static_cast<vu32 *>(mappableAlloc(0x2B0));
        if (gManualHidMap == nullptr)
        {
            rc = static_cast<Result>(0xFFFFFFFFu);
            gPokebotManualHidResult = static_cast<u32>(rc);
            CleanupManualHidReadOnly();
            return rc;
        }

        rc = svcMapMemoryBlock(gManualHidMem,
                               reinterpret_cast<u32>(gManualHidMap),
                               MEMPERM_READ, MEMPERM_DONTCARE);
        if (R_FAILED(rc))
        {
            gPokebotManualHidResult = static_cast<u32>(rc);
            CleanupManualHidReadOnly();
            return rc;
        }

        gPokebotManualHidAddress = reinterpret_cast<u32>(gManualHidMap);
        gPokebotManualHidReady = 1;
        gPokebotManualHidResult = 0;
        return 0;
    }

    static void UpdateManualHidReadOnly()
    {
        gPokebotPhysicalPad = ReadPhysicalPadRegister();

        if (!gPokebotManualHidReady || gManualHidMap == nullptr)
            return;

        u32 id = gManualHidMap[4];
        if (id > 7)
            id = 7;
        gPokebotManualHidIndex = id;
        gPokebotManualHidKeys = gManualHidMap[10 + id * 4] & 0x0FFFu;
    }

'''

main = replace_once(
    main,
    "    static u32 RemainingMsLocked(u64 now)\n",
    helpers + "    static u32 RemainingMsLocked(u64 now)\n",
    "manual HID helper insertion",
)

# v0p7 already samples at the start of FrameTick. Sample our independent
# read-only HID view there too.
main = replace_once(
    main,
    "        // Always sample the game's mapped HID ring, even when no PC input is active.\n"
    "        // This lets the v0p7 overlay compare real physical presses with synthetic writes.\n"
    "        RecordCurrentHid(0, false);\n",
    "        UpdateManualHidReadOnly();\n"
    "        // Keep the older CTRPF pointer diagnostic for comparison only.\n"
    "        RecordCurrentHid(0, false);\n",
    "FrameTick manual HID sample",
)

# Initialize after the overlay exists so failures can be shown rather than
# crashing startup.
main = replace_once(
    main,
    "        BridgeOverlay::Init();\n"
    "        OSD::Run(BridgeOverlay::Draw);\n"
    "        gInput = ActiveInput{};\n",
    "        BridgeOverlay::Init();\n"
    "        OSD::Run(BridgeOverlay::Draw);\n"
    "        InitManualHidReadOnly();\n"
    "        gInput = ActiveInput{};\n",
    "manual HID init in Start",
)

main = replace_once(
    main,
    "        gRunning = false;\n"
    "        OSD::Stop(BridgeOverlay::Draw);\n",
    "        gRunning = false;\n"
    "        CleanupManualHidReadOnly();\n"
    "        OSD::Stop(BridgeOverlay::Draw);\n",
    "manual HID cleanup in Stop",
)

main = main.replace('Pokebot3DS-3GX-v0p9', 'Pokebot3DS-3GX-v0p10')
main = main.replace('Pokebot3DS 3GX v0p9:', 'Pokebot3DS 3GX v0p10:')
main_path.write_text(main, encoding="utf-8")

# Overlay: show hardware register and independently mapped HID shmem together.
overlay = replace_once(
    overlay,
    'extern "C" vu32 *hidSharedMem;\n\nnamespace BridgeOverlay\n{\n',
    'extern "C" vu32 *hidSharedMem;\n'
    'extern "C" volatile u32 gPokebotManualHidReady;\n'
    'extern "C" volatile u32 gPokebotManualHidResult;\n'
    'extern "C" volatile u32 gPokebotManualHidAddress;\n'
    'extern "C" volatile u32 gPokebotManualHidIndex;\n'
    'extern "C" volatile u32 gPokebotManualHidKeys;\n'
    'extern "C" volatile u32 gPokebotPhysicalPad;\n\n'
    'namespace BridgeOverlay\n{\n',
    "overlay manual HID externs",
)

needle = (
    "        std::snprintf(line, sizeof(line), \"OldPtr:%08lX Hook:%08lX\",\n"
    "                      static_cast<unsigned long>(sLocatorHidPointer),\n"
    "                      static_cast<unsigned long>(sLocatorHeuristic));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
)
insert = needle + (
    "        std::snprintf(line, sizeof(line), \"HW:%03lX MAN:%03lX i%lu Ready:%s\",\n"
    "                      static_cast<unsigned long>(gPokebotPhysicalPad & 0x0FFFu),\n"
    "                      static_cast<unsigned long>(gPokebotManualHidKeys & 0x0FFFu),\n"
    "                      static_cast<unsigned long>(gPokebotManualHidIndex),\n"
    "                      gPokebotManualHidReady ? \"YES\" : \"NO\");\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        std::snprintf(line, sizeof(line), \"MANMAP:%08lX RC:%08lX\",\n"
    "                      static_cast<unsigned long>(gPokebotManualHidAddress),\n"
    "                      static_cast<unsigned long>(gPokebotManualHidResult));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
)
overlay = replace_once(overlay, needle, insert, "overlay manual HID lines")
overlay_path.write_text(overlay, encoding="utf-8")

print("Applied Pokebot3DS v0p10 manual hid:USER read-only diagnostic")
