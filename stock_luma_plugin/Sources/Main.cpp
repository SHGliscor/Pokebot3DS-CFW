#include <3ds.h>
#include <CTRPluginFramework.hpp>

#include <arpa/inet.h>
#include <malloc.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <algorithm>
#include <cstring>

using namespace CTRPluginFramework;

namespace PokebotBridge
{
    static constexpr u16 kPort = 4952;
    static constexpr u32 kReqMagic = 0x5242524F;
    static constexpr u32 kRespMagic = 0x5342524F;
    static constexpr u16 kVersion = 1;
    static constexpr u32 kMaxRead = 0x200;
    static constexpr u32 kNeutralHid = 0x00000FFF;
    static constexpr u32 kMaxHoldMs = 5000;
    static constexpr u32 kMaxSettleMs = 5000;

    static constexpr u64 kOmegaRubyTitle = 0x000400000011C400ULL;
    static constexpr u64 kAlphaSapphireTitle = 0x000400000011C500ULL;

    enum Command : u16
    {
        CMD_PING = 1,
        CMD_GAME_INFO = 2,
        CMD_QUERY = 3,
        CMD_READ = 4,
        CMD_INPUT_PING = 5,
        CMD_INPUT_PULSE = 6,
        CMD_INPUT_STATUS = 7,
        CMD_RELEASE_ALL = 8,
        CMD_INPUT_TOUCH_PULSE = 9,
        CMD_INPUT_HID_LATCH = 10,
    };

    enum Status : u16
    {
        STATUS_OK = 0,
        STATUS_BAD_MAGIC = 1,
        STATUS_BAD_VERSION = 2,
        STATUS_BAD_COMMAND = 3,
        STATUS_GAME_NOT_FOUND = 4,
        STATUS_OPEN_FAILED = 5,
        STATUS_QUERY_FAILED = 6,
        STATUS_NOT_READABLE = 7,
        STATUS_RANGE_INVALID = 8,
        STATUS_LENGTH_INVALID = 9,
        STATUS_MAP_FAILED = 10,
        STATUS_INTERNAL = 11,
        STATUS_INPUT_INVALID = 12,
        STATUS_INPUT_BUSY = 13,
        STATUS_INPUT_LEGACY_ACTIVE = 14,
        STATUS_INPUT_PATCH_FAILED = 15,
    };

    enum InputStateCode : u32
    {
        INPUT_IDLE = 0,
        INPUT_ACCEPTED = 1,
        INPUT_IN_PROGRESS = 2,
        INPUT_COMPLETED = 3,
        INPUT_ALREADY_COMPLETED = 4,
        INPUT_ABORTED = 5,
        INPUT_NOT_FOUND = 6,
    };

    enum InputKind : u32
    {
        INPUT_KIND_NONE = 0,
        INPUT_KIND_HID_PULSE = 1,
        INPUT_KIND_TOUCH_PULSE = 2,
        INPUT_KIND_HID_LATCH = 3,
    };

    enum InputCaps : u32
    {
        INPUT_CAP_HID_PULSE = 1u << 0,
        INPUT_CAP_STATUS = 1u << 1,
        INPUT_CAP_SEQUENCE_DEDUPE = 1u << 2,
        INPUT_CAP_RELEASE_ALL = 1u << 3,
        INPUT_CAP_TOUCH_PULSE = 1u << 6,
        INPUT_CAP_HID_LATCH = 1u << 7,
    };

    static constexpr u32 kInputCaps =
        INPUT_CAP_HID_PULSE |
        INPUT_CAP_STATUS |
        INPUT_CAP_SEQUENCE_DEDUPE |
        INPUT_CAP_RELEASE_ALL |
        INPUT_CAP_TOUCH_PULSE |
        INPUT_CAP_HID_LATCH;

#pragma pack(push, 1)
    struct Request
    {
        u32 magic;
        u16 version;
        u16 command;
        u32 requestId;
        u32 argument;
        u32 aux;
    };

    struct Response
    {
        u32 magic;
        u16 version;
        u16 status;
        u32 requestId;
        u32 argument;
        s32 result;
        u32 payloadLength;
    };

