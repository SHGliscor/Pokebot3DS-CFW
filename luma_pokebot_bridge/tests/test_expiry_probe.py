import importlib.util
import struct
import unittest
from pathlib import Path
SPEC=importlib.util.spec_from_file_location('expiry_probe',Path(__file__).resolve().parents[1]/'expiry_probe'/'expiry_probe.py')

class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(Path(SPEC.origin).exists(), 'standalone expiry probe is missing')
        self.mod=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(self.mod)
    def test_old_firmware_is_rejected_before_input(self):
        b=FakeBridge(caps=207)
        with self.assertRaises(RuntimeError):self.mod.run_test(b,lambda *a,**k:None,b.sleep)
        self.assertFalse(any(cmd in (16,17) for cmd,_,_,_ in b.calls))
    def test_missing_timer_witness_is_not_a_pass(self):
        b=FakeBridge(witness=False)
        with self.assertRaises(RuntimeError):self.mod.run_test(b,lambda *a,**k:None,b.sleep)
    def test_l_only_and_no_movement_input(self):
        b=FakeBridge();self.mod.run_test(b,lambda *a,**k:None,b.sleep)
        starts=[arg for cmd,_,arg,_ in b.calls if cmd==16]
        self.assertTrue(starts);self.assertEqual(set(starts),{0xDFF})
    def test_expired_renew_is_checked(self):
        b=FakeBridge();events=[];self.mod.run_test(b,lambda event,**k:events.append(event),b.sleep)
        self.assertIn('expired_renew_rejected',events)

class FakeBridge:
    def __init__(self,caps=719,witness=True):
        self.calls=[];self.seq=10;self.now=0;self.deadline=0;self.lease=0;self.caps=caps;self.witness=witness
    def sleep(self,seconds):self.now+=seconds
    def request(self,cmd,arg=0,aux=0,expected_status=0,request_id=None):
        self.seq+=1;seq=self.seq if request_id is None else request_id
        self.calls.append((cmd,seq,arg,aux))
        if cmd==1:return b'Pokebot3DS-Luma-v0p6-home39-lease1',seq
        if cmd==2:return struct.pack('<QI8sI',0x000400000011C500,58,b'sango-2',0),seq
        if cmd==4:return struct.pack('<I',0x40000),seq
        if cmd==5:return struct.pack('<6I',1,self.caps,1,4095,5000,5000),seq
        if cmd==8:return struct.pack('<5I',seq,3,4095,0,1),seq
        if cmd==16:self.deadline=self.now+.250;self.lease=seq
        if cmd==17:
            if self.now>=self.deadline:
                if expected_status!=12:raise RuntimeError('expired')
                return b'',seq
            self.deadline=self.now+.250
        active=self.now<self.deadline
        return struct.pack('<5I',self.lease,2 if active else 5,0xDFF if active else 4095,round((self.deadline-self.now)*1000) if active else 0,1 if active else 1|(4 if self.witness else 0)),seq
