@ This file contains the Luma3DS custom SVC wrapper needed by the 3GX bridge.
@
@ Based on Luma3DS sysmodules/rosalina/source/csvc.s.
@ This altered source keeps only svcControlMemoryUnsafe (custom SVC 0xA3).
@
@ Original license notice:
@
@ This software is provided 'as-is', without any express or implied warranty. In no event will the authors be held liable
@ for any damages arising from the use of this software.
@
@ Permission is granted to anyone to use this software for any purpose, including commercial applications, and to alter it
@ and redistribute it freely, subject to the following restrictions:
@
@ 1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
@ 2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
@ 3. This notice may not be removed or altered from any source distribution.

.arm
.balign 4

.section .text.svcControlMemoryUnsafe, "ax", %progbits
.global svcControlMemoryUnsafe
.type svcControlMemoryUnsafe, %function
.align 2
.cfi_startproc
svcControlMemoryUnsafe:
    str r4, [sp, #-4]!
    ldr r4, [sp, #4]
    svc 0xA3
    ldr r4, [sp], #4
    bx lr
.cfi_endproc
