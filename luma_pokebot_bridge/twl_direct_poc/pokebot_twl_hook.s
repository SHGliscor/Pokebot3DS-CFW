.syntax unified
.cpu mpcore
.thumb

.global pokebot_twl_hook_start
.type pokebot_twl_hook_start, %function

/*
 * Pokebot TWL direct-input proof.
 *
 * This runs inside TwlBg's normal HID update path.  Physical Y is converted
 * into a DS A press using the LGY HID-emulation registers.  Y itself is
 * suppressed while held.  No ARM7/RTCom/nds-bootstrap communication is used.
 *
 * The hook site overwrites:
 *   0x0E01
 *   0x4308
 * Those instructions are replayed before returning.
 */
pokebot_twl_hook_start:
    push    {r0-r3}

    /* HID_PAD is active-low.  Move physical Y (bit 11) into N. */
    ldr     r0, =0x10146000
    ldrh    r1, [r0]
    lsls    r1, r1, #20
    bmi     y_released

y_pressed:
    /* Override DS A + Y. */
    ldr     r0, =0x10141110      /* LGY_HIDEMU_MASK */
    ldrh    r1, [r0]
    ldr     r2, =0x00000801      /* A | Y */
    orrs    r1, r2
    strh    r1, [r0]

    ldr     r0, =0x10141112      /* LGY_HIDEMU_PAD */
    ldrh    r1, [r0]
    movs    r2, #1
    bics    r1, r2               /* A = pressed (0) */
    movs    r2, #8
    lsls    r2, r2, #8
    orrs    r1, r2               /* Y = released (1) */
    strh    r1, [r0]
    b       hook_done

y_released:
    /* Release our override and return control to normal TwlBg HID handling. */
    ldr     r0, =0x10141110
    ldrh    r1, [r0]
    ldr     r2, =0x00000801
    bics    r1, r2
    strh    r1, [r0]

hook_done:
    pop     {r0-r3}

    /* Replay the two Thumb instructions replaced by the BL hook. */
    .hword  0x0E01
    .hword  0x4308
    bx      lr

    .align 2
.size pokebot_twl_hook_start, .-pokebot_twl_hook_start
