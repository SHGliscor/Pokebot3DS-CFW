"""Compile and execute the actual generated C title gate and process-name function.

Removing Ultra Sun acceptance, accepting update/unknown titles, or breaking any
existing accepted game must fail this test. Requires a host C compiler, not a 3DS.
"""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def function(source, name):
    match = re.search(r'static [^\n]+\b' + re.escape(name) + r'\([^\n]*\)\s*\{', source)
    if not match:
        raise ValueError('Function not found: ' + name)
    start, pos, depth = match.start(), match.end(), 1
    while depth and pos < len(source):
        depth += (source[pos] == '{') - (source[pos] == '}')
        pos += 1
    if depth:
        raise ValueError('Unclosed function: ' + name)
    return source[start:pos]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=Path)
    args = parser.parse_args()
    source = args.source.read_text()
    defines = '\n'.join(re.findall(r'^#define POKEBOT_\w+_TID[^\n]+', source, re.M))
    code = '''#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint64_t u64;
''' + defines + '\n' + function(source, 'Pokebot_IsSupportedTitle') + '\n' + function(source, 'Pokebot_ProcessName') + r'''
int main(void) {
    struct {u64 id; const char *name;} games[] = {
        {0x0004000000055D00ULL, "kujira-1"},
        {0x0004000000055E00ULL, "kujira-2"},
        {0x000400000011C400ULL, "sango-1"},
        {0x000400000011C500ULL, "sango-2"},
        {0x00040000001B5000ULL, "momiji"}
    };
    int failed = 0;
    for (unsigned i = 0; i < sizeof(games)/sizeof(games[0]); i++) {
        if (!Pokebot_IsSupportedTitle(games[i].id) ||
            strcmp(Pokebot_ProcessName(games[i].id), games[i].name)) {
            fprintf(stderr, "FAIL: title %016llX not accepted with expected name %s\n",
                (unsigned long long)games[i].id, games[i].name);
            failed++;
        }
    }
    u64 rejected[] = {0, 0x0004000E001B5000ULL, 0x00040000001B5100ULL,
                      0x0004000000164800ULL, 0xFFFFFFFFFFFFFFFFULL};
    for (unsigned i = 0; i < sizeof(rejected)/sizeof(rejected[0]); i++) {
        if (Pokebot_IsSupportedTitle(rejected[i])) {
            fprintf(stderr, "FAIL: unexpected title accepted\n");
            failed++;
        }
    }
    if (!failed) puts("PASS: X/Y/ORAS/Ultra Sun accepted with correct names; other tested titles rejected");
    return failed ? 1 : 0;
}
'''
    with tempfile.TemporaryDirectory() as temp:
        path = Path(temp)
        (path/'title_gate.c').write_text(code)
        subprocess.run(['cc', '-std=c99', '-Wall', '-Wextra', '-Werror', str(path/'title_gate.c'), '-o', str(path/'title_gate')], check=True)
        return subprocess.run([str(path/'title_gate')]).returncode


if __name__ == '__main__':
    raise SystemExit(main())
