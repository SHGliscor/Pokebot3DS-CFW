#!/usr/bin/env python3
"""Optional leased HID on the exact source lineage of Roger's HOME v39 FIRM.

Run last. Commands 1-14 and legacy indefinite latch 10 remain unchanged.
A separate Rosalina thread services deadlines even if the UDP/RAM thread blocks.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / 'Luma3DS'

def one(s, old, new):
    if s.count(old) != 1:
        raise RuntimeError(f'Expected one source anchor: {old[:90]!r}, found {s.count(old)}')
    return s.replace(old, new, 1)

def transform_controller(s):
    s=one(s,'#include <string.h>','#include <string.h>\n#include "MyThread.h"\n#include "menu.h"\nextern bool preTerminationRequested;')
    s=one(s,'#define POKEBOT_CMD_HID_LATCH   10', '''#define POKEBOT_CMD_HID_LATCH   10
#define POKEBOT_CMD_HID_LEASE   16
#define POKEBOT_CMD_HID_RENEW   17
#define POKEBOT_CAP_HID_LEASE   (1UL << 9)
#define POKEBOT_LEASE_MIN_MS    50UL
#define POKEBOT_LEASE_MAX_MS    250UL''')
    s=one(s,'#define POKEBOT_KIND_HID_LATCH   3','#define POKEBOT_KIND_HID_LATCH   3\n#define POKEBOT_KIND_HID_LEASE   4')
    s=one(s,'    u64 deadlineMs;','    u64 deadlineMs;\n    u32 renewToken;\n    bool expiredByTimer;')
    s=one(s,'    return flags;', '    if (sInput.expiredByTimer) flags |= (1UL << 2);\n    return flags;')
    s=one(s,'static PokebotInputRuntime sInput;', '''static PokebotInputRuntime sInput;
static LightLock sInputLock;
static MyThread sExpiryThread;
static u8 CTR_ALIGN(8) sExpiryStack[0x1000];
static bool sExpiryReady = false;''')
    for name in ['Update','ReleaseAll','SetEnabled','Handle']:
        s=s.replace('PokebotInputController_'+name+'(', 'PokebotInputController_'+name+'Unlocked(')
    # All state transitions and hardware writes are serialized by public wrappers.
    for typ,name in [('void','Update'),('void','ReleaseAll'),('Result','SetEnabled'),('u16','Handle')]:
        s=s.replace(typ+' PokebotInputController_'+name+'Unlocked(', 'static '+typ+' PokebotInputController_'+name+'Unlocked(')
    s=one(s,'    sInput.state = POKEBOT_INPUT_COMPLETED;\n    neutral();', '''    sInput.state = sInput.kind == POKEBOT_KIND_HID_LEASE ?
                   POKEBOT_INPUT_ABORTED : POKEBOT_INPUT_COMPLETED;
    neutral();''')
    anchor='static u16 PokebotInputController_HandleUnlocked('
    helpers=r'''static u16 startHidLease(u16 command, u32 sequence, u32 rawHid, u32 leaseMs)
{
    if (!sExpiryReady || !sequence || !validRawHid(rawHid) ||
        leaseMs < POKEBOT_LEASE_MIN_MS || leaseMs > POKEBOT_LEASE_MAX_MS)
        return POKEBOT_STATUS_INPUT_INVALID;
    if (active())
        return POKEBOT_STATUS_INPUT_BUSY;
    memset(&sInput, 0, sizeof(sInput));
    sInput.sequence = sequence;
    sInput.command = command;
    sInput.state = POKEBOT_INPUT_IN_PROGRESS;
    sInput.rawHid = rawHid;
    sInput.touchState = POKEBOT_TOUCH_NEUTRAL;
    sInput.holdMs = leaseMs;
    sInput.kind = POKEBOT_KIND_HID_LEASE;
    sInput.phase = POKEBOT_PHASE_LATCHED;
    sInput.deadlineMs = osGetTime() + leaseMs;
    PokebotInput_SetRemoteTouch(POKEBOT_TOUCH_NEUTRAL);
    PokebotInput_SetRemoteHid(rawHid);
    pokebotInputCommands++;
    return POKEBOT_STATUS_OK;
}

static u16 renewHidLease(u32 sequence, u32 token)
{
    /* Update ran before this check. An expired/released hold cannot restart. */
    if (!sExpiryReady || !active() || sInput.kind != POKEBOT_KIND_HID_LEASE ||
        !sequence || sequence != sInput.sequence || !token || token > 0x7FFFFFFFUL ||
        token < sInput.renewToken)
        return POKEBOT_STATUS_INPUT_INVALID;
    u64 now = osGetTime();
    if (now >= sInput.deadlineMs)
    {
        PokebotInputController_ReleaseAllUnlocked();
        return POKEBOT_STATUS_INPUT_INVALID;
    }
    /* Replayed renewals are observational; they never extend the deadline. */
    if (token > sInput.renewToken)
    {
        sInput.renewToken = token;
        sInput.deadlineMs = now + sInput.holdMs;
        pokebotInputCommands++;
    }
    return POKEBOT_STATUS_OK;
}

'''
    s=one(s,anchor,helpers+anchor)
    s=one(s,'        caps.capabilityFlags = POKEBOT_INPUT_CAPS;',
          '        caps.capabilityFlags = POKEBOT_INPUT_CAPS | (sExpiryReady ? POKEBOT_CAP_HID_LEASE : 0);')
    s=one(s,'    if (duplicate(command, requestId))', '''    if (command == POKEBOT_CMD_HID_LEASE || command == POKEBOT_CMD_HID_RENEW)
    {
        if (payloadCapacity < sizeof(PokebotInputStatusPayload))
            return POKEBOT_STATUS_INPUT_INVALID;
        if (command == POKEBOT_CMD_HID_RENEW)
        {
            u16 code = renewHidLease(argument, aux);
            if (code != POKEBOT_STATUS_OK) return code;
            PokebotInputStatusPayload status;
            fillStatus(&status, 0xFFFFFFFFUL);
            memcpy(payload, &status, sizeof(status));
            *payloadLength = sizeof(status);
            return POKEBOT_STATUS_OK;
        }
    }

    if (duplicate(command, requestId))''')
    s=one(s,'    u16 statusCode = POKEBOT_STATUS_BAD_COMMAND;', '''    u16 statusCode = POKEBOT_STATUS_BAD_COMMAND;
    if (command == POKEBOT_CMD_HID_LEASE)
        statusCode = startHidLease(command, requestId, argument, aux);
    else''')
    s+=r'''
/* Only these entrypoints cross threads; no lock spans UDP, RAM reads or sleep. */
void PokebotInputController_Update(void)
{
    LightLock_Lock(&sInputLock);
    PokebotInputController_UpdateUnlocked();
    LightLock_Unlock(&sInputLock);
}

void PokebotInputController_ReleaseAll(void)
{
    LightLock_Lock(&sInputLock);
    PokebotInputController_ReleaseAllUnlocked();
    LightLock_Unlock(&sInputLock);
}

Result PokebotInputController_SetEnabled(bool enable)
{
    LightLock_Lock(&sInputLock);
    Result res = PokebotInputController_SetEnabledUnlocked(enable);
    LightLock_Unlock(&sInputLock);
    return res;
}

u16 PokebotInputController_Handle(u16 command, u32 requestId, u32 argument, u32 aux,
    void *payload, u32 payloadCapacity, u32 *payloadLength, s32 *result)
{
    LightLock_Lock(&sInputLock);
    u16 status = PokebotInputController_HandleUnlocked(command, requestId, argument,
        aux, payload, payloadCapacity, payloadLength, result);
    LightLock_Unlock(&sInputLock);
    return status;
}

static void expiryThreadMain(void)
{
    while (!preTerminationRequested)
    {
        LightLock_Lock(&sInputLock);
        bool expiringLease = active() && sInput.kind == POKEBOT_KIND_HID_LEASE &&
                             osGetTime() >= sInput.deadlineMs;
        PokebotInputController_UpdateUnlocked();
        if (expiringLease && !active()) sInput.expiredByTimer = true;
        LightLock_Unlock(&sInputLock);
        svcSleepThread(5 * 1000 * 1000LL);
    }
    LightLock_Lock(&sInputLock);
    PokebotInputController_ReleaseAllUnlocked();
    sExpiryReady = false;
    LightLock_Unlock(&sInputLock);
}

MyThread *PokebotInputController_CreateExpiryThread(void)
{
    /* Called once from main, before menu/network threads can touch the lock. */
    LightLock_Init(&sInputLock);
    Result res = MyThread_Create(&sExpiryThread, expiryThreadMain, sExpiryStack,
        sizeof(sExpiryStack), 0x1F, CORE_SYSTEM);
    sExpiryReady = !R_FAILED(res);
    return sExpiryReady ? &sExpiryThread : NULL;
}
'''
    return s

def main():
    src=ROOT/'sysmodules/rosalina/source'
    inc=ROOT/'sysmodules/rosalina/include'
    c=src/'pokebot_input_controller.c'
    c.write_text(transform_controller(c.read_text()))
    h=inc/'pokebot_input_controller.h'
    h.write_text(h.read_text()+'\n#include "MyThread.h"\nMyThread *PokebotInputController_CreateExpiryThread(void);\n')
    p=src/'main.c';s=p.read_text()
    s=one(s,'#include "input_redirection.h"','#include "input_redirection.h"\n#include "pokebot_input_controller.h"')
    s=one(s,'    MyThread *menuThread = menuCreateThread();','    MyThread *inputExpiryThread = PokebotInputController_CreateExpiryThread();\n    MyThread *menuThread = menuCreateThread();')
    s=one(s,'    MyThread_Join(menuThread, -1LL);','    MyThread_Join(inputExpiryThread, -1LL);\n    MyThread_Join(menuThread, -1LL);')
    p.write_text(s)
    p=src/'pokebot_ram_bridge.c';s=p.read_text()
    s=one(s,'if (req->command >= 5 && req->command <= 10)',
          'if ((req->command >= 5 && req->command <= 10) || req->command == 16 || req->command == 17)')
    s=one(s,'"Pokebot3DS-Luma-v0p6-n3ds-fb1"','"Pokebot3DS-Luma-v0p6-home39-lease1"')
    p.write_text(s)
    p=src/'menus.c';p.write_text(p.read_text().replace('Pokebot-Luma v0p6-n3ds-home-v39','Pokebot-Luma v0p6-home39-lease1'))
    print('Independent expiry thread and optional leased HID 16/17 applied; legacy commands retained.')

if __name__=='__main__':main()
