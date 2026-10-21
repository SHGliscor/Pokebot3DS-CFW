"""Execute generated controller C on the host; OS/HID dependencies are stubbed."""
import ast
import ctypes as C
import subprocess
import tempfile
import unittest
from pathlib import Path
TOOLS = Path(__file__).resolve().parents[1] / 'tools'

class ExpiryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        p = Path(cls.tmp.name)
        tree = ast.parse((TOOLS/'apply_ack_controller_v0p5.py').read_text())
        original = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='source' for t in n.targets))
        patch = TOOLS/'apply_input_expiry.py'
        if patch.exists():
            import importlib.util
            spec=importlib.util.spec_from_file_location('expiry_patch',patch)
            mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
            original=mod.transform_controller(original)
        for name in ['3ds.h','input_redirection.h','pokebot_input_controller.h','MyThread.h']:
            (p/name).write_text('')
        (p/'controller.c').write_text(original)
        (p/'harness.c').write_text(r'''
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
typedef uint32_t u32; typedef uint16_t u16; typedef uint8_t u8;
typedef uint64_t u64; typedef int32_t s32; typedef int64_t s64;
typedef int Result; typedef int LightLock; typedef struct {int handle;} MyThread;
#define CTR_ALIGN(n) __attribute__((aligned(n)))
#define CORE_SYSTEM 0
#define R_FAILED(r) ((r)<0)
static u64 clock_ms; static u32 clock_step; static u32 remote_hid=4095, remote_touch=0x02000000;
static int thread_error, sleeps; static void (*timer_entry)(void);
bool inputRedirectionEnabled=false, preTerminationRequested=false;
u64 osGetTime(void){u64 now=clock_ms;clock_ms+=clock_step;return now;}
void step_clock(u32 ms){clock_step=ms;}
void LightLock_Init(LightLock *x){*x=1;}
void LightLock_Lock(LightLock *x){(void)x;}
void LightLock_Unlock(LightLock *x){(void)x;}
Result MyThread_Create(MyThread*t,void(*f)(void),void*s,u32 z,int p,int a){(void)t;(void)s;(void)z;(void)p;(void)a;timer_entry=f;return thread_error;}
void svcSleepThread(s64 n){clock_ms+=n/1000000;if(++sleeps>=60)preTerminationRequested=true;}
void PokebotInput_SetRemoteHid(u32 v){remote_hid=v;}
void PokebotInput_SetRemoteTouch(u32 v){remote_touch=v;}
void PokebotInput_ResetRemote(void){remote_hid=4095;remote_touch=0x02000000;}
Result InputRedirection_DoOrUndoPatches(void){return 0;}
#include "controller.c"
static u32 last_payload[8];
int init(void){
#ifdef POKEBOT_CMD_HID_LEASE
 PokebotInputController_CreateExpiryThread();
#endif
 return PokebotInputController_SetEnabled(true);
}
int send_cmd(u16 cmd,u32 seq,u32 arg,u32 aux){u32 len; s32 result;return PokebotInputController_Handle(cmd,seq,arg,aux,last_payload,sizeof(last_payload),&len,&result);}
u32 field(int i){return last_payload[i];}
u32 hid(void){return remote_hid;}
void advance(u32 ms){clock_ms+=ms;PokebotInputController_Update();}
void run_timer(void){if(timer_entry)timer_entry();}
void fail_thread(void){thread_error=-1;}
''')
        result=subprocess.run(['cc','-std=c11','-shared','-fPIC','-I',str(p),str(p/'harness.c'),'-o',str(p/'controller.so')],capture_output=True,text=True)
        if result.returncode:raise RuntimeError(result.stderr)
        cls.binary=(p/'controller.so').read_bytes()
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def setUp(self):
        p=Path(self.tmp.name)/f'{self._testMethodName}.so';p.write_bytes(self.binary)
        self.c=C.CDLL(str(p));self.c.field.restype=C.c_uint32;self.c.hid.restype=C.c_uint32
    def start(self):
        self.assertEqual(self.c.init(),0)
        self.assertEqual(self.c.send_cmd(16,100,0xFDF,250),0,'leased latch must be supported')
    def test_expiry_releases_without_any_udp_request(self):
        self.start();self.assertEqual(self.c.hid(),0xFDF)
        self.c.advance(249);self.assertEqual(self.c.hid(),0xFDF)
        self.c.advance(1);self.assertEqual(self.c.hid(),4095)
        self.c.send_cmd(7,101,100,0);self.assertEqual(self.c.field(1),5)
    def test_timer_runs_without_network_loop(self):
        self.start();self.c.run_timer();self.assertEqual(self.c.hid(),4095)
        self.c.send_cmd(7,101,100,0);self.assertTrue(self.c.field(4)&4, "timer must record release before a status request")
    def test_renew_keeps_hold_continuous(self):
        self.start();self.c.advance(150)
        self.assertEqual(self.c.send_cmd(17,101,100,1),0)
        self.c.advance(150);self.assertEqual(self.c.hid(),0xFDF)
        self.c.advance(100);self.assertEqual(self.c.hid(),4095)
    def test_replayed_renew_does_not_extend(self):
        self.start();self.c.advance(100);self.assertEqual(self.c.send_cmd(17,101,100,1),0)
        self.c.advance(100);self.c.send_cmd(17,101,100,1)
        self.c.advance(150);self.assertEqual(self.c.hid(),4095)
    def test_expired_lease_cannot_be_revived_by_renew(self):
        self.start();self.c.advance(250)
        self.assertNotEqual(self.c.send_cmd(17,101,100,1),0);self.assertEqual(self.c.hid(),4095)
    def test_deadline_crossing_during_renew_does_not_revive(self):
        self.start();self.c.advance(249);self.c.step_clock(2)
        self.assertNotEqual(self.c.send_cmd(17,101,100,1),0)
        self.assertEqual(self.c.hid(),4095)
    def test_wrong_sequence_does_not_extend(self):
        self.start();self.c.advance(200)
        self.assertNotEqual(self.c.send_cmd(17,101,99,1),0)
        self.c.advance(50);self.assertEqual(self.c.hid(),4095)
    def test_duplicate_start_does_not_extend(self):
        self.start();self.c.advance(200);self.c.send_cmd(16,100,0xFDF,250)
        self.c.advance(50);self.assertEqual(self.c.hid(),4095)
    def test_release_prevents_renew(self):
        self.start();self.c.send_cmd(8,101,0,0)
        self.assertNotEqual(self.c.send_cmd(17,102,100,1),0);self.assertEqual(self.c.hid(),4095)
    def test_invalid_durations_and_sequence_fail_before_input(self):
        self.c.init()
        for seq,ms in [(100,0),(100,49),(100,251),(0,250)]:
            self.assertNotEqual(self.c.send_cmd(16,seq,0xFDF,ms),0)
            self.assertEqual(self.c.hid(),4095)
    def test_no_expiry_capability_if_timer_cannot_start(self):
        self.c.fail_thread();self.c.init();self.c.send_cmd(5,101,0,0)
        self.assertEqual(self.c.field(1)&512,0)
        self.assertNotEqual(self.c.send_cmd(16,100,0xFDF,250),0)
    def test_legacy_latch_remains_compatible(self):
        self.c.init();self.assertEqual(self.c.send_cmd(10,100,0xFDF,0),0)
        self.c.advance(10000);self.assertEqual(self.c.hid(),0xFDF)
        self.c.send_cmd(8,101,0,0);self.assertEqual(self.c.hid(),4095)
    def test_pulse_still_releases(self):
        self.c.init();self.assertEqual(self.c.send_cmd(6,100,0xFFE,100),0)
        self.c.advance(100);self.assertEqual(self.c.hid(),4095)

if __name__=='__main__':unittest.main()
