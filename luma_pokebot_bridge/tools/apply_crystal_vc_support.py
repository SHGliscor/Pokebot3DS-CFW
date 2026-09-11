#!/usr/bin/env python3
"""Add read-only Pokémon Crystal (English VC) support to the Pokebot RAM bridge.

This patch intentionally does not add any process-memory write primitive. It only
allows the existing QUERY/READ bridge to open the official English Crystal VC
process so PC-side tools can read the VC emulator's mirrored Game Boy WRAM.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Luma3DS"
SOURCE = ROOT / "sysmodules" / "rosalina" / "source" / "pokebot_ram_bridge.c"

CRYSTAL_DEFINE = "#define POKEBOT_CRYSTAL_EN_TID 0x0004000000172800ULL"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> int:
    if not SOURCE.is_file():
        raise FileNotFoundError(
            f"{SOURCE} does not exist. Run apply_ram_bridge.py before this patch."
        )

    text = SOURCE.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "#define POKEBOT_AS_TID 0x000400000011C500ULL",
        "#define POKEBOT_AS_TID 0x000400000011C500ULL\n" + CRYSTAL_DEFINE,
        "Crystal title define",
    )

    text = replace_once(
        text,
        "return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID;",
        "return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID ||\n"
        "           tid == POKEBOT_CRYSTAL_EN_TID;",
        "supported-title predicate",
    )

    text = replace_once(
        text,
        '    if (tid == POKEBOT_AS_TID)\n        return "sango-2";\n    return "unknown";',
        '    if (tid == POKEBOT_AS_TID)\n        return "sango-2";\n'
        '    if (tid == POKEBOT_CRYSTAL_EN_TID)\n        return "crystal";\n'
        '    return "unknown";',
        "Crystal process label",
    )

    SOURCE.write_text(text, encoding="utf-8")

    # Fail closed if the generated bridge unexpectedly gains a RAM write path.
    verify = SOURCE.read_text(encoding="utf-8")
    required = (
        CRYSTAL_DEFINE,
        "tid == POKEBOT_CRYSTAL_EN_TID",
        'return "crystal";',
        "POKEBOT_CMD_READ      = 4",
    )
    for needle in required:
        if needle not in verify:
            raise RuntimeError(f"verification failed: missing {needle!r}")

    forbidden = ("svcWriteProcessMemory", "Pokebot_WriteTarget", "POKEBOT_CMD_WRITE")
    for needle in forbidden:
        if needle in verify:
            raise RuntimeError(f"safety verification failed: found {needle!r}")

    print("Applied English Pokémon Crystal VC read-only target support.")
    print("Title ID: 0004000000172800")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
