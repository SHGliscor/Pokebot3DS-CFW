// SPDX-License-Identifier: GPL-3.0-or-later
#include "PokebotBridge.h"

#include <switch.h>

#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <unistd.h>

#include <atomic>
#include <cerrno>
#include <cctype>
#include <cstdio>
#include <cstdlib>
#include <cstring>

#include "NDS.h"

namespace PokebotBridge
{
namespace
{
constexpr const char* BridgeTag = "POKEBOT_MELONDS_BRIDGE_V0P1";
constexpr u32 MainRamStart = 0x02000000;
constexpr u32 MainRamEndExclusive = 0x02400000;
constexpr u32 MaxReadLength = 512;
constexpr size_t ResponseCapacity = 4096;

enum class CommandType : int
{
    None = 0,
    Read9,
    Info,
    Press,
    Keys,
    Release,
};

enum class CommandState : int
{
    Idle = 0,
    Pending,
    Done,
};

struct Command
{
    CommandType Type = CommandType::None;
    u32 Address = 0;
    u32 Length = 0;
    u32 KeyMask = 0;
    u32 Frames = 0;
    char Response[ResponseCapacity]{};
};

Thread ServerThread{};
bool ThreadCreated = false;
std::atomic<bool> Running{false};
std::atomic<int> ListenSocket{-1};
std::atomic<int> ClientSocket{-1};
std::atomic<CommandState> State{CommandState::Idle};
Command PendingCommand{};

u32 RemotePressedMask = 0;
u32 RemoteFramesRemaining = 0;

bool SendAll(int fd, const char* data, size_t len)
{
    while (len > 0)
    {
        ssize_t sent = send(fd, data, len, 0);
        if (sent <= 0)
            return false;
        data += sent;
        len -= static_cast<size_t>(sent);
    }
    return true;
}

bool SendLine(int fd, const char* line)
{
    return SendAll(fd, line, std::strlen(line));
}

void Uppercase(char* text)
{
    for (; *text; ++text)
        *text = static_cast<char>(std::toupper(static_cast<unsigned char>(*text)));
}

bool ParseU32(const char* text, u32& value, int base)
{
    if (!text || !*text)
        return false;

    errno = 0;
    char* end = nullptr;
    unsigned long parsed = std::strtoul(text, &end, base);
    if (errno != 0 || end == text || *end != '\0' || parsed > 0xFFFFFFFFUL)
        return false;

    value = static_cast<u32>(parsed);
    return true;
}

bool KeyNameToMask(const char* keyName, u32& mask)
{
    char key[16]{};
    std::snprintf(key, sizeof(key), "%s", keyName ? keyName : "");
    Uppercase(key);

    struct KeyDef { const char* Name; u32 Bit; };
    static constexpr KeyDef Keys[] = {
        {"A",      1u << 0},
        {"B",      1u << 1},
        {"SELECT", 1u << 2},
        {"START",  1u << 3},
        {"RIGHT",  1u << 4},
        {"LEFT",   1u << 5},
        {"UP",     1u << 6},
        {"DOWN",   1u << 7},
        {"R",      1u << 8},
        {"L",      1u << 9},
        {"X",      1u << 10},
        {"Y",      1u << 11},
    };

    for (const auto& def : Keys)
    {
        if (std::strcmp(key, def.Name) == 0)
        {
            mask = def.Bit;
            return true;
        }
    }
    return false;
}

bool SubmitAndWait(const Command& command, char* response, size_t responseCapacity)
{
    if (State.load(std::memory_order_acquire) != CommandState::Idle)
    {
        std::snprintf(response, responseCapacity, "ERR BUSY\n");
        return true;
    }

    PendingCommand = command;
    State.store(CommandState::Pending, std::memory_order_release);

    while (Running.load(std::memory_order_acquire))
    {
        if (State.load(std::memory_order_acquire) == CommandState::Done)
        {
            std::snprintf(response, responseCapacity, "%s", PendingCommand.Response);
            State.store(CommandState::Idle, std::memory_order_release);
            return true;
        }
        svcSleepThread(1000000);
    }

    std::snprintf(response, responseCapacity, "ERR SHUTDOWN\n");
    return false;
}

bool HandleCommandLine(int fd, char* line)
{
    while (*line && std::isspace(static_cast<unsigned char>(*line)))
        ++line;
    if (!*line)
        return true;

    char* save = nullptr;
    char* verb = strtok_r(line, " \t", &save);
    if (!verb)
        return true;
    Uppercase(verb);

    if (std::strcmp(verb, "PING") == 0)
    {
        char response[128];
        std::snprintf(response, sizeof(response), "PONG %s port=%u\n", BridgeTag, Port);
        return SendLine(fd, response);
    }

    if (std::strcmp(verb, "HELP") == 0)
    {
        return SendLine(fd,
            "OK PING | INFO | READ9 <hexaddr> <len> | PRESS <key> [frames] | KEYS <hexmask> [frames] | RELEASE\n");
    }

    Command cmd{};

    if (std::strcmp(verb, "INFO") == 0)
    {
        cmd.Type = CommandType::Info;
    }
    else if (std::strcmp(verb, "READ9") == 0)
    {
        char* addressText = strtok_r(nullptr, " \t", &save);
        char* lengthText = strtok_r(nullptr, " \t", &save);
        u32 address = 0, length = 0;
        if (!ParseU32(addressText, address, 16) || !ParseU32(lengthText, length, 10))
            return SendLine(fd, "ERR USAGE READ9 <hexaddr> <len>\n");
        if (length == 0 || length > MaxReadLength)
            return SendLine(fd, "ERR LENGTH 1..512\n");
        if (address < MainRamStart || address >= MainRamEndExclusive ||
            length > (MainRamEndExclusive - address))
            return SendLine(fd, "ERR RANGE 02000000..023FFFFF\n");

        cmd.Type = CommandType::Read9;
        cmd.Address = address;
        cmd.Length = length;
    }
    else if (std::strcmp(verb, "PRESS") == 0)
    {
        char* keyText = strtok_r(nullptr, " \t", &save);
        char* framesText = strtok_r(nullptr, " \t", &save);
        u32 keyMask = 0;
        u32 frames = 2;
        if (!KeyNameToMask(keyText, keyMask))
            return SendLine(fd, "ERR KEY A B X Y L R START SELECT UP DOWN LEFT RIGHT\n");
        if (framesText && !ParseU32(framesText, frames, 10))
            return SendLine(fd, "ERR FRAMES\n");
        if (frames == 0 || frames > 600)
            return SendLine(fd, "ERR FRAMES 1..600\n");

        cmd.Type = CommandType::Press;
        cmd.KeyMask = keyMask;
        cmd.Frames = frames;
    }
    else if (std::strcmp(verb, "KEYS") == 0)
    {
        char* maskText = strtok_r(nullptr, " \t", &save);
        char* framesText = strtok_r(nullptr, " \t", &save);
        u32 mask = 0;
        u32 frames = 2;
        if (!ParseU32(maskText, mask, 16))
            return SendLine(fd, "ERR USAGE KEYS <hexmask> [frames]\n");
        if (framesText && !ParseU32(framesText, frames, 10))
            return SendLine(fd, "ERR FRAMES\n");
        if ((mask & ~0xFFFu) != 0 || frames == 0 || frames > 600)
            return SendLine(fd, "ERR MASK/FRAMES\n");

        cmd.Type = CommandType::Keys;
        cmd.KeyMask = mask;
        cmd.Frames = frames;
    }
    else if (std::strcmp(verb, "RELEASE") == 0)
    {
        cmd.Type = CommandType::Release;
    }
    else
    {
        return SendLine(fd, "ERR UNKNOWN; send HELP\n");
    }

    char response[ResponseCapacity]{};
    if (!SubmitAndWait(cmd, response, sizeof(response)))
        return false;
    return SendLine(fd, response);
}

void ServeClient(int fd)
{
    char incoming[1024];
    char line[1024];
    size_t lineLength = 0;

    SendLine(fd, "HELLO POKEBOT_MELONDS_BRIDGE_V0P1\n");

    while (Running.load(std::memory_order_acquire))
    {
        ssize_t got = recv(fd, incoming, sizeof(incoming), 0);
        if (got <= 0)
            break;

        for (ssize_t i = 0; i < got; ++i)
        {
            char ch = incoming[i];
            if (ch == '\r')
                continue;
            if (ch == '\n')
            {
                line[lineLength] = '\0';
                if (!HandleCommandLine(fd, line))
                    return;
                lineLength = 0;
                continue;
            }

            if (lineLength + 1 < sizeof(line))
                line[lineLength++] = ch;
            else
            {
                SendLine(fd, "ERR LINE_TOO_LONG\n");
                lineLength = 0;
            }
        }
    }
}

void ServerMain(void*)
{
    int server = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (server < 0)
    {
        std::printf("PokebotBridge: socket() failed: %d\n", errno);
        Running.store(false, std::memory_order_release);
        return;
    }
    ListenSocket.store(server, std::memory_order_release);

    int reuse = 1;
    setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(Port);

    if (bind(server, reinterpret_cast<sockaddr*>(&address), sizeof(address)) < 0)
    {
        std::printf("PokebotBridge: bind(%u) failed: %d\n", Port, errno);
        close(server);
        ListenSocket.store(-1, std::memory_order_release);
        Running.store(false, std::memory_order_release);
        return;
    }

    if (listen(server, 1) < 0)
    {
        std::printf("PokebotBridge: listen() failed: %d\n", errno);
        close(server);
        ListenSocket.store(-1, std::memory_order_release);
        Running.store(false, std::memory_order_release);
        return;
    }

    std::printf("PokebotBridge: listening on TCP %u\n", Port);

    while (Running.load(std::memory_order_acquire))
    {
        sockaddr_in peer{};
        socklen_t peerLength = sizeof(peer);
        int client = accept(server, reinterpret_cast<sockaddr*>(&peer), &peerLength);
        if (client < 0)
        {
            if (!Running.load(std::memory_order_acquire))
                break;
            svcSleepThread(10000000);
            continue;
        }

        ClientSocket.store(client, std::memory_order_release);
        std::printf("PokebotBridge: client connected\n");
        ServeClient(client);
        shutdown(client, SHUT_RDWR);
        close(client);
        ClientSocket.store(-1, std::memory_order_release);
        std::printf("PokebotBridge: client disconnected\n");
    }

    int expected = server;
    ListenSocket.compare_exchange_strong(expected, -1, std::memory_order_acq_rel);
    close(server);
}

} // namespace

bool Init()
{
    if (Running.load(std::memory_order_acquire))
        return true;

    Result rc = socketInitializeDefault();
    if (R_FAILED(rc))
    {
        std::printf("PokebotBridge: socketInitializeDefault failed: 0x%08X\n", rc);
        return false;
    }

    State.store(CommandState::Idle, std::memory_order_release);
    Running.store(true, std::memory_order_release);

    rc = threadCreate(&ServerThread, ServerMain, nullptr, nullptr, 0x10000, 0x2C, -2);
    if (R_FAILED(rc))
    {
        std::printf("PokebotBridge: threadCreate failed: 0x%08X\n", rc);
        Running.store(false, std::memory_order_release);
        socketExit();
        return false;
    }

    ThreadCreated = true;
    threadStart(&ServerThread);
    return true;
}

void DeInit()
{
    if (!ThreadCreated)
        return;

    Running.store(false, std::memory_order_release);

    int client = ClientSocket.load(std::memory_order_acquire);
    if (client >= 0)
        shutdown(client, SHUT_RDWR);

    int server = ListenSocket.load(std::memory_order_acquire);
    if (server >= 0)
        shutdown(server, SHUT_RDWR);

    threadWaitForExit(&ServerThread);
    threadClose(&ServerThread);
    ThreadCreated = false;

    State.store(CommandState::Idle, std::memory_order_release);
    RemotePressedMask = 0;
    RemoteFramesRemaining = 0;
    socketExit();
}

void ApplyFrame(u32& keyMask)
{
    if (State.load(std::memory_order_acquire) == CommandState::Pending)
    {
        switch (PendingCommand.Type)
        {
        case CommandType::Read9:
        {
            size_t pos = static_cast<size_t>(std::snprintf(
                PendingCommand.Response, sizeof(PendingCommand.Response),
                "OK %08X %u ", PendingCommand.Address, PendingCommand.Length));

            static constexpr char Hex[] = "0123456789ABCDEF";
            for (u32 i = 0; i < PendingCommand.Length && pos + 3 < sizeof(PendingCommand.Response); ++i)
            {
                u8 value = NDS::ARM9Read8(PendingCommand.Address + i);
                PendingCommand.Response[pos++] = Hex[value >> 4];
                PendingCommand.Response[pos++] = Hex[value & 0x0F];
            }
            PendingCommand.Response[pos++] = '\n';
            PendingCommand.Response[pos] = '\0';
            break;
        }
        case CommandType::Info:
            std::snprintf(PendingCommand.Response, sizeof(PendingCommand.Response),
                "OK bridge=%s frames=%u console=%s ram_mask=%08X\n",
                BridgeTag, NDS::NumFrames, NDS::ConsoleType == 0 ? "DS" : "DSi", NDS::MainRAMMask);
            break;

        case CommandType::Press:
        case CommandType::Keys:
            RemotePressedMask = PendingCommand.KeyMask & 0xFFFu;
            RemoteFramesRemaining = PendingCommand.Frames;
            std::snprintf(PendingCommand.Response, sizeof(PendingCommand.Response),
                "OK INPUT mask=%03X frames=%u\n", RemotePressedMask, RemoteFramesRemaining);
            break;

        case CommandType::Release:
            RemotePressedMask = 0;
            RemoteFramesRemaining = 0;
            std::snprintf(PendingCommand.Response, sizeof(PendingCommand.Response), "OK RELEASED\n");
            break;

        default:
            std::snprintf(PendingCommand.Response, sizeof(PendingCommand.Response), "ERR INTERNAL\n");
            break;
        }

        State.store(CommandState::Done, std::memory_order_release);
    }

    if (RemoteFramesRemaining > 0)
    {
        keyMask &= ~(RemotePressedMask & 0xFFFu);
        --RemoteFramesRemaining;
        if (RemoteFramesRemaining == 0)
            RemotePressedMask = 0;
    }
}

} // namespace PokebotBridge
