#include <switch.h>

/* Stage A intentionally initializes no Horizon services.
 * Hardware acceptance criterion: Atmosphere reaches HOME with this
 * boot2 sysmodule present.
 */

u32 __nx_applet_type = AppletType_None;

void __libnx_initheap(void)
{
    static unsigned char heap[0x10000];
    extern void* fake_heap_start;
    extern void* fake_heap_end;
    fake_heap_start = heap;
    fake_heap_end = heap + sizeof(heap);
}

void __appInit(void) {}
void __appExit(void) {}

int main(int argc, char** argv)
{
    (void)argc;
    (void)argv;

    for (;;) {
        svcSleepThread(1000000000LL);
    }

    return 0;
}
