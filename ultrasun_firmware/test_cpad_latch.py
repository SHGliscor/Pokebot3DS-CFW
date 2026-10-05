from pathlib import Path
import sys

if len(sys.argv) != 4:
    raise SystemExit("usage: test_cpad_latch.py <controller.c> <bridge.c> <controller.h>")

controller = Path(sys.argv[1]).read_text(encoding="utf-8")
bridge = Path(sys.argv[2]).read_text(encoding="utf-8")
header = Path(sys.argv[3]).read_text(encoding="utf-8")

required_controller = [
    "#define POKEBOT_CMD_CPAD_LATCH  14",
    "#define POKEBOT_KIND_CPAD_LATCH  5",
    "#define POKEBOT_INPUT_CAPS     0x000003CFUL",
    "sInput.kind == POKEBOT_KIND_CPAD_LATCH",
    "static u16 startCpadLatch(",
    "PokebotInput_SetRemoteCircle(cpadState);",
    "else if (command == POKEBOT_CMD_CPAD_LATCH)",
]
for needle in required_controller:
    if needle not in controller:
        raise AssertionError(f"missing controller latch invariant: {needle}")

if "if (sInput.kind == POKEBOT_KIND_HID_LATCH ||\n        sInput.kind == POKEBOT_KIND_CPAD_LATCH)\n        return;" not in controller:
    raise AssertionError("persistent CPAD latch must bypass timeout update")

if "if (active() && sInput.kind != POKEBOT_KIND_CPAD_LATCH)" not in controller:
    raise AssertionError("CPAD latch updates must replace an existing CPAD latch without BUSY")

if "req->command == 14" not in bridge:
    raise AssertionError("bridge does not route CPAD_LATCH command 14")

if "startCpadLatch" in header:
    raise AssertionError("CPAD latch implementation leaked into public header")

if "svcWriteProcessMemory" in bridge:
    raise AssertionError("game-process RAM write path present")

print("CPAD latch regression: PASS")
