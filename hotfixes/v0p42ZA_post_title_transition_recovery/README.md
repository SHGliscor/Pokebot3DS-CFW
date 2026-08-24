# v0p42ZA post-title transition recovery

Three Random-starter support exports from 2026-08-24 showed the same false safety HOLD: `RESET_UNKNOWN_BUDGET_EXHAUSTED` after positive title detection and after two title inputs. Successful cycles in those runs normally reached `continue_menu` after the third title input.

The failure is therefore scoped to the reset route: pre-title `unknown` observations can consume the shared unknown budget, leaving no allowance for the legitimate blank/transitional state between `DllTitle` and `DllStartMenu`.

## Fix scope

- Patch only `reset_route.py`.
- Add three bounded post-title unknown probes after `title_inputs > 0`.
- Send no gameplay input while state is `unknown`.
- Reuse the existing unknown-state settle/probe path.
- Preserve the original `RESET_UNKNOWN_BUDGET_EXHAUSTED` safety HOLD after the bounded allowance is exhausted.
- Do not increase the pre-title/global unknown allowance.
- Do not modify Treecko, Torchic or Mudkip modules.
- Do not modify PK6 validation, shiny authority, battle gates, Random selection, starter timing, `boot.firm`, or `code.ips`.

## Patcher safety

`apply_hotfix.py` refuses to edit unless it finds exactly one `reset_route.py` containing both `RESET_ROUTE_STATE` and `RESET_UNKNOWN_BUDGET_EXHAUSTED`. It requires a unique `title_inputs = 0` initialization and a unique `kind == "unknown"` block containing the HOLD, identifies the existing unknown-budget variable structurally, parses Python before and after, creates a backup, and compares starter module hashes before/after. Structural ambiguity aborts without an unsafe fallback.

The patcher can operate on either an unpacked bot folder or a current Pokebot3DS-CFW ZIP. ZIP mode emits `Pokebot3DS-CFW_v0p42ZA_PostTitleTransitionRecovery.zip` without altering the input archive.

Hardware validation remains required after applying the patch.