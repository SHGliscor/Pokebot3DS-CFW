from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"game-HID patch expected one match, got {count}: {old[:120]!r}")
    text = text.replace(old, new, 1)


# v0p6 hardware finding:
# v0p5 proved the PC->UDP->scheduler path but ORAS still did not consume the
# synthetic A press. CTRPluginFramework defaults UseGameHidMemory to false,
# which means its hidSharedMem pointer is not the game's HID mapping. For a 3GX
# plugin that wants additive injection without taking ownership of hid:USER,
# the framework explicitly provides UseGameHidMemory=true.
#
# This asks CTRPF to hook the game's HID shared-memory mapping and point
# hidSharedMem at that mapping. We keep the current-sample additive OR injection
# from v0p5 so physical controls remain the normal source of truth.

replace_once(
    "    void PatchProcess(FwkSettings &settings)\n"
    "    {\n"
    "        (void)settings;\n"
    "        // Deliberately no hidInit(), no HID service takeover and no game RAM patches.\n"
    "    }\n",
    "    void PatchProcess(FwkSettings &settings)\n"
    "    {\n"
    "        // Use ORAS's own HID shared-memory mapping. CTRPF will not call hidInit()\n"
    "        // in this mode; physical game input remains the normal HID owner.\n"
    "        settings.UseGameHidMemory = true;\n"
    "        // Deliberately no game RAM patches and no direct HID service takeover.\n"
    "    }\n",
)

replace_once(
    '                static const char payload[] = "Pokebot3DS-3GX-v0p5";\n',
    '                static const char payload[] = "Pokebot3DS-3GX-v0p6";\n',
)

for old, new in (
    ('Pokebot3DS 3GX v0p5: srvInit', 'Pokebot3DS 3GX v0p6: srvInit'),
    ('Pokebot3DS 3GX v0p5: allocate SOC shared memory', 'Pokebot3DS 3GX v0p6: allocate SOC shared memory'),
    ('Pokebot3DS 3GX v0p5: socInit', 'Pokebot3DS 3GX v0p6: socInit'),
    ('Pokebot3DS 3GX v0p5: UDP 4952 ready', 'Pokebot3DS 3GX v0p6: UDP 4952 ready'),
):
    replace_once(old, new)

p.write_text(text, encoding="utf-8")
print("Applied Pokebot3DS v0p6 game-HID shared-memory mapping fix")