    struct GameInfoPayload
    {
        u64 titleId;
        u32 processId;
        char processName[8];
        u32 flags;
    };

    struct QueryPayload
    {
        u32 base;
        u32 size;
        u32 perm;
        u32 state;
        u32 pageFlags;
    };

    struct InputCapsPayload
    {
        u32 protocol;
        u32 caps;
        u32 runtimeFlags;
        u32 neutralHid;
        u32 maxHoldMs;
        u32 maxSettleMs;
    };

    struct InputStatusPayload
    {
        u32 sequence;
        u32 state;
        u32 rawHid;
        u32 remainingMs;
        u32 runtimeFlags;
    };
#pragma pack(pop)

    struct ActiveInput
    {
        InputKind kind{INPUT_KIND_NONE};
        u32 sequence{0};
        u32 state{INPUT_IDLE};
        u32 requestedRawHid{kNeutralHid};
        u32 keyMask{0};
        u16 touchX{0};
        u16 touchY{0};
        u32 holdMs{0};
        u32 settleMs{0};
        u64 startedMs{0};
    };

    static LightLock gInputLock;
    static ActiveInput gInput;
    static u32 gLastCompletedSequence = 0;
    static int gSocket = -1;
    static Thread gServerThread = nullptr;
    static volatile bool gRunning = false;
    static u32 *gSocBuffer = nullptr;
    static constexpr size_t kSocBufferSize = 0x100000;

    static u32 RemainingMsLocked(u64 now)
    {
        if (gInput.kind == INPUT_KIND_NONE)
            return 0;
        if (gInput.kind == INPUT_KIND_HID_LATCH)
            return 0xFFFFFFFFu;

        const u64 total = static_cast<u64>(gInput.holdMs) + gInput.settleMs;
        const u64 elapsed = now > gInput.startedMs ? (now - gInput.startedMs) : 0;
        return elapsed >= total ? 0 : static_cast<u32>(total - elapsed);
    }

    static InputStatusPayload SnapshotInputStatus(u32 requestedSequence = 0)
    {
        LightLock_Lock(&gInputLock);
        InputStatusPayload out{};

        if (gInput.kind != INPUT_KIND_NONE &&
            (requestedSequence == 0 || requestedSequence == gInput.sequence))
        {
            out.sequence = gInput.sequence;
            out.state = gInput.state;
            out.rawHid =
                (gInput.kind == INPUT_KIND_HID_PULSE || gInput.kind == INPUT_KIND_HID_LATCH)
                    ? gInput.requestedRawHid
                    : kNeutralHid;

            if (gInput.kind == INPUT_KIND_HID_PULSE)
            {
                const u64 elapsed = osGetTime() - gInput.startedMs;
                if (elapsed >= gInput.holdMs)
                    out.rawHid = kNeutralHid;
            }

            out.remainingMs = RemainingMsLocked(osGetTime());
            out.runtimeFlags = 0;
        }
        else if (requestedSequence != 0 && requestedSequence == gLastCompletedSequence)
        {
            out.sequence = requestedSequence;
            out.state = INPUT_ALREADY_COMPLETED;
            out.rawHid = kNeutralHid;
            out.remainingMs = 0;
            out.runtimeFlags = 0;
        }
        else if (requestedSequence != 0)
        {
            out.sequence = requestedSequence;
            out.state = INPUT_NOT_FOUND;
            out.rawHid = kNeutralHid;
            out.remainingMs = 0;
            out.runtimeFlags = 0;
        }
        else
        {
            out.sequence = 0;
            out.state = INPUT_IDLE;
            out.rawHid = kNeutralHid;
            out.remainingMs = 0;
            out.runtimeFlags = 0;
        }

        LightLock_Unlock(&gInputLock);
        return out;
    }

    static void CompleteInputLocked()
    {
        if (gInput.sequence != 0)
            gLastCompletedSequence = gInput.sequence;
        gInput = ActiveInput{};
    }

