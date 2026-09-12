from pathlib import Path

root = Path(__file__).resolve().parents[1]
main_path = root / "Sources" / "Main.cpp"
overlay_path = root / "Sources" / "BridgeOverlay.hpp"
main = main_path.read_text(encoding="utf-8")
overlay = overlay_path.read_text(encoding="utf-8")

# v0p9 hardware finding:
# v0p8 observed one svcMapMemoryBlock mapping (0x060BCA40), but its HID-shaped
# fields stayed zero while real A/START worked. That proves the mapping hook did
# not capture the live ORAS PAD ring. v0p9 therefore does a bounded READ-ONLY
# enumeration of already-mapped SHARED/ALIASED regions and ranks page-aligned
# HID-shaped candidates by live timestamps and physical-key changes.

start = overlay.find("    static void UpdateHidLocator()\n")
end = overlay.find("    static bool Draw(const Screen &screen)\n", start)
if start < 0 or end < 0:
    raise SystemExit("v0p9 could not locate UpdateHidLocator/Draw markers")

replacement = r'''    static void UpdateHidLocator()
    {
        const u64 nowMs = osGetTime();
        if (sLocatorLastUpdateMs != 0 && (nowMs - sLocatorLastUpdateMs) < 50)
            return;
        sLocatorLastUpdateMs = nowMs;

        for (u32 i = 0; i < 3; ++i)
            sLocatorTop[i] = LocatorCandidate{};

        sLocatorMapCount = 0;
        sLocatorHeuristic = gPokebotHidHeuristicAddr;
        sLocatorHidPointer = reinterpret_cast<u32>(hidSharedMem);

        const u64 nowTick = svcGetSystemTick();
        u32 address = 0;
        u32 slot = 0;
        u32 regionsVisited = 0;

        // svcQueryMemory reports whole regions, so this is bounded by region
        // count rather than a byte-by-byte RAM scan. Only SHARED/ALIASED pages
        // are inspected, and only the small HID header/ring fields are read.
        while (address < 0x40000000u && regionsVisited < 512 && slot < 16)
        {
            MemInfo info{};
            PageInfo page{};
            if (R_FAILED(svcQueryMemory(&info, &page, address)))
                break;
            ++regionsVisited;

            const u64 next64 = static_cast<u64>(info.base_addr) + static_cast<u64>(info.size);
            if (next64 <= address || next64 > 0x100000000ULL)
                break;

            const bool interestingState =
                info.state == MEMSTATE_SHARED ||
                info.state == MEMSTATE_ALIASED ||
                info.state == MEMSTATE_ALIAS;

            if (interestingState && (info.perm & MEMPERM_READ) != 0 && info.size >= 0x2B0u)
            {
                const u64 regionEnd = next64;
                for (u32 candidateAddress = info.base_addr;
                     slot < 16 && static_cast<u64>(candidateAddress) + 0x2B0ULL <= regionEnd;
                     candidateAddress += 0x1000u)
                {
                    volatile u32 *words = reinterpret_cast<volatile u32 *>(candidateAddress);
                    const u32 index = words[4];
                    const u32 touchIndex = words[46];
                    if (index > 7 || touchIndex > 7)
                        continue;

                    const u64 padTick = *reinterpret_cast<volatile u64 *>(candidateAddress);
                    const u64 touchTick = *reinterpret_cast<volatile u64 *>(candidateAddress + 0xA8u);
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
                    candidate.address = candidateAddress;
                    candidate.index = index;
                    candidate.keys = keys;
                    candidate.lastNonZero = sLocatorLastNonZero[slot];
                    candidate.changes = sLocatorChanges[slot];
                    candidate.score = 2;
                    candidate.valid = true;

                    if (TickDelta(nowTick, padTick) < 1000000000ULL)
                        candidate.score += 4;
                    if (TickDelta(nowTick, touchTick) < 1000000000ULL)
                        candidate.score += 4;
                    if (candidate.changes != 0)
                        candidate.score += 4;
                    if (candidate.lastNonZero != 0)
                        candidate.score += 2;

                    ConsiderLocatorCandidate(candidate);
                    ++slot;
                }
            }

            address = static_cast<u32>(next64);
        }

        sLocatorMapCount = slot;
    }

'''

overlay = overlay[:start] + replacement + overlay[end:]
overlay = overlay.replace('HID LOCATOR Maps:%lu', 'HID REGION Candidates:%lu')
overlay = overlay.replace('Ptr:%08lX Heur:%08lX', 'OldPtr:%08lX Hook:%08lX')
overlay_path.write_text(overlay, encoding="utf-8")

main = main.replace('Pokebot3DS-3GX-v0p8', 'Pokebot3DS-3GX-v0p9')
main = main.replace('Pokebot3DS 3GX v0p8:', 'Pokebot3DS 3GX v0p9:')
main_path.write_text(main, encoding="utf-8")

print("Applied Pokebot3DS v0p9 bounded shared-region HID locator")
