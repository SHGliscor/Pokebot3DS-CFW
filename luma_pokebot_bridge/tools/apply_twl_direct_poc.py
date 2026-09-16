#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LUMA = ROOT / "Luma3DS"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def make_header(data: bytes) -> str:
    if not data:
        raise RuntimeError("TWL hook binary is empty")
    rows = []
    for i in range(0, len(data), 12):
        rows.append("    " + ", ".join(f"0x{x:02X}" for x in data[i:i + 12]) + ",")
    return """#pragma once

#include "types.h"

static const u8 pokebot_twl_hook_bin[] = {
%s
};

#define POKEBOT_TWL_HOOK_BIN_SIZE ((u32)sizeof(pokebot_twl_hook_bin))
""" % "\n".join(rows)


def patch_patches_c(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        '#include "large_patches.h"\n',
        '#include "large_patches.h"\n#include "pokebot_twl_hook_bin.h"\n',
        1,
    )

    helpers = r'''
static u8 *findPokebotTwlCodeCave(u8 *pos, u32 textSize, u32 need)
{
    if(need == 0 || textSize <= need + 0x1000)
        return NULL;

    /*
     * Limit the search to the tail of executable .text. This is deliberately
     * conservative: we only use a naturally zero-filled cave near the end of
     * text rather than overwriting a live TwlBg function.
     */
    u32 lower = textSize > 0x2000 ? textSize - 0x2000 : 0x1000;
    u32 off = (textSize - need) & ~3U;

    while(off >= lower)
    {
        u32 j = 0;
        while(j < need && pos[off + j] == 0)
            j++;

        if(j == need)
            return pos + off;

        if(off < lower + 4)
            break;
        off -= 4;
    }

    return NULL;
}

static bool writePokebotThumbBl(u16 *at, const u8 *target)
{
    s32 rel = (s32)(target - ((u8 *)at + 4));

    if((rel & 1) != 0 || rel < -0x400000 || rel > 0x3FFFFE)
        return false;

    u32 jump = (u32)rel;
    at[0] = 0xF000 | ((jump >> 12) & 0x7FF);
    at[1] = 0xF800 | ((jump >> 1) & 0x7FF);
    return true;
}
'''
    marker = 'void patchTwlBg(u8 *pos, u32 size)\n{'
    if marker not in text:
        raise RuntimeError("patchTwlBg signature anchor missing")
    text = text.replace(
        marker,
        helpers + 'void patchTwlBg(u8 *pos, u32 size, u32 textSize)\n{',
        1,
    )

    insertion = r'''
    /*
     * Pokebot TWL direct-input PoC v0p1.
     * Signature comes from the TwlBg HID update routine already used by the
     * established New-3DS TwlBg/RTCom patching work.
     */
    static const u8 hidUpdatePattern[] = {
        0x01, 0x0E, 0x08, 0x43, 0xB0, 0x43, 0x34, 0x40,
        0x20, 0x43, 0x84, 0xB2, 0xF0, 0x20, 0x06, 0x43
    };

    if(textSize == 0 || textSize > size)
        return;

    u8 *hidHook = memsearch(pos, hidUpdatePattern, textSize, sizeof(hidUpdatePattern));
    if(hidHook == NULL)
        return;

    u16 *hook = (u16 *)hidHook;
    if(hook[0] != 0x0E01 || hook[1] != 0x4308)
        return;

    u8 *cave = findPokebotTwlCodeCave(pos, textSize, POKEBOT_TWL_HOOK_BIN_SIZE);
    if(cave == NULL)
        return;

    memcpy(cave, pokebot_twl_hook_bin, POKEBOT_TWL_HOOK_BIN_SIZE);

    if(!writePokebotThumbBl(hook, cave))
    {
        memset(cave, 0, POKEBOT_TWL_HOOK_BIN_SIZE);
        return;
    }
'''
    end_marker = '\n}\n\nu32 patchLgyK11('
    idx = text.find(end_marker, text.find('void patchTwlBg('))
    if idx < 0:
        raise RuntimeError("patchTwlBg end anchor missing")
    text = text[:idx] + "\n" + insertion + text[idx:]
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hook-bin", required=True, type=Path)
    args = ap.parse_args()

    if not LUMA.is_dir():
        raise RuntimeError(f"missing Luma checkout: {LUMA}")

    hook = args.hook_bin.read_bytes()
    if not hook or len(hook) > 0x180:
        raise RuntimeError(f"unexpected TWL hook size: {len(hook)} bytes")

    (LUMA / "arm9/source/pokebot_twl_hook_bin.h").write_text(
        make_header(hook), encoding="utf-8"
    )

    patches_c = LUMA / "arm9/source/patches.c"
    patches_h = LUMA / "arm9/source/patches.h"
    firm_c = LUMA / "arm9/source/firm.c"

    patch_patches_c(patches_c)

    replace_once(
        patches_h,
        'void patchTwlBg(u8 *pos, u32 size); // silently fails\n',
        'void patchTwlBg(u8 *pos, u32 size, u32 textSize); // Pokebot direct-TWL PoC\n',
    )

    replace_once(
        firm_c,
        '''typedef struct CopyKipResult {
    u32 cxiSize;
    u8 *codeDstAddr;
    u32 codeSize;
} CopyKipResult;
''',
        '''typedef struct CopyKipResult {
    u32 cxiSize;
    u8 *codeDstAddr;
    u32 codeSize;
    u32 textSize;
} CopyKipResult;
''',
    )

    replace_once(
        firm_c,
        '''    u8 *codeAddr = (u8 *)exefs + sizeof(ExeFsHeader) + fh->offset;

    if (memcmp(fh->name, ".code\\0\\0\\0", 8) != 0 || fh->offset != 0 || exefs->fileHeaders[1].size != 0)
''',
        '''    u8 *codeAddr = (u8 *)exefs + sizeof(ExeFsHeader) + fh->offset;
    res.textSize = exh->systemControlInfo.textCodeSet.size;

    if (memcmp(fh->name, ".code\\0\\0\\0", 8) != 0 || fh->offset != 0 || exefs->fileHeaders[1].size != 0)
''',
    )

    replace_once(
        firm_c,
        '            patchTwlBg(copyRes.codeDstAddr, copyRes.codeSize);\n',
        '            patchTwlBg(copyRes.codeDstAddr, copyRes.codeSize, copyRes.textSize);\n',
    )

    print(f"Pokebot direct-TWL PoC applied; ARM11 payload={len(hook)} bytes")


if __name__ == "__main__":
    main()
