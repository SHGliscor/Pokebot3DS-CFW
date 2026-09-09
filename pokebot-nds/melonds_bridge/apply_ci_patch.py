#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: apply_ci_patch.py <melonDS-switch-upscale-folder>")
        return 2

    repo = Path(sys.argv[1]).resolve()
    switch_dir = repo / "src" / "frontend" / "switch"
    main_cpp = switch_dir / "main.cpp"
    cmake = switch_dir / "CMakeLists.txt"

    if not main_cpp.is_file() or not cmake.is_file():
        raise RuntimeError("Unexpected melonDS Switch source tree")

    text = main_cpp.read_text(encoding="utf-8")

    if '#include "PokebotBridge.h"' not in text:
        text = replace_once(
            text,
            '#include "InputConfig.h"\n',
            '#include "InputConfig.h"\n#include "PokebotBridge.h"\n',
            "include hook",
        )

    if "PokebotBridge::Init();" not in text:
        text = replace_once(
            text,
            '    hidStartSixAxisSensor(FullKeySixAxisHandle);\n}\n\nvoid DeInit()\n',
            '    hidStartSixAxisSensor(FullKeySixAxisHandle);\n\n'
            '    PokebotBridge::Init();\n'
            '}\n\nvoid DeInit()\n',
            "init hook",
        )

    if "PokebotBridge::DeInit();" not in text:
        text = replace_once(
            text,
            '    GPU::DeInitRenderer();\n    NDS::DeInit();\n',
            '    PokebotBridge::DeInit();\n\n'
            '    GPU::DeInitRenderer();\n    NDS::DeInit();\n',
            "deinit hook",
        )

    if "PokebotBridge::ApplyFrame(keyMask);" not in text:
        text = replace_once(
            text,
            '            NDS::SetKeyMask(keyMask);\n',
            '            PokebotBridge::ApplyFrame(keyMask);\n'
            '            NDS::SetKeyMask(keyMask);\n',
            "frame hook",
        )

    main_cpp.write_text(text, encoding="utf-8")

    cmake_text = cmake.read_text(encoding="utf-8")
    if "PokebotBridge.cpp" not in cmake_text:
        cmake_text = replace_once(
            cmake_text,
            'SET(SOURCES_SWITCH\n    main.cpp\n',
            'SET(SOURCES_SWITCH\n    main.cpp\n    PokebotBridge.cpp\n',
            "CMake source hook",
        )
        cmake.write_text(cmake_text, encoding="utf-8")

    print("PASS: Pokebot-nds melonDS bridge v0p1 applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
