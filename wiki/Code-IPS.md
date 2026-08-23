# ORAS `code.ips`

Pokebot3DS-CFW includes separate update-1.4 `code.ips` patches for Pokémon Omega Ruby and Pokémon Alpha Sapphire.

## Why the patch is needed

ORAS can display a **communication error** when remote/InputRedirection-style controller input is used while the game's PSS communication is still active.

Later in the game, the player can normally avoid this by opening the **PSS** and disabling PSS communication. That option is not available during the early Route 101 starter sequence because the player has **not unlocked access to the PSS yet**.

That creates a problem for starter automation: the bot needs remote controller input before the game gives the player a normal way to disable the communication state that causes the error.

## What `code.ips` does

The patch removes/bypasses the ORAS communication-error interruption so remote controller input can be used during those early hunts without the game stopping on the communication-error message.

```text
Remote input required
+ PSS communication still active
+ PSS menu not yet available
→ code.ips prevents the communication-error interruption
```

## Game-specific patches

```text
000400000011C400  → Omega Ruby 1.4
000400000011C500  → Alpha Sapphire 1.4
```

Use the patch that matches the game being run.

## What it does NOT do

`code.ips` is not the RAM bridge and is not the controller. It does not:

- generate controller inputs
- detect shiny Pokémon
- alter shiny odds
- modify Pokémon data
- change PID, IVs or encounter generation
- provide a game-RAM write path

Its job is narrowly defined: **stop the ORAS communication-error path from interrupting automation when PSS communication cannot yet be disabled normally.**