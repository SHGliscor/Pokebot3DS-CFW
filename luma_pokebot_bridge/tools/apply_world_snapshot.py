#!/usr/bin/env python3
"""Read-only AS snapshot18; retains HOME39 and leased input16/17."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]/'Luma3DS'
SNAPSHOT_CODE=r'''
/* AS v1.4 profile1. Read-only, no input side effects, one process handle. */
#pragma pack(push,1)
typedef struct PokebotWorldSnapshot {
    u32 magic, version;
    u64 titleId;
    u32 processId;
    u64 startTick, positionTick, endTick;
    u32 battleBefore, battleAfter, flags;
    u8 primaryBefore[0xD8];
    u8 secondary[12];
    u8 primaryAfter[0xD8];
} PokebotWorldSnapshot;
#pragma pack(pop)
_Static_assert(sizeof(PokebotWorldSnapshot)==500, "snapshot wire size");

static PokebotStatus Pokebot_ReadWorldSnapshot(const PokebotTarget *target,
    u32 expectedPid, u32 profile, PokebotWorldSnapshot *out, Result *outResult)
{
    *outResult=0;
    if (target->titleId!=POKEBOT_AS_TID || !expectedPid ||
        expectedPid!=target->pid || profile!=1)
        return POKEBOT_STATUS_BAD_COMMAND;
    memset(out,0,sizeof(*out));
    out->magic=0x31504E53UL;
    out->version=1;
    out->titleId=target->titleId;
    out->processId=target->pid;
    out->startTick=svcGetSystemTick();
    PokebotStatus status=Pokebot_ReadTarget(target->process,0x081FB478,4,
        &out->battleBefore,outResult);
    if (status!=POKEBOT_STATUS_OK) return status;
    out->battleAfter=out->battleBefore;
    if (out->battleBefore!=0x00040000UL)
    {
        out->positionTick=out->endTick=svcGetSystemTick();
        return POKEBOT_STATUS_OK;
    }
    status=Pokebot_ReadTarget(target->process,0x08C6E7B0,0xD8,out->primaryBefore,outResult);
    if (status!=POKEBOT_STATUS_OK) return status;
    status=Pokebot_ReadTarget(target->process,0x08DA8568,12,out->secondary,outResult);
    if (status!=POKEBOT_STATUS_OK) return status;
    out->positionTick=svcGetSystemTick();
    status=Pokebot_ReadTarget(target->process,0x08C6E7B0,0xD8,out->primaryAfter,outResult);
    if (status!=POKEBOT_STATUS_OK) return status;
    status=Pokebot_ReadTarget(target->process,0x081FB478,4,&out->battleAfter,outResult);
    if (status!=POKEBOT_STATUS_OK) return status;
    out->endTick=svcGetSystemTick();
    out->flags=1;
    return POKEBOT_STATUS_OK;
}
'''

def one(s,a,b):
    if s.count(a)!=1:raise RuntimeError(f'Unexpected source anchor {a[:75]!r}')
    return s.replace(a,b,1)

def main():
    p=ROOT/'sysmodules/rosalina/source/pokebot_ram_bridge.c';s=p.read_text()
    for required in ['POKEBOT_CMD_HOME_CAPS = 13','POKEBOT_CMD_HOME_PULSE = 14','req->command == 16 || req->command == 17']:
        if required not in s:raise RuntimeError('Missing validated HOME/lease source feature: '+required)
    s=one(s,'/* HOME capability/pulse response, guarded by nonce, 3DS endpoint, Crystal PID */',SNAPSHOT_CODE+'\n/* HOME capability/pulse response, guarded by nonce, 3DS endpoint, Crystal PID */')
    route=r'''    if (req->command == 18)
    {
        PokebotWorldSnapshot snapshot;
        Result snapshotResult=0;
        PokebotStatus status=Pokebot_ReadWorldSnapshot(&target,req->argument,
            req->aux,&snapshot,&snapshotResult);
        svcCloseHandle(target.process);
        Pokebot_SendResponse(sock,remote,remoteLen,req,status,snapshotResult,
            status==POKEBOT_STATUS_OK ? &snapshot : NULL,
            status==POKEBOT_STATUS_OK ? sizeof(snapshot) : 0);
        return;
    }

'''
    s=one(s,'    if (req->command == POKEBOT_CMD_FRAMEBUFFER_INFO)',route+'    if (req->command == POKEBOT_CMD_FRAMEBUFFER_INFO)')
    s=one(s,'"Pokebot3DS-Luma-v0p6-home39-lease1"','"Pokebot3DS-Luma-v0p6-home39-snap1"')
    p.write_text(s)
    p=ROOT/'sysmodules/rosalina/source/menus.c';s=p.read_text();s=one(s,'Pokebot-Luma v0p6-home39-lease1','Pokebot-Luma v0p6-home39-snap1');p.write_text(s)
    print('Read-only AS500-byte snapshot18 applied; leased input and existing services retained.')

if __name__=='__main__':main()
