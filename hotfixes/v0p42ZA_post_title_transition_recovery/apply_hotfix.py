from __future__ import annotations

import ast
import hashlib
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

PATCH_MARKER = "POKEBOT_POST_TITLE_UNKNOWN_GRACE_V1"
TARGET_ERROR = "RESET_UNKNOWN_BUDGET_EXHAUSTED"
TARGET_EVENT = "RESET_ROUTE_STATE"
OUTPUT_ZIP_NAME = "Pokebot3DS-CFW_v0p42ZA_PostTitleTransitionRecovery.zip"
GRACE_PROBES = 3

LOCKED_STARTER_SHA256 = {
    "treecko.py": "f0a412924442c667fd6f3280a5b759290cdfff2b9ede176698f2c4e3304c95a5",
    "torchic.py": "f3a50bc7c644dcb5dd7f4d5f12e9f64b038a0f05514cf4ce896f748f530bfb6d",
    "mudkip.py": "d2f8d78e9900743cc319be48eda7f4d2572814a33f12b7d82cbd7cebd7bd01ef",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def python_ok(text: str, filename: str) -> None:
    ast.parse(text, filename=filename)


def leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def block_end(lines: list[str], start: int, indent: int) -> int:
    i = start + 1
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped and not stripped.startswith("#") and leading_spaces(lines[i]) <= indent:
            return i
        i += 1
    return len(lines)


def find_target(root: Path) -> Path:
    candidates = []
    for p in root.rglob("reset_route.py"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if TARGET_ERROR in text and TARGET_EVENT in text:
            candidates.append(p)
    if len(candidates) != 1:
        raise RuntimeError(
            f"expected exactly one reset_route.py with {TARGET_ERROR}; found {len(candidates)}"
        )
    return candidates[0]


def find_starters(root: Path) -> dict[str, Path]:
    out = {}
    for name in LOCKED_STARTER_SHA256:
        matches = [p for p in root.rglob(name) if p.parent.name == "starters"]
        if len(matches) == 1:
            out[name] = matches[0]
    return out


def starter_hashes(root: Path) -> dict[str, str]:
    return {name: sha256(path) for name, path in find_starters(root).items()}


def verify_locked_starters(root: Path, before: dict[str, str] | None = None) -> None:
    current = starter_hashes(root)
    if before is not None and current != before:
        raise RuntimeError("starter module hashes changed while applying reset-route hotfix")
    for name, digest in current.items():
        expected = LOCKED_STARTER_SHA256[name]
        status = "LOCKED_MATCH" if digest == expected else "PREEXISTING_DIFFERENT_HASH"
        print(f"STARTER {name}: {status} {digest}")


def identify_unknown_block(lines: list[str]) -> tuple[int, int, int]:
    error_lines = [i for i, line in enumerate(lines) if TARGET_ERROR in line]
    if len(error_lines) != 1:
        raise RuntimeError(f"expected one {TARGET_ERROR} literal, found {len(error_lines)}")
    err = error_lines[0]

    candidates = []
    for i in range(err - 1, -1, -1):
        s = lines[i].strip()
        if not re.match(r"^(?:if|elif)\s+kind\s*==\s*['\"]unknown['\"]\s*:\s*$", s):
            continue
        indent = leading_spaces(lines[i])
        end = block_end(lines, i, indent)
        if i < err < end:
            candidates.append((i, end, indent))
            break
    if len(candidates) != 1:
        raise RuntimeError("could not uniquely locate kind == 'unknown' block containing the hold")
    return candidates[0]


def identify_budget_var(block_lines: list[str]) -> str:
    joined = "\n".join(block_lines)
    names: dict[str, int] = {}

    patterns = [
        r"\b([A-Za-z_]\w*(?:unknown|Unknown)\w*)\s*-=?=\s*\d+",
        r"\b([A-Za-z_]\w*(?:unknown|Unknown)\w*)\s*(?:<=|<|==|>=|>)\s*\d+",
        r"\b([A-Za-z_]\w*(?:budget|Budget)\w*)\s*-=?=\s*\d+",
        r"\b([A-Za-z_]\w*(?:budget|Budget)\w*)\s*(?:<=|<|==|>=|>)\s*\d+",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, joined):
            name = m.group(1)
            if name in {"title_inputs", "post_title_unknown_grace"}:
                continue
            names[name] = names.get(name, 0) + 1

    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*-=\s*1\b", joined):
        name = m.group(1)
        if "unknown" in name.lower() or "budget" in name.lower():
            names[name] = names.get(name, 0) + 2

    if not names:
        raise RuntimeError("could not identify the existing unknown-state budget variable")
    ranked = sorted(names.items(), key=lambda kv: (-kv[1], kv[0]))
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        raise RuntimeError(f"ambiguous unknown budget variables: {[x[0] for x in ranked[:3]]}")
    return ranked[0][0]


def identify_budget_floor(block_lines: list[str], budget: str) -> int:
    dec = []
    checks = []
    for i, line in enumerate(block_lines):
        if re.search(rf"\b{re.escape(budget)}\s*-=\s*1\b", line):
            dec.append(i)
        if re.search(rf"\b{re.escape(budget)}\b\s*(?:<=|<|==|>=|>)\s*\d+", line):
            checks.append(i)
        elif re.search(rf"\d+\s*(?:<=|<|==|>=|>)\s*\b{re.escape(budget)}\b", line):
            checks.append(i)
    if not dec or not checks:
        raise RuntimeError(f"could not determine decrement/check order for `{budget}`")
    first_dec = min(dec)
    first_check = min(checks)
    if first_dec == first_check:
        raise RuntimeError(f"ambiguous decrement/check order for `{budget}`")
    return 2 if first_dec < first_check else 1


def patch_text(text: str, filename: str = "reset_route.py") -> str:
    if PATCH_MARKER in text:
        print("Hotfix marker already present; no source change needed.")
        return text

    python_ok(text, filename)
    lines = text.splitlines(keepends=True)

    title_init = [
        i for i, line in enumerate(lines)
        if re.match(r"^\s*title_inputs\s*=\s*0\s*(?:#.*)?(?:\r?\n)?$", line)
    ]
    if len(title_init) != 1:
        raise RuntimeError(f"expected one `title_inputs = 0` initialization, found {len(title_init)}")

    u_start, u_end, u_indent = identify_unknown_block(lines)
    budget = identify_budget_var(lines[u_start:u_end])
    budget_floor = identify_budget_floor(lines[u_start:u_end], budget)

    init_re = re.compile(rf"^\s*{re.escape(budget)}\s*=\s*.+$")
    budget_inits = [i for i in range(0, u_start) if init_re.match(lines[i].rstrip("\r\n"))]
    if not budget_inits:
        raise RuntimeError(f"identified `{budget}` but could not find its initialization before unknown block")

    ti = title_init[0]
    init_indent = " " * leading_spaces(lines[ti])
    init_insert = (
        f"{init_indent}post_title_unknown_grace = {GRACE_PROBES}  # {PATCH_MARKER}\n"
    )
    lines.insert(ti + 1, init_insert)

    if ti + 1 <= u_start:
        u_start += 1
        u_end += 1

    body_indent = " " * (u_indent + 4)
    grace = [
        f"{body_indent}# {PATCH_MARKER}: pre-title unknowns must not consume the bounded\n",
        f"{body_indent}# transition allowance after positive title authority. No input is\n",
        f"{body_indent}# sent here; the existing unknown-state settle/probe path still runs.\n",
        f"{body_indent}if title_inputs > 0 and post_title_unknown_grace > 0:\n",
        f"{body_indent}    post_title_unknown_grace -= 1\n",
        f"{body_indent}    {budget} = max({budget}, {budget_floor})\n",
    ]
    lines[u_start + 1:u_start + 1] = grace

    patched = "".join(lines)
    python_ok(patched, filename)

    if patched.count(PATCH_MARKER) < 2:
        raise RuntimeError("hotfix marker postcondition failed")
    if TARGET_ERROR not in patched:
        raise RuntimeError("original safety HOLD literal disappeared unexpectedly")
    if patched.count("post_title_unknown_grace") < 3:
        raise RuntimeError("post-title grace postcondition failed")
    return patched


def patch_tree(root: Path) -> Path:
    target = find_target(root)
    print(f"Target: {target}")
    before_starters = starter_hashes(root)
    original = target.read_text(encoding="utf-8")
    patched = patch_text(original, str(target))

    if patched == original:
        verify_locked_starters(root, before_starters)
        return target

    backup = target.with_suffix(target.suffix + ".v0p42ZA-pre-post-title-recovery.bak")
    if not backup.exists():
        shutil.copy2(target, backup)
    target.write_text(patched, encoding="utf-8")

    try:
        python_ok(target.read_text(encoding="utf-8"), str(target))
        verify_locked_starters(root, before_starters)
    except Exception:
        shutil.copy2(backup, target)
        raise

    print("PASS: post-title transition recovery applied.")
    print(f"Backup: {backup}")
    print("Scope: pokebot/common reset route only; starter choreography and shiny authority untouched.")
    return target


def common_top_level(names: list[str]) -> str | None:
    tops = {Path(n).parts[0] for n in names if n and not n.startswith("__MACOSX/")}
    return next(iter(tops)) if len(tops) == 1 else None


def patch_zip(zip_path: Path) -> Path:
    zip_path = zip_path.resolve()
    if not zip_path.is_file():
        raise RuntimeError(f"ZIP not found: {zip_path}")
    with tempfile.TemporaryDirectory(prefix="pokebot_post_title_") as td:
        work = Path(td)
        with zipfile.ZipFile(zip_path, "r") as zf:
            bad = zf.testzip()
            if bad:
                raise RuntimeError(f"input ZIP CRC failure at {bad}")
            names = zf.namelist()
            zf.extractall(work)
        top = common_top_level(names)
        root = work / top if top and (work / top).is_dir() else work
        patch_tree(root)

        output = zip_path.with_name(OUTPUT_ZIP_NAME)
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as out:
            base = work
            for p in sorted(work.rglob("*")):
                if p.is_file():
                    out.write(p, p.relative_to(base))
        with zipfile.ZipFile(output, "r") as verify:
            bad = verify.testzip()
            if bad:
                raise RuntimeError(f"output ZIP CRC failure at {bad}")
        print(f"OUTPUT: {output}")
        print(f"SHA256: {sha256(output)}")
        return output


def auto_input_zip(script_dir: Path) -> Path | None:
    candidates = [
        p for p in script_dir.glob("Pokebot3DS-CFW*.zip")
        if p.name != OUTPUT_ZIP_NAME and "Hotfix" not in p.name
    ]
    return candidates[0] if len(candidates) == 1 else None


def main() -> int:
    try:
        if len(sys.argv) > 2:
            print("Usage: apply_hotfix.py [current Pokebot3DS-CFW ZIP or unpacked folder]")
            return 2

        if len(sys.argv) == 2:
            target = Path(sys.argv[1]).expanduser()
        else:
            script_dir = Path(__file__).resolve().parent
            found = auto_input_zip(script_dir)
            if found is not None:
                target = found
            else:
                target = Path.cwd()

        if target.is_file() and target.suffix.lower() == ".zip":
            patch_zip(target)
        elif target.is_dir():
            patch_tree(target.resolve())
        else:
            raise RuntimeError("target must be an unpacked Pokebot3DS-CFW folder or ZIP")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        print("No unsafe fallback was attempted. If a backup was created, the original source was restored on validation failure.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