    static bool IsSupportedTitle(u64 title)
    {
        return title == kOmegaRubyTitle || title == kAlphaSapphireTitle;
    }

    static const char *ProcessNameForTitle(u64 title)
    {
        if (title == kOmegaRubyTitle)
            return "sango-1";
        if (title == kAlphaSapphireTitle)
            return "sango-2";
        return "unknown";
    }

    static bool QueryMemory(u32 address, QueryPayload &out)
    {
        MemInfo info{};
        PageInfo page{};
        Result rc = svcQueryMemory(&info, &page, address);
        if (R_FAILED(rc))
            return false;

        out.base = info.base_addr;
        out.size = info.size;
        out.perm = info.perm;
        out.state = info.state;
        out.pageFlags = page.flags;
        return true;
    }

    static bool ReadMemory(u32 address, void *dst, u32 length, Status &error)
    {
        if (length == 0 || length > kMaxRead)
        {
            error = STATUS_LENGTH_INVALID;
            return false;
        }

        const u64 end = static_cast<u64>(address) + static_cast<u64>(length);
        if (end > 0x100000000ULL)
        {
            error = STATUS_RANGE_INVALID;
            return false;
        }

        QueryPayload q{};
        if (!QueryMemory(address, q))
        {
            error = STATUS_QUERY_FAILED;
            return false;
        }

        const u64 regionEnd = static_cast<u64>(q.base) + static_cast<u64>(q.size);
        if (address < q.base || end > regionEnd)
        {
            error = STATUS_RANGE_INVALID;
            return false;
        }

        if ((q.perm & MEMPERM_READ) == 0)
        {
            error = STATUS_NOT_READABLE;
            return false;
        }

        std::memcpy(dst, reinterpret_cast<const void *>(address), length);
        error = STATUS_OK;
        return true;
    }

    static void SendResponse(int sock, const sockaddr_in &remote, socklen_t remoteLen,
                             const Request &req, Status status, s32 result = 0,
                             const void *payload = nullptr, u32 payloadLength = 0)
    {
        u8 buffer[sizeof(Response) + kMaxRead + 64]{};
        Response resp{};
        resp.magic = kRespMagic;
        resp.version = kVersion;
        resp.status = status;
        resp.requestId = req.requestId;
        resp.argument = req.argument;
        resp.result = result;
        resp.payloadLength = payloadLength;

        std::memcpy(buffer, &resp, sizeof(resp));
        if (payload != nullptr && payloadLength != 0)
            std::memcpy(buffer + sizeof(resp), payload, payloadLength);

        sendto(sock, buffer, sizeof(resp) + payloadLength, 0,
               reinterpret_cast<const sockaddr *>(&remote), remoteLen);
    }

    static bool DecodeTouch(u32 touchState, u16 &x, u16 &y)
    {
        if ((touchState & (1u << 24)) == 0)
            return false;

        const u32 rawX = touchState & 0xFFFu;
        const u32 rawY = (touchState >> 12) & 0xFFFu;
        x = static_cast<u16>(std::min<u32>(319, (rawX * 320u + 2047u) / 4095u));
        y = static_cast<u16>(std::min<u32>(239, (rawY * 240u + 2047u) / 4095u));
        return true;
    }

