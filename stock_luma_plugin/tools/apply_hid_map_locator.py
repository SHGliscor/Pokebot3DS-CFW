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


# v0p8 is a read-only HID locator. v0p7 showed that hidSharedMem itself stayed
# at zero while physical A/START still worked in ORAS. Instead of another blind
# injection attempt, expose every shared-memory mapping observed by CTRPF's
# svcMapMemoryBlock hook and rank HID-shaped mappings by live ring/timestamp data.

# Symbols exported by the tiny CTRPF build-time instrumentation patch.
overlay = replace_once(
    overlay,
    "namespace BridgeOverlay\n{\n",
    "extern \"C\" volatile u32 gPokebotSharedMapCount;\n"
    "extern \"C\" volatile u32 gPokebotSharedMapAddr[16];\n"
    "extern \"C\" volatile u32 gPokebotSharedMapPerm[16];\n"
    "extern \"C\" volatile u32 gPokebotHidHeuristicAddr;\n"
    "extern \"C\" vu32 *hidSharedMem;\n\n"
    "namespace BridgeOverlay\n{\n",
    "locator externs",
)

locator_code = r'''
    struct LocatorCandidate
    {
        u32 address{0};
        u32 index{0};
        u32 keys{0};
        u32 lastNonZero{0};
        u32 changes{0};
        u32 score{0};
        bool valid{false};
    };

    static u32 sLocatorLastKeys[16]{};
    static u32 sLocatorLastNonZero[16]{};
    static u32 sLocatorChanges[16]{};
    static bool sLocatorInitialised[16]{};
    static LocatorCandidate sLocatorTop[3]{};
    static u32 sLocatorMapCount = 0;
    static u32 sLocatorHeuristic = 0;
    static u32 sLocatorHidPointer = 0;
    static u64 sLocatorLastUpdateMs = 0;

    static u64 TickDelta(u64 a, u64 b)
    {
        return a >= b ? (a - b) : (b - a);
    }

    static bool BetterLocatorCandidate(const LocatorCandidate &a, const LocatorCandidate &b)
    {
        if (!a.valid)
            return false;
        if (!b.valid)
            return true;
        if (a.score != b.score)
            return a.score > b.score;
        if (a.changes != b.changes)
            return a.changes > b.changes;
        return a.address < b.address;
    }

    static void ConsiderLocatorCandidate(const LocatorCandidate &candidate)
    {
        if (!candidate.valid)
            return;

        for (u32 pos = 0; pos < 3; ++pos)
        {
            if (!BetterLocatorCandidate(candidate, sLocatorTop[pos]))
                continue;

            for (u32 move = 2; move > pos; --move)
                sLocatorTop[move] = sLocatorTop[move - 1];
            sLocatorTop[pos] = candidate;
            break;
        }
    }

    static void UpdateHidLocator()
    {
        const u64 nowMs = osGetTime();
        if (sLocatorLastUpdateMs != 0 && (nowMs - sLocatorLastUpdateMs) < 75)
            return;
        sLocatorLastUpdateMs = nowMs;

        for (u32 i = 0; i < 3; ++i)
            sLocatorTop[i] = LocatorCandidate{};

        u32 count = gPokebotSharedMapCount;
        if (count > 16)
            count = 16;
        sLocatorMapCount = count;
        sLocatorHeuristic = gPokebotHidHeuristicAddr;
        sLocatorHidPointer = reinterpret_cast<u32>(hidSharedMem);

        const u64 nowTick = svcGetSystemTick();

        for (u32 slot = 0; slot < count; ++slot)
        {
            const u32 address = gPokebotSharedMapAddr[slot];
            if (address == 0)
                continue;

            MemInfo info{};
            PageInfo page{};
            if (R_FAILED(svcQueryMemory(&info, &page, address)))
                continue;

            const u64 regionEnd = static_cast<u64>(info.base_addr) + static_cast<u64>(info.size);
            if ((info.perm & MEMPERM_READ) == 0 ||
                address < info.base_addr ||
                static_cast<u64>(address) + 0x2B0ULL > regionEnd)
                continue;

            volatile u32 *words = reinterpret_cast<volatile u32 *>(address);
            const u32 index = words[4];
            const u32 touchIndex = words[46];
            if (index > 7 || touchIndex > 7)
                continue;

            const u64 padTick = *reinterpret_cast<volatile u64 *>(address);
            const u64 touchTick = *reinterpret_cast<volatile u64 *>(address + 0xA8u);
            const u32 keys = words[10 + index * 4] & 0x0FFFu;

            if (!sLocatorInitialised[slot])
            {
                sLocatorInitialised[slot] = true;
                sLocatorLastKeys[slot] = keys;
            }
            else if (keys != sLocatorLastKeys[slot])
            {
                ++sLocatorChanges[slot];
                sLocatorLastKeys[slot] = keys;
            }

            if (keys != 0)
                sLocatorLastNonZero[slot] = keys;

            LocatorCandidate candidate{};
            candidate.address = address;
            candidate.index = index;
            candidate.keys = keys;
            candidate.lastNonZero = sLocatorLastNonZero[slot];
            candidate.changes = sLocatorChanges[slot];
            candidate.score = 2; // valid PAD and touch ring indexes
            candidate.valid = true;

            if (TickDelta(nowTick, padTick) < 1000000000ULL)
                candidate.score += 3;
            if (TickDelta(nowTick, touchTick) < 1000000000ULL)
                candidate.score += 3;
            if (candidate.changes != 0)
                candidate.score += 2;
            if (candidate.lastNonZero != 0)
                candidate.score += 1;
            if (address == sLocatorHeuristic)
                candidate.score += 2;

            ConsiderLocatorCandidate(candidate);
        }
    }

'''

