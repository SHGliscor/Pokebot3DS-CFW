from __future__ import annotations

from pathlib import Path
import py_compile
import shutil
import sys

TARGET = Path('pokebot/common/luma_input.py')
BACKUP = TARGET.with_suffix('.py.v0p42Z-backup')

OLD = """        interval = max(0.010, min(0.100, float(poll_ms) / 1000.0))
        samples = []
        while time.monotonic() < deadline:
            # Avoid polling faster than needed while still giving the bridge
            # regular service opportunities for hold->settle->terminal state.
            remaining_ms = int(current.get('remaining_ms', 0) or 0)
            if remaining_ms > 80:
                time.sleep(min(0.050, max(interval, (remaining_ms - 40) / 1000.0)))
            else:
                time.sleep(interval)
            current = self._status(sequence)
            samples.append({
                'state': current['state'],
                'state_name': current['state_name'],
                'remaining_ms': current['remaining_ms'],
                'raw_hid': current['raw_hid'],
            })
"""

NEW = """        interval = max(0.010, min(0.100, float(poll_ms) / 1000.0))
        samples = []
        status_timeouts = 0
        max_status_timeouts = 2
        while time.monotonic() < deadline:
            # Avoid polling faster than needed while still giving the bridge
            # regular service opportunities for hold->settle->terminal state.
            remaining_ms = int(current.get('remaining_ms', 0) or 0)
            if remaining_ms > 80:
                time.sleep(min(0.050, max(interval, (remaining_ms - 40) / 1000.0)))
            else:
                time.sleep(interval)

            try:
                # INPUT_STATUS is read-only. If one status reply is lost after
                # the gameplay command was already ACKed, keep querying this
                # same gameplay sequence; never replay the button/touch command.
                current = self._status(sequence)
            except LumaInputError as exc:
                if 'timeout' not in str(exc).lower():
                    raise
                status_timeouts += 1
                samples.append({
                    'event': 'STATUS_TIMEOUT',
                    'sequence': int(sequence),
                    'timeout_count': status_timeouts,
                })
                if status_timeouts > max_status_timeouts:
                    break
                # A lost read-only status packet must not turn a completed
                # gameplay input into a false HOLD. Extend only by one bounded
                # transport timeout per miss, capped by max_status_timeouts.
                deadline += min(self.timeout, 1.0)
                continue

            samples.append({
                'state': current['state'],
                'state_name': current['state_name'],
                'remaining_ms': current['remaining_ms'],
                'raw_hid': current['raw_hid'],
            })
"""


def main() -> int:
    if not TARGET.is_file():
        print(f'ERROR: {TARGET} not found.')
        print('Run this from the root of your Pokebot3DS-CFW v0p42Z folder.')
        return 2

    text = TARGET.read_text(encoding='utf-8')
    if NEW in text:
        print('Hotfix is already applied.')
        return 0
    if text.count(OLD) != 1:
        print('ERROR: exact v0p42Z transport block was not found uniquely.')
        print('No files were changed.')
        return 3

    shutil.copy2(TARGET, BACKUP)
    TARGET.write_text(text.replace(OLD, NEW, 1), encoding='utf-8')
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        shutil.copy2(BACKUP, TARGET)
        print(f'ERROR: patched file failed syntax validation: {exc}')
        print('Original file restored.')
        return 4

    print('PASS: v0p42Z input-status recovery hotfix applied.')
    print(f'Backup: {BACKUP}')
    print('Starter timing, starter RAM/shiny authority and Random selection were not changed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
