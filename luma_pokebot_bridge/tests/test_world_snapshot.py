import ctypes as C
import importlib.util
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path

class SnapshotFirmwareTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=Path(__file__).resolve().parents[1]/'tools'/'apply_world_snapshot.py'
        if not p.exists():raise AssertionError('single-request world snapshot command is missing')
        spec=importlib.util.spec_from_file_location('snapshot_patch',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        cls.tmp=tempfile.TemporaryDirectory();d=Path(cls.tmp.name)
        (d/'test.c').write_text(r'''
#include <stdint.h>
#include <string.h>
typedef uint8_t u8;typedef uint32_t u32;typedef uint64_t u64;
typedef int Result;typedef int Handle;typedef int PokebotStatus;
typedef struct {Handle process;u64 titleId;u32 pid;u32 launchFlags;} PokebotTarget;
#define POKEBOT_AS_TID 0x000400000011C500ULL
#define POKEBOT_STATUS_OK 0
#define POKEBOT_STATUS_BAD_COMMAND 3
#define POKEBOT_STATUS_INTERNAL 11
#define POKEBOT_STATUS_RANGE_INVALID 8
static u64 ticks;static int calls,fail_at;static u32 battle;
u64 svcGetSystemTick(void){ticks+=1000;return ticks;}
static PokebotStatus Pokebot_ReadTarget(Handle h,u32 addr,u32 size,void*out,Result*result){
 (void)h;calls++;if(calls==fail_at){*result=-123;return 11;}
 memset(out,0,size);
 if(addr==0x081FB478){memcpy(out,&battle,4);}
 else if(addr==0x08C6E7B0){u32 zone=23;float xyz[]={1665.f,2.f,2709.f};memcpy(out,xyz,12);memcpy((u8*)out+0xD4,&zone,4);}
 else if(addr==0x08DA8568){float xyz[]={1665.f,2.f,2709.f};memcpy(out,xyz,12);}
 else return 8;
 return 0;
}
'''+m.SNAPSHOT_CODE+r'''
static PokebotWorldSnapshot snap;static Result result;
int capture(u64 title,u32 pid,u32 expected,u32 profile,int failure,u32 flag){
 PokebotTarget target={1,title,pid,0};calls=0;ticks=0;fail_at=failure;battle=flag;
 return Pokebot_ReadWorldSnapshot(&target,expected,profile,&snap,&result);
}
void* payload(void){return &snap;}
int count(void){return calls;}
int size(void){return sizeof(snap);}
int last_result(void){return result;}
''')
        r=subprocess.run(['cc','-std=c11','-shared','-fPIC',str(d/'test.c'),'-o',str(d/'snapshot.so')],capture_output=True,text=True)
        if r.returncode:raise RuntimeError(r.stderr)
        cls.c=C.CDLL(str(d/'snapshot.so'));cls.c.capture.argtypes=[C.c_uint64,C.c_uint32,C.c_uint32,C.c_uint32,C.c_int,C.c_uint32];cls.c.payload.restype=C.c_void_p
    @classmethod
    def tearDownClass(cls):
        if hasattr(cls,'tmp'):cls.tmp.cleanup()
    def capture(self,**kw):
        args={'title':0x400000011C500,'pid':41,'expected':41,'profile':1,'failure':0,'flag':0x40000};args.update(kw)
        return self.c.capture(*args.values())
    def test_full_snapshot_is_five_reads_in_one_500_byte_payload(self):
        self.assertEqual(self.capture(),0);self.assertEqual(self.c.count(),5);self.assertEqual(self.c.size(),500)
        b=C.string_at(self.c.payload(),500);h=struct.unpack_from('<IIQIQQQIII',b)
        self.assertEqual(h[:4],(0x31504E53,1,0x400000011C500,41));self.assertEqual(h[-3:],(0x40000,0x40000,1))
        self.assertLessEqual(h[4],h[5]);self.assertLessEqual(h[5],h[6])
        self.assertEqual(struct.unpack_from('<fff',b,56),(1665.,2.,2709.))
        self.assertEqual(struct.unpack_from('<I',b,56+0xD4)[0],23)
    def test_wrong_game_pid_or_profile_never_reads_memory(self):
        for changes in ({'title':0x4000000055D00},{'expected':42},{'expected':0},{'profile':0}):
            self.assertNotEqual(self.capture(**changes),0);self.assertEqual(self.c.count(),0)
    def test_battle_stops_before_coordinate_reads(self):
        self.assertEqual(self.capture(flag=0x40001),0);self.assertEqual(self.c.count(),1)
        h=struct.unpack_from('<IIQIQQQIII',C.string_at(self.c.payload(),500))
        self.assertEqual(h[-3:],(0x40001,0x40001,0))
    def test_each_read_failure_aborts_the_snapshot(self):
        for n in range(1,6):
            self.assertEqual(self.capture(failure=n),11);self.assertEqual(self.c.count(),n);self.assertEqual(self.c.last_result(),-123)
