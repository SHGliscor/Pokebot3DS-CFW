"""Add only the supplied Ultra Sun title to the existing HF105B title gate."""
import argparse
from pathlib import Path


def replace_once(text, old, new, label):
    if text.count(old) != 1:
        raise SystemExit('Unexpected source: ' + label + ' must occur exactly once')
    return text.replace(old, new, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2] / 'Luma3DS')
    args = parser.parse_args()
    source = args.root / 'sysmodules/rosalina/source'
    bridge = source / 'pokebot_ram_bridge.c'
    menu = source / 'menus.c'
    text = bridge.read_text()
    text = replace_once(text,
        '#define POKEBOT_AS_TID 0x000400000011C500ULL',
        '#define POKEBOT_AS_TID 0x000400000011C500ULL\n#define POKEBOT_US_TID 0x00040000001B5000ULL',
        'Ultra Sun title constant')
    text = replace_once(text,
        'tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID;',
        'tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID || tid == POKEBOT_US_TID;',
        'existing title gate')
    text = replace_once(text,
        '    if (tid == POKEBOT_AS_TID)\n        return "sango-2";\n    return "unknown";',
        '    if (tid == POKEBOT_AS_TID)\n        return "sango-2";\n    if (tid == POKEBOT_US_TID)\n        return "momiji";\n    return "unknown";',
        'process name mapping')
    text = replace_once(text, '"Pokebot3DS-Luma-v0p7-n3ds-fb1-cpad"',
        '"Pokebot3DS-Luma-v0p7-n3ds-fb1-cpad-us1"', 'bridge version label')
    menus = replace_once(menu.read_text(), 'Pokebot-Luma v0p7-n3ds-fb1-cpad',
        'Pokebot-Luma v0p7-n3ds-fb1-cpad-us1', 'menu version label')
    # Validate both files before either is changed; refuse unknown source lineage.
    bridge.write_text(text)
    menu.write_text(menus)
    print('Ultra Sun 00040000001B5000 / momiji added; existing title gate retained.')


if __name__ == '__main__':
    main()
