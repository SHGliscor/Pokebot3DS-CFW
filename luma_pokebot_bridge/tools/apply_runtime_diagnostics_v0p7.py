from pathlib import Path

root = Path(__file__).resolve().parents[2] / "Luma3DS"
source_dir = root / "sysmodules" / "rosalina" / "source"
include_dir = root / "sysmodules" / "rosalina" / "include"

bridge_c = source_dir / "pokebot_ram_bridge.c"
controller_c = source_dir / "pokebot_input_controller.c"
controller_h = include_dir / "pokebot_input_controller.h"
menus_c = source_dir / "menus.c"


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f"v0p7 diagnostics marker not found: {label}")
    return text.replace(old, new, 1)


# Count controller-side writes to the remote HID state. These counters are
# observational only and do not alter pulse/latch timing or game RAM.
header = controller_h.read_text(encoding="utf-8")
header = replace_once(
    header,
    "extern volatile u32 pokebotInputCommands;\n",
    "extern volatile u32 pokebotInputCommands;\n"
    "extern volatile u32 pokebotHidAssertWrites;\n"
    "extern volatile u32 pokebotHidNeutralWrites;\n"
    "extern volatile u32 pokebotHidPulseCommands;\n"
    "extern volatile u32 pokebotHidLatchCommands;\n"
    "extern volatile u32 pokebotLastAssertRawHid;\n",
    "controller counter declarations",
)
controller_h.write_text(header, encoding="utf-8")

controller = controller_c.read_text(encoding="utf-8")
controller = replace_once(
    controller,
    "volatile u32 pokebotInputCommands = 0;\n",
    "volatile u32 pokebotInputCommands = 0;\n"
    "volatile u32 pokebotHidAssertWrites = 0;\n"
    "volatile u32 pokebotHidNeutralWrites = 0;\n"
    "volatile u32 pokebotHidPulseCommands = 0;\n"
    "volatile u32 pokebotHidLatchCommands = 0;\n"
    "volatile u32 pokebotLastAssertRawHid = POKEBOT_HID_NEUTRAL;\n",
    "controller counter storage",
)
controller = replace_once(
    controller,
    "        pokebotInputCommands = 0;\n"
    "        pokebotInputControllerEnabled = true;\n",
    "        pokebotInputCommands = 0;\n"
    "        pokebotHidAssertWrites = 0;\n"
    "        pokebotHidNeutralWrites = 0;\n"
    "        pokebotHidPulseCommands = 0;\n"
    "        pokebotHidLatchCommands = 0;\n"
    "        pokebotLastAssertRawHid = POKEBOT_HID_NEUTRAL;\n"
    "        pokebotInputControllerEnabled = true;\n",
    "controller counter reset",
)
controller = replace_once(
    controller,
    "static void neutral(void)\n{\n    PokebotInput_ResetRemote();\n",
    "static void neutral(void)\n{\n"
    "    PokebotInput_ResetRemote();\n"
    "    pokebotHidNeutralWrites++;\n",
    "neutral write counter",
)
controller = replace_once(
    controller,
    "    PokebotInput_SetRemoteHid(rawHid);\n"
    "    pokebotInputCommands++;\n",
    "    PokebotInput_SetRemoteHid(rawHid);\n"
    "    pokebotHidAssertWrites++;\n"
    "    pokebotHidPulseCommands++;\n"
    "    pokebotLastAssertRawHid = rawHid;\n"
    "    pokebotInputCommands++;\n",
    "pulse assert counter",
)
controller = replace_once(
    controller,
    "    sInput.kind = POKEBOT_KIND_HID_LATCH;\n"
    "    sInput.phase = POKEBOT_PHASE_LATCHED;\n"
    "    PokebotInput_SetRemoteTouch(POKEBOT_TOUCH_NEUTRAL);\n"
    "    PokebotInput_SetRemoteHid(rawHid);\n"
    "    pokebotInputCommands++;\n",
    "    sInput.kind = POKEBOT_KIND_HID_LATCH;\n"
    "    sInput.phase = POKEBOT_PHASE_LATCHED;\n"
    "    PokebotInput_SetRemoteTouch(POKEBOT_TOUCH_NEUTRAL);\n"
    "    PokebotInput_SetRemoteHid(rawHid);\n"
    "    pokebotHidAssertWrites++;\n"
    "    pokebotHidLatchCommands++;\n"
    "    pokebotLastAssertRawHid = rawHid;\n"
    "    pokebotInputCommands++;\n",
    "latch assert counter",
)
controller_c.write_text(controller, encoding="utf-8")


