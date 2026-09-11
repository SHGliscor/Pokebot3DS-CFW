# v0p42Z Input Status Recovery Hotfix

This is a narrow PC-side transport hotfix for the rare false safety HOLD caused by a lost `INPUT_STATUS` UDP reply after a gameplay command has already been acknowledged by Pokebot-Luma.

## What changes

- `pokebot/common/luma_input.py` only.
- After the original gameplay command is ACKed, a transient timeout while querying `INPUT_STATUS` is tolerated up to **two times**.
- Recovery continues querying the **same gameplay sequence ID**.
- The A/button/touch gameplay command is **never replayed** by this recovery path.
- Each tolerated miss is recorded in the terminal samples as `STATUS_TIMEOUT`.
- A third timeout, or any non-timeout controller error, retains fail-closed behaviour and reaches the existing `RELEASE_ALL` / safety failure path.

## What does NOT change

- Treecko, Torchic or Mudkip starter modules.
- Starter selection or confirmation timings.
- Random starter shuffled-bag selection.
- Soft-reset choreography.
- PK6 reads, validation or shiny authority.
- Wild movement/touch timings.
- `boot.firm` or `code.ips`.

## Apply to an existing v0p42Z folder

The easiest user package contains `APPLY_HOTFIX.bat` and `apply_hotfix.py` at the bot root. Double-click `APPLY_HOTFIX.bat`.

From a repository checkout containing this hotfix folder, run:

```text
python hotfixes\v0p42Z_input_status_recovery\apply_hotfix.py
```

The patcher:

1. Requires the exact v0p42Z `_wait_terminal()` block.
2. Refuses a broad/ambiguous replacement.
3. Backs up the original file to `pokebot/common/luma_input.py.v0p42Z-backup`.
4. Applies only the bounded status-recovery block.
5. Compiles the patched Python file to validate syntax.
6. Restores the original automatically if validation fails.

This hotfix is a response to a rare long-run transport-status timeout. Hardware soak validation is still required before calling the change fully hardware proven.
