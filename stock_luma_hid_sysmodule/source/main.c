#include <3ds.h>

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <malloc.h>
#include <netinet/in.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PBH_PORT 4953
#define PBH_REQ_MAGIC  0x48534250u
#define PBH_RESP_MAGIC 0x53534250u
#define PBH_VERSION 1u
#define PBH_SOC_SIZE 0x20000u

#define PBH_CMD_PING   1u
#define PBH_CMD_STATUS 2u

#define PBH_STATUS_OK          0u
#define PBH_STATUS_BAD_MAGIC   1u
#define PBH_STATUS_BAD_VERSION 2u
#define PBH_STATUS_BAD_COMMAND 3u

#define PBH_FLAG_HID_READY (1u << 0)
#define PBH_FLAG_UDP_READY (1u << 1)

#pragma pack(push, 1)
typedef struct
{
    u32 magic;
    u16 version;
    u16 command;
    u32 sequence;
} PbhRequest;

typedef struct
{
    u32 magic;
    u16 version;
    u16 status;
    u32 sequence;
    u32 flags;
    u32 keys;
    u32 lastNonZero;
    u32 changes;
    u32 hidIndex;
    s32 hidResult;
    s32 socResult;
    char identity[20];
} PbhResponse;
#pragma pack(pop)

static Handle gHidService = 0;
static Handle gHidMemHandle = 0;
static vu32 *gHidShared = NULL;
static Result gHidResult = (Result)-1;

static u32 *gSocBuffer = NULL;
static int gSocket = -1;
static Result gSocResult = (Result)-1;

static u32 gKeys = 0;
static u32 gLastKeys = 0;
static u32 gLastNonZero = 0;
static u32 gChanges = 0;
static u32 gHidIndex = 0;
static bool gKeysInitialised = false;

void __appInit(void)
{
    srvInit();
}

static void HidObserverExit(void)
{
    if (gHidShared != NULL && gHidMemHandle != 0)
        svcUnmapMemoryBlock(gHidMemHandle, (u32)gHidShared);

    if (gHidShared != NULL)
        mappableFree((void *)gHidShared);

    if (gHidMemHandle != 0)
        svcCloseHandle(gHidMemHandle);

    if (gHidService != 0)
        svcCloseHandle(gHidService);

    gHidShared = NULL;
    gHidMemHandle = 0;
    gHidService = 0;
}

static void NetworkExit(void)
{
    if (gSocket >= 0)
    {
        close(gSocket);
        gSocket = -1;
    }

    if (gSocBuffer != NULL)
    {
        socExit();
        free(gSocBuffer);
        gSocBuffer = NULL;
    }
}

void __appExit(void)
{
    NetworkExit();
    HidObserverExit();
    srvExit();
}

static Result HidGetHandles(Handle service, Handle *memHandle, Handle events[5])
{
    u32 *cmdbuf = getThreadCommandBuffer();
    cmdbuf[0] = IPC_MakeHeader(0xA, 0, 0);

    Result rc = svcSendSyncRequest(service);
    if (R_FAILED(rc))
        return rc;

    rc = (Result)cmdbuf[1];
    if (R_FAILED(rc))
        return rc;

    *memHandle = (Handle)cmdbuf[3];
    for (u32 i = 0; i < 5; ++i)
        events[i] = (Handle)cmdbuf[4 + i];

    return rc;
}

static Result HidObserverInit(void)
{
    HidObserverExit();

    Handle service = 0;
    Result rc = srvGetServiceHandle(&service, "hid:USER");
    if (R_FAILED(rc))
        return rc;

    Handle memHandle = 0;
    Handle events[5] = {0};
    rc = HidGetHandles(service, &memHandle, events);
    if (R_FAILED(rc))
    {
        svcCloseHandle(service);
        return rc;
    }

    for (u32 i = 0; i < 5; ++i)
    {
        if (events[i] != 0)
            svcCloseHandle(events[i]);
    }

    vu32 *mapping = (vu32 *)mappableAlloc(0x1000);
    if (mapping == NULL)
    {
        svcCloseHandle(memHandle);
        svcCloseHandle(service);
        return (Result)-2;
    }

    rc = svcMapMemoryBlock(memHandle, (u32)mapping, MEMPERM_READ, MEMPERM_DONTCARE);
    if (R_FAILED(rc))
    {
        mappableFree((void *)mapping);
        svcCloseHandle(memHandle);
        svcCloseHandle(service);
        return rc;
    }

    gHidService = service;
    gHidMemHandle = memHandle;
    gHidShared = mapping;
    gKeysInitialised = false;
    gChanges = 0;
    gLastNonZero = 0;
    return 0;
}