    static Status StartInput(const Request &req, InputKind kind, InputStatusPayload &reply)
    {
        const u32 holdMs = req.aux & 0xFFFFu;
        const u32 settleMs = (req.aux >> 16) & 0xFFFFu;

        if (kind != INPUT_KIND_HID_LATCH &&
            (holdMs > kMaxHoldMs || settleMs > kMaxSettleMs))
            return STATUS_INPUT_INVALID;

        LightLock_Lock(&gInputLock);

        if (gInput.kind != INPUT_KIND_NONE)
        {
            if (req.requestId == gInput.sequence)
            {
                reply.sequence = gInput.sequence;
                reply.state = gInput.state;
                reply.rawHid =
                    (gInput.kind == INPUT_KIND_HID_PULSE || gInput.kind == INPUT_KIND_HID_LATCH)
                        ? gInput.requestedRawHid : kNeutralHid;
                reply.remainingMs = RemainingMsLocked(osGetTime());
                reply.runtimeFlags = 0;
                LightLock_Unlock(&gInputLock);
                return STATUS_OK;
            }

            LightLock_Unlock(&gInputLock);
            return STATUS_INPUT_BUSY;
        }

        if (req.requestId != 0 && req.requestId == gLastCompletedSequence)
        {
            reply.sequence = req.requestId;
            reply.state = INPUT_ALREADY_COMPLETED;
            reply.rawHid = kNeutralHid;
            reply.remainingMs = 0;
            reply.runtimeFlags = 0;
            LightLock_Unlock(&gInputLock);
            return STATUS_OK;
        }

        ActiveInput next{};
        next.kind = kind;
        next.sequence = req.requestId;
        next.state = INPUT_ACCEPTED;
        next.startedMs = osGetTime();

        if (kind == INPUT_KIND_HID_PULSE || kind == INPUT_KIND_HID_LATCH)
        {
            if ((req.argument & ~kNeutralHid) != 0)
            {
                LightLock_Unlock(&gInputLock);
                return STATUS_INPUT_INVALID;
            }
            next.requestedRawHid = req.argument & kNeutralHid;
            next.keyMask = (~next.requestedRawHid) & kNeutralHid;
            next.holdMs = kind == INPUT_KIND_HID_LATCH ? 0 : holdMs;
            next.settleMs = kind == INPUT_KIND_HID_LATCH ? 0 : settleMs;
        }
        else
        {
            if (!DecodeTouch(req.argument, next.touchX, next.touchY))
            {
                LightLock_Unlock(&gInputLock);
                return STATUS_INPUT_INVALID;
            }
            next.requestedRawHid = kNeutralHid;
            next.holdMs = holdMs;
            next.settleMs = settleMs;
        }

        gInput = next;
        reply.sequence = gInput.sequence;
        reply.state = gInput.state;
        reply.rawHid =
            (kind == INPUT_KIND_HID_PULSE || kind == INPUT_KIND_HID_LATCH)
                ? gInput.requestedRawHid : kNeutralHid;
        reply.remainingMs = kind == INPUT_KIND_HID_LATCH ? 0xFFFFFFFFu : holdMs + settleMs;
        reply.runtimeFlags = 0;
        LightLock_Unlock(&gInputLock);
        return STATUS_OK;
    }

