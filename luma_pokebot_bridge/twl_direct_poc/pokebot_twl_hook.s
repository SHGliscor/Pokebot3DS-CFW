.syntax unified
.cpu mpcore
.thumb

.global pokebot_twl_hook_start
.type pokebot_twl_hook_start, %function

/*
 * Pokebot TWL direct-input proof.
 *
 * Runs inside TwlBg's HID update path. Physical Y is converted into DS A
 * through LGY_HIDEMU_MASK/PAD. No RTCom, ARM7 bridge, or DS ROM patch.
 */
pokebot_twl_hook_start:
    push    {r0-r3}

    /* HID_PAD active-low. Physical Y is bit 11. */
    ldr     r0, =0x10146000
    ldrh    r1, [r0]
    lsls    r1, r1, #20
    bmi     y_released

y_pressed:
    ldr     r0, =0x10141110      /* LGY_HIDEMU_MASK */
    ldrh    r1, [r0]
    ldr     r2, =0x00000801      /* override A | Y */
    orrs    r1, r2
    strh    r1, [r0]

    ldr     r0, =0x10141112      /* LGY_HIDEMU_PAD */
    ldrh    r1, [r0]
    movs    r2, #1
    bics    r1, r2               /* DS A pressed */
    movs    r2, #8
    lsls    r2, r2, #8
    orrs    r1, r2               /* DS Y released/suppressed */
    strh    r1, [r0]
    b       hook_done

y_released:
    ldr     r0, =0x10141110
    ldrh    r1, [r0]
    ldr     r2, =0x00000801
    bics    r1, r2               /* release our A/Y override */
    strh    r1, [r0]

hook_done:
    pop     {r0-r3}

    /* Replay the two Thumb instructions replaced by the BL hook. */
    .hword  0x0E01
    .hword  0x4308
    bx      lr

    .align 2
.size pokebot_twl_hook_start, .-pokebot_twl_hook_start
