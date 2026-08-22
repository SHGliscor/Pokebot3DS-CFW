from pathlib import Path

root = Path(__file__).resolve().parents[2] / "Luma3DS"
menus_path = root / "sysmodules" / "rosalina" / "source" / "menus.c"
text = menus_path.read_text(encoding="utf-8")

if "Pokebot-Luma v0p2" in text:
    raise SystemExit(0)

include_marker = '#include "luma_config.h"\n'
if include_marker not in text:
    raise SystemExit("include marker not found")

block = r'''

static bool sPokebotRamEnabled = false;
static bool sPokebotInputEnabled = false;

static void PokebotBridge_ToggleRam(void)
{
    sPokebotRamEnabled = !sPokebotRamEnabled;
}

static void PokebotBridge_ToggleInput(void)
{
    sPokebotInputEnabled = !sPokebotInputEnabled;
}

static void PokebotBridge_EnableBoth(void)
{
    sPokebotRamEnabled = true;
    sPokebotInputEnabled = true;
}

static void PokebotBridge_DisableBoth(void)
{
    sPokebotRamEnabled = false;
    sPokebotInputEnabled = false;
}

static void PokebotBridge_ShowStatus(void)
{
    Draw_Lock();
    Draw_ClearFramebuffer();
    Draw_FlushFramebuffer();
    Draw_Unlock();

    do
    {
        Draw_Lock();
        Draw_DrawString(10, 10, COLOR_TITLE, "Pokebot3DS Bridge");
        u32 posY = 30;
        posY = Draw_DrawFormattedString(10, posY, COLOR_WHITE,
            "Pokebot-Luma v0p2\n\nRAM Bridge:       %s\nInput Controller: %s\n\n",
            sPokebotRamEnabled ? "ON" : "OFF",
            sPokebotInputEnabled ? "ON" : "OFF");
        Draw_DrawString(10, posY, COLOR_WHITE,
            "Safe menu foundation.\nRuntime state only; reboot returns both OFF.\n\nPress B to go back.");
        Draw_FlushFramebuffer();
        Draw_Unlock();
    }
    while(!(waitInput() & KEY_B) && !menuShouldExit);
}

Menu pokebotBridgeMenu = {
    "Pokebot3DS Bridge",
    {
        { "Toggle RAM Bridge", METHOD, .method = &PokebotBridge_ToggleRam },
        { "Toggle Input Controller", METHOD, .method = &PokebotBridge_ToggleInput },
        { "Enable Both", METHOD, .method = &PokebotBridge_EnableBoth },
        { "Disable Both", METHOD, .method = &PokebotBridge_DisableBoth },
        { "Status", METHOD, .method = &PokebotBridge_ShowStatus },
        {},
    }
};
'''

text = text.replace(include_marker, include_marker + block, 1)
marker = '        { "Miscellaneous options...", MENU, .menu = &miscellaneousMenu },\n'
if marker not in text:
    raise SystemExit("menu marker not found")
text = text.replace(marker, marker + '        { "Pokebot3DS Bridge...", MENU, .menu = &pokebotBridgeMenu },\n', 1)
menus_path.write_text(text, encoding="utf-8")
