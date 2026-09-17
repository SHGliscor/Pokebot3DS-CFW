#!/usr/bin/env python3
"""Add a guarded RNG_WRITE command to an already patched mGBA 3DS bridge.

Run this after the repository's existing bridge, RTC, and starter-gate patches.
The command only writes Ruby/Sapphire's known gRngValue address.
"""
from pathlib import Path
import sys

ADDRESS = 0x03004818
MARKER = "Pokebot3DS-CFW mGBA guarded gRngValue write"

HELPER = f"""
/* ===== {MARKER} ===== */
#define PB3_RS_RNG_WRITE_ADDR 0x{ADDRESS:08X}u

static void _pb3Write32(struct mGUIRunner* runner, uint32_t address, uint32_t value) {{
    runner->core->busWrite8(runner->core, address + 0, (value >> 0) & 0xFFu);
    runner->core->busWrite8(runner->core, address + 1, (value >> 8) & 0xFFu);
    runner->core->busWrite8(runner->core, address + 2, (value >> 16) & 0xFFu);
    runner->core->busWrite8(runner->core, address + 3, (value >> 24) & 0xFFu);
}}
/* ===== end {MARKER} ===== */
"""

COMMAND = f"""
    if (!strncmp(cmd, "RNG_WRITE ", 10)) {{
#ifdef M_CORE_GBA
        char *end = NULL;
        unsigned long value = strtoul(cmd + 10, &end, 16);
        if (end == cmd + 10 || *end != '\\\\0') {{
            _pb3Send(&peer, peerLen, "PB3 ERR RNG_WRITE_SYNTAX");
            return;
        }}
        struct mGameInfo info;
        memset(&info, 0, sizeof(info));
        runner->core->getGameInfo(runner->core, &info);
        if (strcmp(info.code, "AXVE") && strcmp(info.code, "AXPE")) {{
            _pb3Send(&peer, peerLen, "PB3 ERR RNG_WRITE_UNSUPPORTED_GAME");
            return;
        }}
        _pb3Write32(runner, PB3_RS_RNG_WRITE_ADDR, (uint32_t) value);
        char out[96];
        snprintf(out, sizeof(out), "PB3 OK RNG_WRITE %08lX", value & 0xFFFFFFFFul);
        _pb3Send(&peer, peerLen, out);
#else
        _pb3Send(&peer, peerLen, "PB3 ERR NOT_GBA");
#endif
        return;
    }}

"""


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one marker, found {text.count(old)}")
    return text.replace(old, new, 1)


def main():
    if len(sys.argv) == 2:
        path = Path(sys.argv[1].strip('"'))
    else:
        print("This patch must target the upstream mGBA source file:")
        print("  upstream\\src\\platform\\3ds\\main.c")
        print()
        print("It cannot patch the Pokebot ZIP folder by itself.")
        raw = input("Drag main.c here, then press Enter (or type its path): ").strip()
        if not raw:
            raise SystemExit("No main.c path supplied.")
        path = Path(raw.strip('"'))
    if not path.is_file() or path.name.lower() != "main.c":
        raise SystemExit(f"File not found or not main.c: {path}")
    text = path.read_text(encoding="utf-8")
    if MARKER in text:
        print("gRngValue write patch already applied")
        return
    text = replace_once(
        text,
        "static void _pb3BridgePoll(struct mGUIRunner* runner) {",
        HELPER + "\nstatic void _pb3BridgePoll(struct mGUIRunner* runner) {",
        "helper insertion",
    )
    text = replace_once(
        text,
        '\t_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");\n}',
        COMMAND + '\t_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");\n}',
        "command insertion",
    )
    path.write_text(text, encoding="utf-8")
    print(f"Applied guarded gRngValue write patch to {path}")


if __name__ == "__main__":
    main()