static void UpdatePhysicalKeys(void)
{
    if (gHidShared == NULL)
        return;

    u32 index = gHidShared[4];
    if (index > 7)
        index = 7;

    const u32 keys = gHidShared[10 + index * 4] & 0x0FFFu;
    gHidIndex = index;
    gKeys = keys;

    if (!gKeysInitialised)
    {
        gLastKeys = keys;
        gKeysInitialised = true;
    }
    else if (keys != gLastKeys)
    {
        ++gChanges;
        gLastKeys = keys;
    }

    if (keys != 0)
        gLastNonZero = keys;
}

static Result NetworkInit(void)
{
    NetworkExit();

    gSocBuffer = (u32 *)memalign(0x1000, PBH_SOC_SIZE);
    if (gSocBuffer == NULL)
        return (Result)-3;

    memset(gSocBuffer, 0, PBH_SOC_SIZE);
    Result rc = socInit(gSocBuffer, PBH_SOC_SIZE);
    if (R_FAILED(rc))
    {
        free(gSocBuffer);
        gSocBuffer = NULL;
        return rc;
    }

    const int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        rc = (Result)(-0x10000 - errno);
        NetworkExit();
        return rc;
    }

    int flags = fcntl(sock, F_GETFL, 0);
    if (flags < 0 || fcntl(sock, F_SETFL, flags | O_NONBLOCK) < 0)
    {
        rc = (Result)(-0x20000 - errno);
        close(sock);
        gSocket = -1;
        socExit();
        free(gSocBuffer);
        gSocBuffer = NULL;
        return rc;
    }

    struct sockaddr_in local;
    memset(&local, 0, sizeof(local));
    local.sin_family = AF_INET;
    local.sin_port = htons(PBH_PORT);
    local.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock, (struct sockaddr *)&local, sizeof(local)) < 0)
    {
        rc = (Result)(-0x30000 - errno);
        close(sock);
        gSocket = -1;
        socExit();
        free(gSocBuffer);
        gSocBuffer = NULL;
        return rc;
    }

    gSocket = sock;
    return 0;
}

static void FillResponse(PbhResponse *resp, const PbhRequest *req, u16 status)
{
    memset(resp, 0, sizeof(*resp));
    resp->magic = PBH_RESP_MAGIC;
    resp->version = PBH_VERSION;
    resp->status = status;
    resp->sequence = req != NULL ? req->sequence : 0;

    if (gHidShared != NULL)
        resp->flags |= PBH_FLAG_HID_READY;
    if (gSocket >= 0)
        resp->flags |= PBH_FLAG_UDP_READY;

    resp->keys = gKeys;
    resp->lastNonZero = gLastNonZero;
    resp->changes = gChanges;
    resp->hidIndex = gHidIndex;
    resp->hidResult = (s32)gHidResult;
    resp->socResult = (s32)gSocResult;
    strncpy(resp->identity, "PokebotHID-v0p1", sizeof(resp->identity) - 1);
}

static void PollUdp(void)
{
    if (gSocket < 0)
        return;

    for (u32 packet = 0; packet < 8; ++packet)
    {
        PbhRequest req;
        struct sockaddr_in remote;
        socklen_t remoteLen = sizeof(remote);
        const int n = recvfrom(gSocket, &req, sizeof(req), 0, (struct sockaddr *)&remote, &remoteLen);

        if (n < 0)
        {
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                return;
            return;
        }

        PbhResponse resp;
        u16 status = PBH_STATUS_OK;

        if (n != (int)sizeof(req) || req.magic != PBH_REQ_MAGIC)
            status = PBH_STATUS_BAD_MAGIC;
        else if (req.version != PBH_VERSION)
            status = PBH_STATUS_BAD_VERSION;
        else if (req.command != PBH_CMD_PING && req.command != PBH_CMD_STATUS)
            status = PBH_STATUS_BAD_COMMAND;

        FillResponse(&resp, &req, status);
        sendto(gSocket, &resp, sizeof(resp), 0, (struct sockaddr *)&remote, remoteLen);
    }
}

int main(int argc, char **argv)
{
    (void)argc;
    (void)argv;

    u64 lastHidAttempt = 0;
    u64 lastSocAttempt = 0;

    while (true)
    {
        const u64 now = osGetTime();

        if (gHidShared == NULL && (lastHidAttempt == 0 || now - lastHidAttempt >= 1000))
        {
            lastHidAttempt = now;
            gHidResult = HidObserverInit();
        }

        if (gSocket < 0 && (lastSocAttempt == 0 || now - lastSocAttempt >= 2000))
        {
            lastSocAttempt = now;
            gSocResult = NetworkInit();
        }

        UpdatePhysicalKeys();
        PollUdp();
        svcSleepThread(10 * 1000 * 1000LL);
    }

    return 0;
}