    static void HandleRequest(int sock, const sockaddr_in &remote, socklen_t remoteLen,
                              const Request &req)
    {
        if (req.magic != kReqMagic)
        {
            SendResponse(sock, remote, remoteLen, req, STATUS_BAD_MAGIC);
            return;
        }
        if (req.version != kVersion)
        {
            SendResponse(sock, remote, remoteLen, req, STATUS_BAD_VERSION);
            return;
        }

        const u64 title = Process::GetTitleID();
        if (!IsSupportedTitle(title) && req.command != CMD_PING)
        {
            SendResponse(sock, remote, remoteLen, req, STATUS_GAME_NOT_FOUND);
            return;
        }

        switch (req.command)
        {
            case CMD_PING:
            {
                static const char payload[] = "Pokebot3DS-3GX-v0p1";
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0,
                             payload, sizeof(payload) - 1);
                return;
            }
            case CMD_GAME_INFO:
            {
                GameInfoPayload info{};
                info.titleId = title;
                info.processId = Process::GetProcessID();
                std::strncpy(info.processName, ProcessNameForTitle(title), sizeof(info.processName));
                info.flags = 0x00030001u;
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &info, sizeof(info));
                return;
            }
            case CMD_QUERY:
            {
                QueryPayload q{};
                if (!QueryMemory(req.argument, q))
                {
                    SendResponse(sock, remote, remoteLen, req, STATUS_QUERY_FAILED, -1);
                    return;
                }
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &q, sizeof(q));
                return;
            }
            case CMD_READ:
            {
                u8 data[kMaxRead]{};
                Status error = STATUS_OK;
                if (!ReadMemory(req.argument, data, req.aux, error))
                {
                    SendResponse(sock, remote, remoteLen, req, error, -1);
                    return;
                }
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, data, req.aux);
                return;
            }
            case CMD_INPUT_PING:
            {
                InputCapsPayload caps{};
                caps.protocol = 1;
                caps.caps = kInputCaps;
                caps.runtimeFlags = 0;
                caps.neutralHid = kNeutralHid;
                caps.maxHoldMs = kMaxHoldMs;
                caps.maxSettleMs = kMaxSettleMs;
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &caps, sizeof(caps));
                return;
            }
            case CMD_INPUT_PULSE:
            case CMD_INPUT_TOUCH_PULSE:
            case CMD_INPUT_HID_LATCH:
            {
                InputStatusPayload input{};
                const InputKind kind =
                    req.command == CMD_INPUT_PULSE ? INPUT_KIND_HID_PULSE :
                    req.command == CMD_INPUT_TOUCH_PULSE ? INPUT_KIND_TOUCH_PULSE :
                    INPUT_KIND_HID_LATCH;
                const Status status = StartInput(req, kind, input);
                SendResponse(sock, remote, remoteLen, req, status,
                             status == STATUS_OK ? 0 : -1,
                             status == STATUS_OK ? &input : nullptr,
                             status == STATUS_OK ? sizeof(input) : 0);
                return;
            }
            case CMD_INPUT_STATUS:
            {
                const InputStatusPayload input = SnapshotInputStatus(req.argument);
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &input, sizeof(input));
                return;
            }
            case CMD_RELEASE_ALL:
            {
                InputStatusPayload input{};
                LightLock_Lock(&gInputLock);
                if (gInput.sequence != 0)
                    gLastCompletedSequence = gInput.sequence;
                input.sequence = gInput.sequence;
                input.state = INPUT_COMPLETED;
                input.rawHid = kNeutralHid;
                gInput = ActiveInput{};
                LightLock_Unlock(&gInputLock);
                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &input, sizeof(input));
                return;
            }
            default:
                SendResponse(sock, remote, remoteLen, req, STATUS_BAD_COMMAND, -1);
                return;
        }
    }

    static void ServerThreadMain(void *)
    {
        gSocBuffer = static_cast<u32 *>(memalign(0x1000, kSocBufferSize));
        if (gSocBuffer == nullptr)
        {
            OSD::Notify("Pokebot3DS 3GX: SOC buffer allocation failed");
            gRunning = false;
            return;
        }

        if (R_FAILED(socInit(gSocBuffer, kSocBufferSize)))
        {
            OSD::Notify("Pokebot3DS 3GX: socInit failed");
            free(gSocBuffer);
            gSocBuffer = nullptr;
            gRunning = false;
            return;
        }

        gSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (gSocket < 0)
        {
            OSD::Notify("Pokebot3DS 3GX: UDP socket failed");
            socExit();
            free(gSocBuffer);
            gSocBuffer = nullptr;
            gRunning = false;
            return;
        }

        sockaddr_in local{};
        local.sin_family = AF_INET;
        local.sin_port = htons(kPort);
        local.sin_addr.s_addr = htonl(INADDR_ANY);

        if (bind(gSocket, reinterpret_cast<sockaddr *>(&local), sizeof(local)) < 0)
        {
            OSD::Notify("Pokebot3DS 3GX: UDP 4952 bind failed");
            close(gSocket);
            gSocket = -1;
            socExit();
            free(gSocBuffer);
            gSocBuffer = nullptr;
            gRunning = false;
            return;
        }

        timeval timeout{};
        timeout.tv_usec = 250000;
        setsockopt(gSocket, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
        OSD::Notify("Pokebot3DS 3GX: UDP 4952 ready");

        while (gRunning)
        {
            Request req{};
            sockaddr_in remote{};
            socklen_t remoteLen = sizeof(remote);
            const int received = recvfrom(gSocket, &req, sizeof(req), 0,
                                          reinterpret_cast<sockaddr *>(&remote), &remoteLen);
            if (received < 0)
                continue;
            if (received != static_cast<int>(sizeof(req)))
                continue;
            HandleRequest(gSocket, remote, remoteLen, req);
        }

        if (gSocket >= 0)
        {
            close(gSocket);
            gSocket = -1;
        }
        socExit();
        if (gSocBuffer != nullptr)
        {
            free(gSocBuffer);
            gSocBuffer = nullptr;
        }
    }

    static bool Start()
    {
        if (gRunning)
            return true;
        LightLock_Init(&gInputLock);
        gInput = ActiveInput{};
        gLastCompletedSequence = 0;
        gRunning = true;
        gServerThread = threadCreate(ServerThreadMain, nullptr, 0x6000, 0x30, -2, false);
        if (gServerThread == nullptr)
        {
            gRunning = false;
            OSD::Notify("Pokebot3DS 3GX: bridge thread failed");
            return false;
        }
        return true;
    }

    static void Stop()
    {
        if (!gRunning && gServerThread == nullptr)
            return;
        gRunning = false;
        LightLock_Lock(&gInputLock);
        gInput = ActiveInput{};
        LightLock_Unlock(&gInputLock);
        if (gSocket >= 0)
            shutdown(gSocket, SHUT_RDWR);
        if (gServerThread != nullptr)
        {
            threadJoin(gServerThread, U64_MAX);
            threadFree(gServerThread);
            gServerThread = nullptr;
        }
    }

    static void FrameTick()
    {
        LightLock_Lock(&gInputLock);
        if (gInput.kind == INPUT_KIND_NONE)
        {
            LightLock_Unlock(&gInputLock);
            return;
        }

        const u64 now = osGetTime();
        if (gInput.kind == INPUT_KIND_HID_LATCH)
        {
            gInput.state = INPUT_IN_PROGRESS;
            const u32 keys = gInput.keyMask;
            LightLock_Unlock(&gInputLock);
            if (keys != 0)
                Controller::InjectKey(keys);
            return;
        }

        const u64 elapsed = now >= gInput.startedMs ? now - gInput.startedMs : 0;
        if (elapsed < gInput.holdMs)
        {
            gInput.state = INPUT_IN_PROGRESS;
            const InputKind kind = gInput.kind;
            const u32 keys = gInput.keyMask;
            const u16 x = gInput.touchX;
            const u16 y = gInput.touchY;
            LightLock_Unlock(&gInputLock);
            if (kind == INPUT_KIND_HID_PULSE && keys != 0)
                Controller::InjectKey(keys);
            else if (kind == INPUT_KIND_TOUCH_PULSE)
                Controller::InjectTouch(x, y);
            return;
        }

        if (elapsed < static_cast<u64>(gInput.holdMs) + gInput.settleMs)
        {
            gInput.state = INPUT_IN_PROGRESS;
            LightLock_Unlock(&gInputLock);
            return;
        }

        CompleteInputLocked();
        LightLock_Unlock(&gInputLock);
    }
}

namespace CTRPluginFramework
{
    void PatchProcess(FwkSettings &settings)
    {
        (void)settings;
        // Deliberately no hidInit(), no HID service takeover and no game RAM patches.
    }

    void OnProcessExit(void)
    {
        PokebotBridge::Stop();
    }

    int main(void)
    {
        const u64 title = Process::GetTitleID();
        if (title != PokebotBridge::kOmegaRubyTitle &&
            title != PokebotBridge::kAlphaSapphireTitle)
        {
            OSD::Notify("Pokebot3DS 3GX: unsupported title");
            Process::WaitForExit();
            return 0;
        }

        PokebotBridge::Start();
        PluginMenu *menu = new PluginMenu(
            "Pokebot3DS Bridge", 0, 1, 0,
            "Stock-Luma bridge proof. UDP 4952 read-only RAM and acknowledged additive input. Physical game HID remains the normal owner.");
        menu->ShowWelcomeMessage(false);
        menu->SynchronizeWithFrame(true);
        menu->Callback(PokebotBridge::FrameTick);
        menu->Run();
        PokebotBridge::Stop();
        delete menu;
        return 0;
    }
}
