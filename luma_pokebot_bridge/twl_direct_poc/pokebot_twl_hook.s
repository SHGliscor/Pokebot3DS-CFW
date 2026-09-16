.syntax unified
.cpu mpcore
.thumb

.global pokebot_twl_hook_start
.type pokebot_twl_hook_start, %function

/*
 * Pokebot TWL direct-input proof v0p2.
 *
 * Hooked from TwlBg's per-frame HID update routine, but stored in the same
 * unused PXI-log function area used by the established TwlBg/RTCom patch.
 *
 * Physical Y is suppressed and converted to DS A through LGY_HIDEMU.
 */
pokebot_twl_hook_start:
    push    {r0-r3}

    /* HID_PAD is active-low; physical Y is bit 11. */
    ldr     r0, =0x10146000
    ldrh    r1, [r0]
    lsls    r1, r1, #20
    bmi     y_released

y_pressed:
    /* Override A and Y as seen by the DS CPU. */
    ldr     r0, =0x10141110      /* LGY_HIDEMU_MASK */
    ldrh    r1, [r0]
    ldr     r2, =0x00000801      /* A | Y */
    orrs    r1, r2
    strh    r1, [r0]

    ldr     r0, =0x10141112      /* LGY_HIDEMU_PAD */
    ldrh    r1, [r0]
    movs    r2, #1
    bics    r1, r2               /* A pressed (active-low 0) */
    movs    r2, #8
    lsls    r2, r2, #8
    orrs    r1, r2               /* Y released (1) */
    strh    r1, [r0]
    b       hook_done

y_released:
    /* Return A/Y bits to physical hardware when Y is not held. */
    ldr     r0, =0x10141110
    ldrh    r1, [r0]
    ldr     r2, =0x00000801
    bics    r1, r2
    strh    r1, [r0]

hook_done:
    pop     {r0-r3}

    /* Replay the two Thumb instructions replaced at the HID hook. */
    .hword  0x0E01
    .hword  0x4308
    bx      lr

    .align 2
.size pokebot_twl_hook_start, .-pokebot_twl_hook_start
