from pathlib import Path

p = Path("/tmp/ctrpf/Library/source/pluginInit.cpp")
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, got {count}: {old[:120]!r}")
    text = text.replace(old, new, 1)


# v0p8 HID locator support.
# Record the actual shared-memory mappings seen by CTRPF's svcMapMemoryBlock hook.
# This is read-only instrumentation: it does not alter the game mapping or input.
replace_once(
    "static LightLock    g_onLoadCroLock;\n",
    "static LightLock    g_onLoadCroLock;\n\n"
    "extern \"C\"\n"
    "{\n"
    "    volatile u32 gPokebotSharedMapCount = 0;\n"
    "    volatile u32 gPokebotSharedMapAddr[16] = {};\n"
    "    volatile u32 gPokebotSharedMapPerm[16] = {};\n"
    "    volatile u32 gPokebotHidHeuristicAddr = 0;\n"
    "}\n",
    "locator globals",
)

replace_once(
    "    Result res = svcMapMemoryBlock(handle, (u32)sharedMem, myPerm, otherPerm);\n"
    "    if (R_SUCCEEDED(res) && sharedMem && CTRPluginFramework::FwkSettings::Get().UseGameHidMemory)\n",
    "    Result res = svcMapMemoryBlock(handle, (u32)sharedMem, myPerm, otherPerm);\n"
    "    if (R_SUCCEEDED(res) && sharedMem)\n"
    "    {\n"
    "        const u32 addr = (u32)sharedMem;\n"
    "        bool seen = false;\n"
    "        const u32 count = gPokebotSharedMapCount > 16 ? 16 : gPokebotSharedMapCount;\n"
    "        for (u32 i = 0; i < count; ++i)\n"
    "        {\n"
    "            if (gPokebotSharedMapAddr[i] == addr)\n"
    "            {\n"
    "                seen = true;\n"
    "                break;\n"
    "            }\n"
    "        }\n"
    "        if (!seen && gPokebotSharedMapCount < 16)\n"
    "        {\n"
    "            const u32 slot = gPokebotSharedMapCount++;\n"
    "            gPokebotSharedMapAddr[slot] = addr;\n"
    "            gPokebotSharedMapPerm[slot] = ((u32)myPerm & 0xFFFFu) | (((u32)otherPerm & 0xFFFFu) << 16);\n"
    "        }\n"
    "    }\n"
    "    if (R_SUCCEEDED(res) && sharedMem && CTRPluginFramework::FwkSettings::Get().UseGameHidMemory)\n",
    "record shared mappings",
)

replace_once(
    "        if (llabs(currSysTick - firstSysTick) < 1000000000ULL && llabs(currSysTick - firstSysTickTS) < 1000000000ULL &&\n"
    "        arrayIndex < 8 && arrayIndexTS < 8)\n"
    "            hidSetSharedMem((vu32*)sharedMem);\n",
    "        if (llabs(currSysTick - firstSysTick) < 1000000000ULL && llabs(currSysTick - firstSysTickTS) < 1000000000ULL &&\n"
    "        arrayIndex < 8 && arrayIndexTS < 8)\n"
    "        {\n"
    "            gPokebotHidHeuristicAddr = (u32)sharedMem;\n"
    "            hidSetSharedMem((vu32*)sharedMem);\n"
    "        }\n",
    "record HID heuristic mapping",
)

p.write_text(text, encoding="utf-8")
print("Patched CTRPluginFramework to expose shared-memory map candidates for Pokebot v0p8")
