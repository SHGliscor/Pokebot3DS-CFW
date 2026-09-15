#!/usr/bin/env python3
from pathlib import Path
import sys

def replace_once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected exactly one marker, found {count}")
    return text.replace(old, new, 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: mgba_fastoverride_patch.py <path-to-src/platform/3ds/main.c>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    if "pb3FastOverride" in text:
        print("Fast override patch already applied")
        return

    text = replace_once(
        text,
        "static u64 pb3RemoteKeysUntil = 0;\n",
        "static u64 pb3RemoteKeysUntil = 0;\nstatic bool pb3FastOverride = false;\n",
        "fast override state",
    )

    text = replace_once(
        text,
        '''\tif (!strncmp(cmd, "FAST ", 5)) {
\t\tint on = atoi(cmd + 5) ? 1 : 0;
\t\tframeLimiter = !on;
\t\t_pb3Send(&peer, peerLen, on ? "PB3 OK FAST 1" : "PB3 OK FAST 0");
\t\treturn;
\t}
''',
        '''\tif (!strncmp(cmd, "FAST ", 5)) {
\t\tint on = atoi(cmd + 5) ? 1 : 0;
\t\tpb3FastOverride = on ? true : false;
\t\tframeLimiter = on ? false : true;
\t\t_pb3Send(&peer, peerLen, on ? "PB3 OK FAST 1" : "PB3 OK FAST 0");
\t\treturn;
\t}
''',
        "FAST command",
    )

    text = replace_once(
        text,
        '''static void _setFrameLimiter(struct mGUIRunner* runner, bool limit) {
\tUNUSED(runner);
\tif (frameLimiter == limit) {
''',
        '''static void _setFrameLimiter(struct mGUIRunner* runner, bool limit) {
\tUNUSED(runner);
\tif (pb3FastOverride) {
\t\tlimit = false;
\t}
\tif (frameLimiter == limit) {
''',
        "frame limiter override",
    )

    path.write_text(text, encoding="utf-8")
    print(f"Applied persistent Pokebot3DS-CFW mGBA fast-forward override patch to {path}")

if __name__ == "__main__":
    main()
