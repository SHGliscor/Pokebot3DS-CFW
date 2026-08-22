from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"HID locator patch expected one match, got {count}: {old[:140]!r}")
    text = text.replace(old, new, 1)


# v0p7 is deliberately diagnostic-only for HID. v0p4 networking/SOC and the
# read-only RAM bridge remain untouched. Synthetic button writes are disabled
# while we locate the actual live PAD shared-memory mapping ORAS consumes.

replace_once(
    '                static const char payload[] = "Pokebot3DS-3GX-v0p6";\n',
    '                static const char payload[] = "Pokebot3DS-3GX-v0p7";\n',
)

for old, new in (
    ('Pokebot3DS 3GX v0p6: srvInit', 'Pokebot3DS 3GX v0p7: srvInit'),
    ('Pokebot3DS 3GX v0p6: allocate SOC shared memory', 'Pokebot3DS 3GX v0p7: allocate SOC shared memory'),
    ('Pokebot3DS 3GX v0p6: socInit', 'Pokebot3DS 3GX v0p7: socInit'),
    ('Pokebot3DS 3GX v0p6: UDP 4952 ready', 'Pokebot3DS 3GX v0p7: UDP 4952 ready'),
):
    replace_once(old, new)

# Disable synthetic button writes in this diagnostic build. Keep scheduling,
# protocol and status replies so the bridge remains easy to compare, but do not
# alter the HID buffer while locating it.
text = text.replace('InjectCurrentHidKey(keys);', '(void)keys; // v0p7 locator: injection disabled')

locator = r'''
namespace HidLocatorV0p7
{
    using namespace CTRPluginFramework;

    struct Candidate
    {
        u32 base{0};
        u32 index{0};
        u32 keys{0};
        u32 previousKeys{0};
        u32 changes{0};
    };

    static Candidate sCandidates[4]{};
    static u32 sCount = 0;
    static bool sScanned = false;

    static bool LooksLikeHid(u32 base, Candidate &out)
    {
        MemInfo info{};
        PageInfo page{};
        if (R_FAILED(svcQueryMemory(&info, &page, base)))
            return false;
        if ((info.perm & MEMPERM_READ) == 0)
            return false;
        if (base < info.base_addr || static_cast<u64>(base) + 0xC0 > static_cast<u64>(info.base_addr) + info.size)
            return false;

        volatile u32 *w = reinterpret_cast<volatile u32 *>(base);
        const u32 padIndex = w[4];
        const u32 touchIndex = w[46];
        if (padIndex > 7 || touchIndex > 7)
            return false;

        const u64 padTick = *reinterpret_cast<volatile u64 *>(base);
        const u64 touchTick = *reinterpret_cast<volatile u64 *>(base + 0xA8);
        const u64 now = svcGetSystemTick();
        const u64 padDelta = now > padTick ? now - padTick : padTick - now;
        const u64 touchDelta = now > touchTick ? now - touchTick : touchTick - now;
        if (padDelta > 1000000000ULL || touchDelta > 1000000000ULL)
            return false;

        out.base = base;
        out.index = padIndex;
        out.keys = w[10 + padIndex * 4] & 0x0FFFu;
        out.previousKeys = out.keys;
        out.changes = 0;
        return true;
    }

    static void ScanOnce()
    {
        if (sScanned)
            return;
        sScanned = true;
        sCount = 0;

        // Walk the process virtual-memory map using svcQueryMemory. We do not
        // read arbitrary large regions: only page starts of small readable
        // mappings are checked against the HID timestamp/index signature.
        u32 address = 0x00100000u;
        while (address < 0x40000000u && sCount < 4)
        {
            MemInfo info{};
            PageInfo page{};
            if (R_FAILED(svcQueryMemory(&info, &page, address)))
                break;

            const u64 regionEnd64 = static_cast<u64>(info.base_addr) + info.size;
            u32 next = regionEnd64 >= 0x40000000ULL ? 0x40000000u : static_cast<u32>(regionEnd64);
            if (next <= address)
                next = address + 0x1000u;

            if ((info.perm & MEMPERM_READ) != 0 && info.size <= 0x20000u)
            {
                const u32 start = (info.base_addr + 0xFFFu) & ~0xFFFu;
                for (u32 p = start; p < next && sCount < 4; p += 0x1000u)
                {
                    Candidate c{};
                    if (LooksLikeHid(p, c))
                    {
                        bool duplicate = false;
                        for (u32 i = 0; i < sCount; ++i)
                            if (sCandidates[i].base == c.base)
                                duplicate = true;
                        if (!duplicate)
                            sCandidates[sCount++] = c;
                    }
                }
            }

            address = next;
        }

        OSD::Notify(Utils::Format("HID locator: %lu candidate(s)", static_cast<unsigned long>(sCount)));
    }

    static void Update()
    {
        ScanOnce();
        for (u32 i = 0; i < sCount; ++i)
        {
            Candidate &c = sCandidates[i];
            volatile u32 *w = reinterpret_cast<volatile u32 *>(c.base);
            u32 idx = w[4];
            if (idx > 7)
                continue;
            const u32 keys = w[10 + idx * 4] & 0x0FFFu;
            c.index = idx;
            c.previousKeys = c.keys;
            c.keys = keys;
            if (c.keys != c.previousKeys)
                ++c.changes;
        }
    }

    static bool Draw(const Screen &screen)
    {
        if (!screen.IsTop)
            return false;

        Update();
        u32 y = 142;
        y = screen.Draw("HID LOCATOR v0p7 (READ ONLY)", 4, y);
        if (sCount == 0)
        {
            screen.Draw("No HID-like candidates found", 4, y);
            return true;
        }

        char line[96]{};
        for (u32 i = 0; i < sCount && i < 3; ++i)
        {
            const Candidate &c = sCandidates[i];
            std::snprintf(line, sizeof(line),
                          "C%lu %08lX idx:%lu keys:%03lX chg:%lu",
                          static_cast<unsigned long>(i + 1),
                          static_cast<unsigned long>(c.base),
                          static_cast<unsigned long>(c.index),
                          static_cast<unsigned long>(c.keys),
                          static_cast<unsigned long>(c.changes));
            y = screen.Draw(line, 4, y);
        }
        return true;
    }
}

'''

marker = '\nnamespace CTRPluginFramework\n{\n'
if marker not in text:
    raise SystemExit('HID locator patch could not find CTRPluginFramework namespace marker')
text = text.replace(marker, '\n' + locator + marker, 1)

replace_once(
    '        BridgeOverlay::Init();\n        OSD::Run(BridgeOverlay::Draw);\n',
    '        BridgeOverlay::Init();\n        OSD::Run(BridgeOverlay::Draw);\n        OSD::Run(HidLocatorV0p7::Draw);\n',
)

replace_once(
    '        OSD::Stop(BridgeOverlay::Draw);\n',
    '        OSD::Stop(HidLocatorV0p7::Draw);\n        OSD::Stop(BridgeOverlay::Draw);\n',
)

p.write_text(text, encoding="utf-8")
print("Applied Pokebot3DS v0p7 read-only HID locator diagnostic")
