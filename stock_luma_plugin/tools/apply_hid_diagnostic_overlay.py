from pathlib import Path

root = Path(__file__).resolve().parents[1]
main_path = root / "Sources" / "Main.cpp"
overlay_path = root / "Sources" / "BridgeOverlay.hpp"
main = main_path.read_text(encoding="utf-8")
overlay = overlay_path.read_text(encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label} expected one match, got {count}: {old[:120]!r}")
    return text.replace(old, new, 1)


# v0p7 is diagnostic-only. v0p6 proved that the real ORAS HID mapping can be
# obtained without breaking physical input, but synthetic A/START still were not
# consumed by the game. Record exactly what the mapped HID ring contains before
# and after each additive synthetic write, plus ring-index movement.

# ---- Overlay data ---------------------------------------------------------
overlay = replace_once(
    overlay,
    "        char lastAction[40];\n",
    "        char lastAction[40];\n"
    "        bool hidMapped;\n"
    "        u32 hidIndex;\n"
    "        u32 hidPrevious;\n"
    "        u32 hidCurrent;\n"
    "        u32 hidPostWrite;\n"
    "        u32 hidSyntheticMask;\n"
    "        u32 hidIndexChanges;\n"
    "        u32 hidWriteCount;\n",
    "overlay Snapshot fields",
)

overlay = replace_once(
    overlay,
    "    static char sLastAction[40] = \"---\";\n",
    "    static char sLastAction[40] = \"---\";\n"
    "    static bool sHidMapped = false;\n"
    "    static u32 sHidIndex = 0;\n"
    "    static u32 sHidPrevious = 0;\n"
    "    static u32 sHidCurrent = 0;\n"
    "    static u32 sHidPostWrite = 0;\n"
    "    static u32 sHidSyntheticMask = 0;\n"
    "    static u32 sHidIndexChanges = 0;\n"
    "    static u32 sHidWriteCount = 0;\n"
    "    static bool sHidIndexSeen = false;\n",
    "overlay globals",
)

record_fn = r'''
    static void RecordHidSample(bool mapped, u32 index, u32 previous,
                                u32 current, u32 postWrite, u32 syntheticMask,
                                bool wrote)
    {
        if (!sInitialised)
            return;

        LightLock_Lock(&sLock);
        sHidMapped = mapped;
        if (mapped)
        {
            if (sHidIndexSeen && index != sHidIndex)
                ++sHidIndexChanges;
            sHidIndexSeen = true;
            sHidIndex = index;
            sHidPrevious = previous;
            sHidCurrent = current;
            sHidPostWrite = postWrite;
            sHidSyntheticMask = syntheticMask;
            if (wrote)
                ++sHidWriteCount;
        }
        LightLock_Unlock(&sLock);
    }
'''

overlay = replace_once(
    overlay,
    "    static Snapshot GetSnapshot()\n",
    record_fn + "\n    static Snapshot GetSnapshot()\n",
    "overlay RecordHidSample insertion",
)

overlay = replace_once(
    overlay,
    "        out.lastError = sLastError;\n"
    "        SafeCopy(out.lastAction, sizeof(out.lastAction), sLastAction);\n",
    "        out.lastError = sLastError;\n"
    "        out.hidMapped = sHidMapped;\n"
    "        out.hidIndex = sHidIndex;\n"
    "        out.hidPrevious = sHidPrevious;\n"
    "        out.hidCurrent = sHidCurrent;\n"
    "        out.hidPostWrite = sHidPostWrite;\n"
    "        out.hidSyntheticMask = sHidSyntheticMask;\n"
    "        out.hidIndexChanges = sHidIndexChanges;\n"
    "        out.hidWriteCount = sHidWriteCount;\n"
    "        SafeCopy(out.lastAction, sizeof(out.lastAction), sLastAction);\n",
    "overlay snapshot copy",
)

