#!/usr/bin/env python3
"""Bounded L-shoulder expiry check. No D-pad, touch, game RAM writes, or resets."""
import argparse
import json
import secrets
import socket
import struct
import time
import zipfile
from datetime import datetime,timezone
from pathlib import Path

REQ=struct.Struct('<IHHIII')
RESP=struct.Struct('<IHHIIiI')
STATUS=struct.Struct('<5I')
FW=b'Pokebot3DS-Luma-v0p6-home39-lease1'
L_ONLY=0xDFF

class Bridge:
    def __init__(self,host,emit):
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.connect((host,4952));self.sock.settimeout(.4)
        self.seq=secrets.randbelow(0x7FFFF000)+1;self.emit=emit
    def request(self,cmd,arg=0,aux=0,expected_status=0,request_id=None):
        self.seq=(self.seq+1)&0x7FFFFFFF or 1
        seq=self.seq if request_id is None else request_id
        start=time.monotonic();end=start+.4
        self.emit('request',command=cmd,request_id=seq,argument=arg,aux=aux)
        self.sock.send(REQ.pack(0x5242524F,1,cmd,seq,arg,aux))
        while True:
            left=end-time.monotonic()
            if left<=0:raise TimeoutError(f'Command {cmd} timed out; no input retry')
            self.sock.settimeout(left)
            raw=self.sock.recv(2048)
            if len(raw)<RESP.size:continue
            magic,version,status,rid,echo,result,length=RESP.unpack_from(raw)
            if magic!=0x5342524F or version!=1 or rid!=seq:continue
            if echo!=arg or length!=len(raw)-RESP.size:raise RuntimeError('Malformed bridge response')
            self.emit('response',command=cmd,request_id=seq,status=status,result=result,duration_s=time.monotonic()-start,payload_hex=raw[RESP.size:].hex())
            if status!=expected_status or (status==0 and result!=0):
                raise RuntimeError(f'Command {cmd}: status {status}, result {result}; expected {expected_status}')
            return raw[RESP.size:],seq
    def close(self):self.sock.close()

def status_payload(raw,seq,state=None,hid=None,timer=False):
    if len(raw)!=STATUS.size:raise RuntimeError('Invalid controller status length')
    got,gotstate,gothid,remaining,flags=STATUS.unpack(raw)
    if got!=seq or not flags&1:raise RuntimeError('Wrong lease identity or inactive input patch')
    if state is not None and gotstate!=state:raise RuntimeError(f'Expected state {state}, got {gotstate}')
    if hid is not None and gothid!=hid:raise RuntimeError(f'Expected HID {hid:03X}, got {gothid:03X}')
    if state==2 and not 0<remaining<=250:raise RuntimeError('Lease has no valid time remaining')
    if state==5 and remaining:raise RuntimeError('Expired lease still has time remaining')
    if timer and not flags&4:raise RuntimeError('No console timer release witness; expiry is not verified')
    return dict(sequence=got,state=gotstate,raw_hid=gothid,remaining_ms=remaining,runtime_flags=flags)

def run_test(b,emit,sleep=time.sleep):
    ping,_=b.request(1)
    if ping.rstrip(b'\0')!=FW:raise RuntimeError('Requires HOME v39 lease1 test firmware; no press attempted')
    game,_=b.request(2)
    if len(game)!=24:raise RuntimeError('Invalid GAME_INFO')
    tid,pid,name,flags=struct.unpack('<QI8sI',game)
    if tid!=0x000400000011C500 or not pid or name.rstrip(b'\0')!=b'sango-2':
        raise RuntimeError('Open Alpha Sapphire for this probe')
    battle,_=b.request(4,0x081FB478,4)
    if battle!=struct.pack('<I',0x00040000):raise RuntimeError('Alpha Sapphire must be in the overworld')
    caps,_=b.request(5)
    if len(caps)!=24:raise RuntimeError('Invalid input capabilities')
    version,bits,runtime,neutral,_,_=struct.unpack('<6I',caps)
    if version!=1 or not bits&512 or not runtime&1 or neutral!=4095:
        raise RuntimeError('Independent expiry unavailable; no press attempted')
    emit('verified',title_id=f'{tid:016X}',pid=pid,capabilities=bits)
    released,rid=b.request(8)
    status_payload(released,rid,3,4095)
    for renew in (False,True):
        # Recheck game/battle before each bounded L-only hold.
        current,_=b.request(2)
        if current!=game:raise RuntimeError('Game process changed')
        battle,_=b.request(4,0x081FB478,4)
        if battle!=struct.pack('<I',0x00040000):raise RuntimeError('Game left overworld')
        raw,lease=b.request(16,L_ONLY,250)
        emit('lease_started',**status_payload(raw,lease,2,L_ONLY),renewal_test=renew)
        if renew:
            for counter in (1,2,3):
                sleep(.06)
                raw,_=b.request(17,lease,counter)
                emit('lease_renewed',counter=counter,**status_payload(raw,lease,2,L_ONLY))
        # No network traffic during this interval; only the console timer may release.
        emit('silence_started',seconds=.45)
        sleep(.45)
        raw,_=b.request(7,lease)
        emit('timer_expiry_verified',**status_payload(raw,lease,5,4095,timer=True))
        b.request(17,lease,100,expected_status=12)
        raw,_=b.request(7,lease)
        status_payload(raw,lease,5,4095,timer=True)
        emit('expired_renew_rejected',lease=lease)
    emit('expiry_checks_passed')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host',default='192.168.1.20');a=p.parse_args()
    folder=Path(__file__).resolve().parent/'logs';folder.mkdir(exist_ok=True)
    stem='input_expiry_'+datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')
    log=folder/(stem+'.jsonl');summary=folder/(stem+'_status.json');archive=folder/(stem+'.zip')
    started=time.monotonic();result={'result':'HOLD','host':a.host,'release_acknowledged':False}
    with log.open('w',encoding='utf-8') as f:
        def emit(event,**fields):
            row={'event':event,'elapsed_s':time.monotonic()-started,**fields}
            f.write(json.dumps(row)+'\n');f.flush()
            if event in ('verified','lease_started','lease_renewed','timer_expiry_verified','expired_renew_rejected','expiry_checks_passed','hold'):
                print(event,fields,flush=True)
        b=None
        try:
            b=Bridge(a.host,emit);run_test(b,emit);result['result']='PASS'
        except (OSError,RuntimeError,KeyboardInterrupt) as exc:
            result['error']=str(exc) or 'Interrupted';emit('hold',reason=result['error'])
        finally:
            if b is not None:
                for attempt in range(3):
                    try:
                        raw,seq=b.request(8);status_payload(raw,seq,3,4095)
                        result['release_acknowledged']=True;break
                    except (OSError,RuntimeError):pass
                b.close()
            if not result['release_acknowledged']:result['result']='HOLD'
            result['elapsed_s']=time.monotonic()-started
            emit('finished',**result)
    summary.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(log,log.name);z.write(summary,summary.name)
    print('\nResult:',result['result']);print('Upload this support ZIP:',archive)
    return 0 if result['result']=='PASS' else 2

if __name__=='__main__':raise SystemExit(main())
