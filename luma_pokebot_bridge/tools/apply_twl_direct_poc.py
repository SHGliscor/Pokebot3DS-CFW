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
static bool writePokebotThumbBl(u16 *at, const u8 *target)
{
    u32 branchBase = (u32)at;
    u32 jumpOffset = (u32)target - (branchBase + 4);

    if(((u32)target & 1U) != 0)
        return false;

    /* Same Thumb BL encoding used by the established TwlBg RTCom patch. */
    at[0] = 0xF000 | ((jumpOffset >> 12) & 0x7FF);
    at[1] = 0xF800 | ((jumpOffset >> 1) & 0x7FF);
    return true;
}
'''

    marker = 'void patchTwlBg(u8 *pos, u32 size)\n{'
    if marker not in text:
        raise RuntimeError("patchTwlBg anchor missing")
    text = text.replace(
        marker,
        helpers + 'void patchTwlBg(u8 *pos, u32 size, u32 textSize)\n{',
        1,
    )

    insertion = r'''
    /*
     * Direct-TWL PoC v0p2.
     *
     * hidUpdatePattern is the established TwlBg HID-update signature.
     * pxiLogPattern is the established unused function area used by the
     * existing ARM11 TwlBg/RTCom patch.  Using it removes the speculative
     * zero-filled code-cave used by v0p1.
     */
    static const u8 hidUpdatePattern[] = {
        0x01, 0x0E, 0x08, 0x43, 0xB0, 0x43, 0x34, 0x40,
        0x20, 0x43, 0x84, 0xB2, 0xF0, 0x20, 0x06, 0x43
    };
    static const u8 pxiLogPattern[] = {
        0xF3, 0xB5, 0x04, 0x1E, 0xAD, 0xB0, 0x3C, 0xDA
    };

    if(textSize == 0 || textSize > size)
        return;

    u8 *hidHook = memsearch(pos, hidUpdatePattern, textSize, sizeof(hidUpdatePattern));
    u8 *payloadDst = memsearch(pos, pxiLogPattern, textSize, sizeof(pxiLogPattern));

    if(hidHook == NULL || payloadDst == NULL)
        return;

    u16 *hook = (u16 *)hidHook;
    if(hook[0] != 0x0E01 || hook[1] != 0x4308)
        return;

    if((u32)(payloadDst - pos) + POKEBOT_TWL_HOOK_BIN_SIZE > textSize)
        return;

    /*
     * PXI log is not used once TwlBg reaches the point where the established
     * RTCom payload is installed.  This is the same storage strategy, but our
     * code is present before TwlBg starts, so no runtime cache flush is needed.
     */
    memcpy(payloadDst, pokebot_twl_hook_bin, POKEBOT_TWL_HOOK_BIN_SIZE);

    if(!writePokebotThumbBl(hook, payloadDst))
    {
        /* Fail closed: restore the known PXI-log signature prefix. */
        memcpy(payloadDst, pxiLogPattern, sizeof(pxiLogPattern));
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

    hook = args.hook_bin.read_bytes()
    if not hook or len(hook) > 0x180:
        raise RuntimeError(f"unexpected hook size: {len(hook)}")

    if not LUMA.is_dir():
        raise RuntimeError("missing Luma3DS checkout")

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
        'void patchTwlBg(u8 *pos, u32 size, u32 textSize); // Pokebot direct-TWL v0p2\n',
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

    print(f"Pokebot direct-TWL v0p2 applied; payload={len(hook)} bytes")


if __name__ == "__main__":
    main()
