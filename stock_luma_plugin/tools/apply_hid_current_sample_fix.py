from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"HID current-sample patch expected one match, got {count}: {old[:120]!r}")
    text = text.replace(old, new, 1)


# v0p5 hardware finding:
# v0p4 proved UDP, protocol scheduling and physical-control coexistence, but
# Controller::InjectKey() did not produce a usable A press in ORAS. The pinned
# CTRPluginFramework implementation ORs the injected key into all eight HID
# history samples, which can erase the neutral->pressed edge a game expects.
#
# Keep physical HID as the owner. Add the synthetic key only to the CURRENT HID
# sample, once per plugin frame while the pulse/latch is active. This is additive
# (bitwise OR), so physical buttons remain intact.

replace_once(
    'extern "C" Result svcControlMemoryUnsafe(u32 *out, u32 addr0, u32 size, MemOp op, MemPerm perm);\n\n',
    'extern "C" Result svcControlMemoryUnsafe(u32 *out, u32 addr0, u32 size, MemOp op, MemPerm perm);\n'
    'extern "C" vu32 *hidSharedMem;\n\n',
)

replace_once(
    '                static const char payload[] = "Pokebot3DS-3GX-v0p4";\n',
    '                static const char payload[] = "Pokebot3DS-3GX-v0p5";\n',
)

for old, new in (
    ('Pokebot3DS 3GX v0p4: srvInit', 'Pokebot3DS 3GX v0p5: srvInit'),
    ('Pokebot3DS 3GX v0p4: allocate SOC shared memory', 'Pokebot3DS 3GX v0p5: allocate SOC shared memory'),
    ('Pokebot3DS 3GX v0p4: socInit', 'Pokebot3DS 3GX v0p5: socInit'),
    ('Pokebot3DS 3GX v0p4: UDP 4952 ready', 'Pokebot3DS 3GX v0p5: UDP 4952 ready'),
):
    replace_once(old, new)

helper = r'''    static void InjectCurrentHidKey(u32 keys)
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

replace_once(
    '    static void FrameTick()\n    {\n',
    helper + '    static void FrameTick()\n    {\n',
)

count = text.count('Controller::InjectKey(keys);')
if count != 2:
    raise SystemExit(f"HID current-sample patch expected two InjectKey sites, got {count}")
text = text.replace('Controller::InjectKey(keys);', 'InjectCurrentHidKey(keys);')

p.write_text(text, encoding="utf-8")
print("Applied Pokebot3DS v0p5 current-HID-sample edge injection patch")