bridge = bridge_c.read_text(encoding="utf-8")
bridge = replace_once(
    bridge,
    '#include "menus.h"\n',
    '#include "menus.h"\n#include "menu.h"\n',
    "console model declaration include",
)
bridge = replace_once(
    bridge,
    "#define POKEBOT_MAP_ADDR       0x00100000UL\n",
    "#define POKEBOT_MAP_ADDR       0x00100000UL\n"
    "#define POKEBOT_BRIDGE_PRIORITY 0x20\n"
    "#define POKEBOT_IDLE_YIELD_US   2000\n",
    "runtime constants",
)
bridge = replace_once(
    bridge,
    "            svcSleepThread(2 * 1000 * 1000LL);\n",
    "            svcSleepThread(POKEBOT_IDLE_YIELD_US * 1000LL);\n",
    "idle-yield constant use",
)
bridge = replace_once(
    bridge,
    "                                 0x20, CORE_SYSTEM)))",
    "                                 POKEBOT_BRIDGE_PRIORITY, CORE_SYSTEM)))",
    "bridge-priority constant use",
)
bridge = replace_once(
    bridge,
    '"Pokebot3DS-Luma-v0p6-n3ds-fb1"',
    '"Pokebot3DS-Luma-v0p7-runtime-diag"',
    "bridge build identity",
)
bridge = replace_once(
    bridge,
    "    POKEBOT_CMD_READ      = 4,\n",
    "    POKEBOT_CMD_READ        = 4,\n"
    "    POKEBOT_CMD_DIAGNOSTICS = 15,\n",
    "diagnostics command enum",
)

query_struct = """typedef struct PokebotQueryInfo
{
    u32 base;
    u32 size;
    u32 perm;
    u32 state;
    u32 pageFlags;
} PokebotQueryInfo;
"""
diag_struct = query_struct + """
typedef struct PokebotRuntimeDiagnostics
{
    u32 diagnosticsProtocol;
    u32 consoleModel;
    u32 bridgePriority;
    u32 idleYieldUs;
    u32 firmwareRevision;
    u32 buildFlags;
    u32 bridgePackets;
    u32 bridgeReads;
    u32 inputCommands;
    u32 hidAssertWrites;
    u32 hidNeutralWrites;
    u32 hidPulseCommands;
    u32 hidLatchCommands;
    u32 lastAssertRawHid;
    char buildId[32];
} PokebotRuntimeDiagnostics;
"""
bridge = replace_once(bridge, query_struct, diag_struct, "diagnostics payload struct")

route_marker = "    PokebotTarget target;\n"
diag_route = """    if (req->command == POKEBOT_CMD_DIAGNOSTICS)
    {
        PokebotRuntimeDiagnostics diagnostics;
        memset(&diagnostics, 0, sizeof(diagnostics));
        diagnostics.diagnosticsProtocol = 1;
        diagnostics.consoleModel = isN3DS ? 2 : 1;
        diagnostics.bridgePriority = POKEBOT_BRIDGE_PRIORITY;
        diagnostics.idleYieldUs = POKEBOT_IDLE_YIELD_US;
        diagnostics.firmwareRevision = 7;
        diagnostics.buildFlags = 0x0000000FUL;
        diagnostics.bridgePackets = pokebotRamBridgePackets;
        diagnostics.bridgeReads = pokebotRamBridgeReads;
        diagnostics.inputCommands = pokebotInputCommands;
        diagnostics.hidAssertWrites = pokebotHidAssertWrites;
        diagnostics.hidNeutralWrites = pokebotHidNeutralWrites;
        diagnostics.hidPulseCommands = pokebotHidPulseCommands;
        diagnostics.hidLatchCommands = pokebotHidLatchCommands;
        diagnostics.lastAssertRawHid = pokebotLastAssertRawHid;
        strncpy(diagnostics.buildId, "v0p7-runtime-diag", sizeof(diagnostics.buildId));
        Pokebot_SendResponse(sock, remote, remoteLen, req, POKEBOT_STATUS_OK, 0,
                             &diagnostics, sizeof(diagnostics));
        return;
    }

"""
bridge = replace_once(bridge, route_marker, diag_route + route_marker, "diagnostics route")
bridge_c.write_text(bridge, encoding="utf-8")

menus = menus_c.read_text(encoding="utf-8")
menus = replace_once(
    menus,
    "Pokebot-Luma v0p6-n3ds-fb1",
    "Pokebot-Luma v0p7 runtime diagnostics",
    "Rosalina menu build identity",
)
menus_c.write_text(menus, encoding="utf-8")

print("Pokebot-Luma v0p7 runtime diagnostics applied.")
