#include <3ds.h>
#include <3ds/allocator/mappable.h>
#include <3ds/os.h>

// libctru's default heap allocator targets the APPLICATION memory region.
// This CXI is a BASE-memory sysmodule, so allocate both heaps explicitly from
// MEMOP_REGION_BASE.  Without this override the process can fail before main()
// ever reaches the UDP/HID diagnostics.

extern u32 __ctru_heap;
extern u32 __ctru_heap_size;
extern u32 __ctru_linear_heap;
extern u32 __ctru_linear_heap_size;
extern char *fake_heap_start;
extern char *fake_heap_end;

void __system_allocateHeaps(void)
{
    u32 out = 0;

    __ctru_heap_size = 0x00400000; // 4 MiB, BASE region
    __ctru_heap = 0x08000000;
    Result rc = svcControlMemory(
        &out,
        __ctru_heap,
        0,
        __ctru_heap_size,
        MEMOP_ALLOC | MEMOP_REGION_BASE,
        MEMPERM_READWRITE);
    if (R_FAILED(rc))
        svcBreak(USERBREAK_PANIC);

    __ctru_linear_heap_size = 0x00100000; // 1 MiB, BASE region
    __ctru_linear_heap = 0x10000000;
    rc = svcControlMemory(
        &out,
        __ctru_linear_heap,
        0,
        __ctru_linear_heap_size,
        MEMOP_ALLOC_LINEAR | MEMOP_REGION_BASE,
        MEMPERM_READWRITE);
    if (R_FAILED(rc))
        svcBreak(USERBREAK_PANIC);

    fake_heap_start = (char *)__ctru_heap;
    fake_heap_end = fake_heap_start + __ctru_heap_size;

    // HidObserverInit() uses mappableAlloc() for the read-only HID shared-memory
    // mapping, so seed libctru's map-area allocator as the default implementation
    // normally would.
    mappableInit(OS_MAP_AREA_BEGIN, OS_MAP_AREA_END);
}
