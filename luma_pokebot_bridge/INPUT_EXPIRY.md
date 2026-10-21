# Optional console-side held-input expiry (HOME39 lease1 test)

This source extends the exact lineage of Roger's uploaded combined firmware:
`boot(7).firm`, SHA-256 `61180b0a8bd76e8f36e68e19d9ad425b144aef1459137bb7ca0f0dde3109e848`.
It matches the successful `feature/crystal-home-v39` build at
`fdd492e49dcfff9940318db010a0362e6d07d616` byte for byte. The installed PING
string still says `v0p6-n3ds-fb1`, whereas the Rosalina menu identifies HOME v39.

The existing ORAS/XY/Crystal title checks, framebuffer commands 11/12, guarded
Crystal HOME commands 13/14, additive physical controls and other firmware
modules are retained. Existing mGBA applications and files are not replaced.
No new game-memory write capability is introduced.

## Wire extension

Same UDP4952 v1 framing as the existing bridge. Input capability bit9 (`0x200`)
is present only if the separate expiry thread was created successfully.

| Command | Argument | Aux | Meaning |
| --- | --- | --- | --- |
| 16 HID_LEASE | Active-low HID mask | Lease milliseconds, 50..250 | Start a held input using the request ID as its lease identity |
| 17 HID_RENEW | Lease identity | Increasing token, 1..0x7fffffff | Extend the active lease by its original duration without releasing/repressing |
| 7 INPUT_STATUS | Lease identity | 0 | Observe the existing 20-byte status |
| 8 RELEASE_ALL | 0 | 0 | Immediately release all injected input |

A repeated start request ID is observational. A repeated renewal token does not
extend the deadline. A lower token, wrong lease, expired lease or released lease
cannot renew. New leased commands validate reply-buffer capacity before input
mutation. Status is ABORTED (5), neutral HID4095 and remaining0 after expiry.
Runtime bit2 (`0x4`) records expiry actually performed by the timer thread;
network-side status/update handling cannot set it. New input clears the marker.
Lease duration is measured from console acceptance; expiry is serviced every
5ms under normal scheduling. This is not a hard real-time guarantee against a
console-wide hang, suspended system or scheduler starvation.

The timer runs independently of UDP polling, RAM reads and HOME event sleeps.
A LightLock serializes controller state and remote writes across threads. No
lock spans a UDP wait or game RAM read. Its creation happens before Rosalina's
menu/network threads, and pre-termination releases injected input.

Legacy command10 remains indefinite for compatibility with existing ORAS, XY,
Crystal and other clients. Those clients do not acquire expiry merely by
installing this firmware. Walking must use the new leased commands and renew
only after fresh valid RAM observations; that integration follows the initial
hardware expiry gate. The existing Route101 walking probe still uses command10.
A console expiry only limits further input; it does not independently validate
terrain, battle state or the PC's chosen direction.

## First hardware gate

Back up the current SD-root `boot.firm`; install the candidate as SD:/boot.firm,
keeping existing game `code.ips`, LayeredFS and mGBA application files. Open
Alpha Sapphire in the overworld and enable both Pokebot bridges. Run
`PC_TEST/run_expiry_probe.bat` (default192.168.1.20; override `--host ADDRESS`).

This self-running test sends only L-shoulder holds, no movement/touch/reset. It
checks expiry after450ms of no requests, requires the console timer marker,
checks continuous renewal, stops renewing, and verifies an expired lease cannot
restart. It attempts release on completion or failure and writes a JSONL,
status JSON and support ZIP into `PC_TEST/logs`. Upload that ZIP. A missing ACK
or marker yields HOLD; neither is treated as a verified physical release.

Offline tests execute the transformed controller C on the host, with unavoidable
3DS clock/thread/HID interface stubs. These establish logic, not actual console
scheduling, boot compatibility or game interaction. Build outputs are TEST
candidates until hardware checks pass. No automated walking in this package.