overlay = replace_once(
    overlay,
    "        std::snprintf(line, sizeof(line), \"Cmd:%s  Packets:%lu\", CommandName(s.lastCommand), static_cast<unsigned long>(s.packetCount));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        if (s.lastError != 0)\n",
    "        std::snprintf(line, sizeof(line), \"Cmd:%s  Packets:%lu\", CommandName(s.lastCommand), static_cast<unsigned long>(s.packetCount));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        std::snprintf(line, sizeof(line), \"HIDMAP:%s Idx:%lu Changes:%lu\",\n"
    "                      s.hidMapped ? \"YES\" : \"NO\",\n"
    "                      static_cast<unsigned long>(s.hidIndex),\n"
    "                      static_cast<unsigned long>(s.hidIndexChanges));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        std::snprintf(line, sizeof(line), \"PAD prev:%03lX cur:%03lX post:%03lX\",\n"
    "                      static_cast<unsigned long>(s.hidPrevious & 0xFFFu),\n"
    "                      static_cast<unsigned long>(s.hidCurrent & 0xFFFu),\n"
    "                      static_cast<unsigned long>(s.hidPostWrite & 0xFFFu));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        std::snprintf(line, sizeof(line), \"SYN:%03lX Writes:%lu\",\n"
    "                      static_cast<unsigned long>(s.hidSyntheticMask & 0xFFFu),\n"
    "                      static_cast<unsigned long>(s.hidWriteCount));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        if (s.lastError != 0)\n",
    "overlay HID diagnostic lines",
)

overlay_path.write_text(overlay, encoding="utf-8")

# ---- Main HID sampling ----------------------------------------------------
old_helper = r'''    static void InjectCurrentHidKey(u32 keys)
    {
        if (keys == 0 || hidSharedMem == nullptr)
            return;

        // libctru reads hidSharedMem[4] as the current PAD history index and
        // the held-key word at 10 + index*4. Only touch that current sample.
        u32 id = hidSharedMem[4];
        if (id > 7)
            id = 7;

        hidSharedMem[10 + id * 4] |= keys;
        __sync_synchronize();
    }

'''

new_helper = r'''    static void RecordCurrentHid(u32 syntheticMask, bool applySynthetic)
    {
        if (hidSharedMem == nullptr)
        {
            BridgeOverlay::RecordHidSample(false, 0, 0, 0, 0, syntheticMask, false);
            return;
        }

        u32 id = hidSharedMem[4];
        if (id > 7)
            id = 7;
        const u32 previousId = (id + 7u) & 7u;
        const u32 previous = hidSharedMem[10 + previousId * 4];
        const u32 current = hidSharedMem[10 + id * 4];
        u32 postWrite = current;

        if (applySynthetic && syntheticMask != 0)
        {
            hidSharedMem[10 + id * 4] = current | syntheticMask;
            __sync_synchronize();
            postWrite = hidSharedMem[10 + id * 4];
        }

        BridgeOverlay::RecordHidSample(true, id, previous, current,
                                       postWrite, syntheticMask,
                                       applySynthetic && syntheticMask != 0);
    }

    static void InjectCurrentHidKey(u32 keys)
    {
        RecordCurrentHid(keys, true);
    }

'''
main = replace_once(main, old_helper, new_helper, "Main HID helper")

main = replace_once(
    main,
    "    static void FrameTick()\n"
    "    {\n"
    "        LightLock_Lock(&gInputLock);\n",
    "    static void FrameTick()\n"
    "    {\n"
    "        // Always sample the game's mapped HID ring, even when no PC input is active.\n"
    "        // This lets the v0p7 overlay compare real physical presses with synthetic writes.\n"
    "        RecordCurrentHid(0, false);\n"
    "        LightLock_Lock(&gInputLock);\n",
    "FrameTick diagnostic sample",
)

main = main.replace('Pokebot3DS-3GX-v0p6', 'Pokebot3DS-3GX-v0p7')
main = main.replace('Pokebot3DS 3GX v0p6:', 'Pokebot3DS 3GX v0p7:')
main_path.write_text(main, encoding="utf-8")

print("Applied Pokebot3DS v0p7 HID ring diagnostic overlay")