overlay = replace_once(
    overlay,
    "    static bool Draw(const Screen &screen)\n",
    locator_code + "    static bool Draw(const Screen &screen)\n",
    "locator implementation insertion",
)

old_lines = (
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
)

new_lines = (
    "        UpdateHidLocator();\n"
    "        std::snprintf(line, sizeof(line), \"HID LOCATOR Maps:%lu\",\n"
    "                      static_cast<unsigned long>(sLocatorMapCount));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        std::snprintf(line, sizeof(line), \"Ptr:%08lX Heur:%08lX\",\n"
    "                      static_cast<unsigned long>(sLocatorHidPointer),\n"
    "                      static_cast<unsigned long>(sLocatorHeuristic));\n"
    "        y = screen.Draw(line, 4, y);\n\n"
    "        for (u32 i = 0; i < 3; ++i)\n"
    "        {\n"
    "            const LocatorCandidate &c = sLocatorTop[i];\n"
    "            if (!c.valid)\n"
    "                continue;\n"
    "            std::snprintf(line, sizeof(line),\n"
    "                          \"#%lu %08lX i%lu K:%03lX Seen:%03lX Ch:%lu S:%lu\",\n"
    "                          static_cast<unsigned long>(i + 1),\n"
    "                          static_cast<unsigned long>(c.address),\n"
    "                          static_cast<unsigned long>(c.index),\n"
    "                          static_cast<unsigned long>(c.keys),\n"
    "                          static_cast<unsigned long>(c.lastNonZero),\n"
    "                          static_cast<unsigned long>(c.changes),\n"
    "                          static_cast<unsigned long>(c.score));\n"
    "            y = screen.Draw(line, 4, y);\n"
    "        }\n\n"
)

overlay = replace_once(overlay, old_lines, new_lines, "replace v0p7 HID lines with locator")

overlay_path.write_text(overlay, encoding="utf-8")

main = main.replace('Pokebot3DS-3GX-v0p7', 'Pokebot3DS-3GX-v0p8')
main = main.replace('Pokebot3DS 3GX v0p7:', 'Pokebot3DS 3GX v0p8:')
main_path.write_text(main, encoding="utf-8")

print("Applied Pokebot3DS v0p8 read-only shared-memory HID locator")
