#!/usr/bin/env python3
"""Fail-closed HOME capability patch for the v0p6 New3DS Pokebot bridge.

Run after the existing v0p6 New3DS XY bridge build-patches. Crystal allowlist
is added (if not already present). This is not proof that the resulting
boot.firm is bit-for-bit identical to the user-proven `v0p6-n3ds-cr1` binary.
HOME commands 13/14 deliberately leave 11/12 framebuffer commands intact.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2] / 'Luma3DS'
src = root/'sysmodules'/'rosalina'/'source'/'pokebot_ram_bridge.c'
menu = root/'sysmodules'/'rosalina'/'source'/'menus.c'


def one(s, a, b, label):
    if b in s:
        return s
    if s.count(a) != 1:
        raise RuntimeError(f'{label}: expected one exact anchor, got {s.count(a)}')
    return s.replace(a,b,1)


def apply(text):
    for marker in ('POKEBOT_CMD_FRAMEBUFFER_INFO = 11', 'POKEBOT_CMD_FRAMEBUFFER_READ = 12',
                   'if (req->command >= 5 && req->command <= 10)',
                   'POKEBOT_CMD_READ      = 4'):
        if marker not in text:
            raise RuntimeError(f'Missing validated v0p6 bridge feature: {marker}')
    if 'POKEBOT_CMD_HOME_CAPS = 13' in text:
        raise RuntimeError('HOME patch already present; refusing second application')
    if 'svcWriteProcessMemory' in text:
        raise RuntimeError('Unexpected write-capable firmware source')
    # Latest shipped v0p6 New3DS XY branch supports OR/AS/XY, but not Crystal.
    if 'POKEBOT_CRYSTAL_EN_TID' not in text:
        text = one(text,
            '#define POKEBOT_AS_TID 0x000400000011C500ULL',
            '#define POKEBOT_AS_TID 0x000400000011C500ULL\n#define POKEBOT_CRYSTAL_EN_TID 0x0004000000172800ULL',
            'Crystal title ID')
        text = one(text,
            'return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID ||',
            'return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID ||',
            'title predicate no-op') if False else text
        # Replace exact return expression only if one of the two known source layouts.
        if 'tid == POKEBOT_CRYSTAL_EN_TID' not in text:
            if 'return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID;' in text:
                text=one(text,'return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID;',
                    'return tid == POKEBOT_OR_TID || tid == POKEBOT_AS_TID || tid == POKEBOT_CRYSTAL_EN_TID;',
                    'title predicate base')
            else:
                # The XY branch uses a wrapped allowlist; insert ahead of final return.
                i=text.index('static bool Pokebot_IsSupportedTitle(')
                j=text.index('\n}',i)
                sub=text[i:j]
                if 'return ' not in sub:
                    raise RuntimeError('Could not inspect title allowlist')
                sub2=sub.replace('return ', 'return tid == POKEBOT_CRYSTAL_EN_TID || ', 1)
                text=text[:i]+sub2+text[j:]
        if 'return "trl";' not in text:
            # Insert process label in the helper without modifying XY/ORAS labels.
            i=text.index('static const char *Pokebot_ProcessName(')
            j=text.index('\n}',i)
            sub=text[i:j]
            sub=one(sub,'    return "unknown";',
                '    if (tid == POKEBOT_CRYSTAL_EN_TID) return "trl";\n    return "unknown";',
                'Crystal process name')
            text=text[:i]+sub+text[j:]
    text = one(text,
        '    POKEBOT_CMD_FRAMEBUFFER_READ = 12,',
        '    POKEBOT_CMD_FRAMEBUFFER_READ = 12,\n'
        '    POKEBOT_CMD_HOME_CAPS = 13,\n'
        '    POKEBOT_CMD_HOME_PULSE = 14,',
        'HOME command enum')
    header=r'''
/* HOME capability/pulse response, guarded by nonce, 3DS endpoint, Crystal PID */
#define POKEBOT_HOME_MAGIC 0x484F4D45UL
#define POKEBOT_HOME_CAPS_PAYLOAD 0x454D4F48UL
#define POKEBOT_HOME_TICKS_30S 8043355680ULL
#pragma pack(push,1)
typedef struct { u32 magic, version, flags, nonce, hold_ms; } PokebotHomeCapsV39;
typedef struct { u32 press_result, release_result, dispatched; } PokebotHomeResultV39;
#pragma pack(pop)
static struct {
    u32 nonce, source_ip, process_id;
    u16 source_port;
    u64 start_tick;
    bool armed;
} sPokebotHomeV39 = {0};
'''
    text=one(text, 'static void Pokebot_SendResponse(', header+'\nstatic void Pokebot_SendResponse(', 'HOME types and state')
    route=r'''
    /* HOME deliberately uses 13/14. Commands 11/12 belong to framebuffer. */
    if (req->command == POKEBOT_CMD_HOME_CAPS || req->command == POKEBOT_CMD_HOME_PULSE)
    {
        if (target.titleId != POKEBOT_CRYSTAL_EN_TID)
        {
            svcCloseHandle(target.process);
            Pokebot_SendResponse(sock, remote, remoteLen, req,
                                 POKEBOT_STATUS_BAD_COMMAND, 0, NULL, 0);
            return;
        }
        if (req->command == POKEBOT_CMD_HOME_CAPS)
        {
            if (req->argument != 0 || req->aux != 0)
            {
                svcCloseHandle(target.process);
                Pokebot_SendResponse(sock, remote, remoteLen, req,
                                     POKEBOT_STATUS_BAD_COMMAND, 0, NULL, 0);
                return;
            }
            u64 t = svcGetSystemTick();
            u32 nonce = (u32)t ^ (u32)(t>>32) ^ req->requestId ^ 0xCB3A72F1UL;
            if (!nonce) nonce = 0x5182E74FUL;
            sPokebotHomeV39.armed = true;
            sPokebotHomeV39.nonce = nonce;
            sPokebotHomeV39.source_ip = remote->sin_addr.s_addr;
            sPokebotHomeV39.source_port = remote->sin_port;
            sPokebotHomeV39.process_id = target.pid;
            sPokebotHomeV39.start_tick = t;
            PokebotHomeCapsV39 caps = {POKEBOT_HOME_CAPS_PAYLOAD, 1, 1, nonce, 120};
            svcCloseHandle(target.process);
            Pokebot_SendResponse(sock, remote, remoteLen, req,
                                 POKEBOT_STATUS_OK, 0, &caps, sizeof(caps));
            return;
        }
        /* Consume challenge before attempting either event. No retry on lost ACK. */
        bool valid = sPokebotHomeV39.armed &&
            req->argument == sPokebotHomeV39.nonce && req->aux == POKEBOT_HOME_MAGIC &&
            remote->sin_addr.s_addr == sPokebotHomeV39.source_ip &&
            remote->sin_port == sPokebotHomeV39.source_port &&
            target.pid == sPokebotHomeV39.process_id &&
            (svcGetSystemTick()-sPokebotHomeV39.start_tick < POKEBOT_HOME_TICKS_30S);
        sPokebotHomeV39.armed = false;
        sPokebotHomeV39.nonce = 0;
        svcCloseHandle(target.process);
        if (!valid)
        {
            Pokebot_SendResponse(sock, remote, remoteLen, req,
                                 POKEBOT_STATUS_BAD_COMMAND, 0, NULL, 0);
            return;
        }
        PokebotHomeResultV39 result;
        result.dispatched = 1;
        result.press_result = (u32)srvPublishToSubscriber(0x204, 0);
        svcSleepThread(120*1000*1000LL);
        result.release_result = (u32)srvPublishToSubscriber(0x205, 0);
        Pokebot_SendResponse(sock, remote, remoteLen, req,
                             POKEBOT_STATUS_OK, 0, &result, sizeof(result));
        return;
    }

'''
    text=one(text,'    if (req->command == POKEBOT_CMD_GAME_INFO)', route+'    if (req->command == POKEBOT_CMD_GAME_INFO)', 'HOME request route')
    for k in ['POKEBOT_CMD_HOME_CAPS = 13','POKEBOT_CMD_HOME_PULSE = 14',
              'POKEBOT_CMD_FRAMEBUFFER_INFO = 11','POKEBOT_CMD_FRAMEBUFFER_READ = 12',
              'srvPublishToSubscriber(0x204, 0)','srvPublishToSubscriber(0x205, 0)']:
        assert k in text
    assert 'svcWriteProcessMemory' not in text
    return text


def main():
    if not src.exists():
        raise SystemExit(f'Missing generated Luma bridge source: {src}')
    original=src.read_text(encoding='utf-8')
    updated=apply(original)
    src.write_text(updated, encoding='utf-8')
    if menu.exists():
        label=menu.read_text(encoding='utf-8')
        label=label.replace('v0p6-n3ds-fb1','v0p6-n3ds-home-v39')
        menu.write_text(label,encoding='utf-8')
    print('Crystal + guarded HOME commands 13/14 applied to generated v0p6 bridge.')

if __name__ == '__main__':
    main()