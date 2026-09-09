// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once

#include "types.h"

namespace PokebotBridge
{
    static constexpr u16 Port = 4953;

    bool Init();
    void DeInit();

    // Called once per emulated frame, immediately before NDS::SetKeyMask().
    // keyMask uses the DS active-low 12-bit keypad representation.
    void ApplyFrame(u32& keyMask);
}
