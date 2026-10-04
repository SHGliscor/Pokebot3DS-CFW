# Ultra Sun firmware connection test

This branch reconstructs the firmware using the seven source patch scripts
included in Roger's HF105B package, against pinned Luma3DS commit
`d30ac8d1c665ed2a50dc30b291f7eb6b33e9890a`.

The additional patch admits Ultra Sun title `00040000001B5000` and names its
process `momiji`, as recorded in both supplied ExHeader files. The bridge and
menu version become `v0p7-n3ds-fb1-cpad-us1` to distinguish the hardware test.
X/Y and ORAS acceptance, read limits, acknowledged controller, framebuffer,
Circle Pad, and New 3DS latency patches are retained.

`test_title_gate.py` compiles the generated C title predicate and name function
with the host compiler, then executes them. The unmodified source fails for
Ultra Sun; the changed source must accept the five named games and reject the
tested unrelated/update title IDs. This is an offline regression test.

The Actions job builds the reconstructed baseline and the new firmware using
the same compiler image. It records both hashes and exports the source diff,
the final boot.firm, build provenance, and the Luma license. A baseline hash
different from the supplied firmware can reflect toolchain/source differences;
the job does not claim byte-for-byte reproduction of the installed firmware.

Use the existing standalone Ultra Sun PC probe after installing the test
boot.firm. A successful build and title test do not establish real-console RAM
access or controller reaction. RAM service remains read-only. This build does
not include or require an Ultra Sun code.ips, game dump, or game save modification.
