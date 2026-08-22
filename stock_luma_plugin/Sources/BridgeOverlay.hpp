#pragma once

#include <3ds.h>
#include <CTRPluginFramework.hpp>

#include <cstdio>
#include <cstring>
#include <string>

namespace BridgeOverlay
{
    using namespace CTRPluginFramework;

    enum ActionKind : u32
    {
        ACTION_NONE = 0,
        ACTION_PULSE = 1,
        ACTION_TOUCH = 2,
        ACTION_LATCH = 3,
        ACTION_RELEASE = 4,
    };

    struct Snapshot
    {
        u64 lastPacketMs;
        u64 lastReadMs;
        u64 actionStartedMs;
        u32 packetCount;
        u32 readCount;
        u32 lastReadAddress;
        u32 lastReadLength;
        u32 lastSequence;
        u32 actionTotalMs;
        u32 actionKind;
        u16 lastCommand;
        u16 lastError;
        char lastAction[40];
    };

    static LightLock sLock;
    static bool sInitialised = false;
    static u64 sLastPacketMs = 0;
    static u64 sLastReadMs = 0;
    static u64 sActionStartedMs = 0;
    static u32 sPacketCount = 0;
    static u32 sReadCount = 0;
    static u32 sLastReadAddress = 0;
    static u32 sLastReadLength = 0;
    static u32 sLastSequence = 0;
    static u32 sActionTotalMs = 0;
    static u32 sActionKind = ACTION_NONE;
    static u16 sLastCommand = 0;
    static u16 sLastError = 0;
    static char sLastAction[40] = "---";

    static void Init()
    {
        if (sInitialised)
            return;

        LightLock_Init(&sLock);
        sInitialised = true;
    }

    static void SafeCopy(char *dst, size_t dstSize, const char *src)
    {
        if (dst == nullptr || dstSize == 0)
            return;
        std::snprintf(dst, dstSize, "%s", src == nullptr ? "---" : src);
    }

    static void DecodeHid(u32 rawHid, char *dst, size_t dstSize)
    {
        static const char *kNames[12] = {
            "A", "B", "SELECT", "START",
            "RIGHT", "LEFT", "UP", "DOWN",
            "R", "L", "X", "Y"
        };

        if (dst == nullptr || dstSize == 0)
            return;

        dst[0] = '\0';
        const u32 pressed = (~rawHid) & 0x0FFFu;
        if (pressed == 0)
        {
            SafeCopy(dst, dstSize, "NEUTRAL");
            return;
        }

        size_t used = 0;
        for (u32 bit = 0; bit < 12; ++bit)
        {
            if ((pressed & (1u << bit)) == 0)
                continue;

            const char *name = kNames[bit];
            const int written = std::snprintf(
                dst + used,
                used < dstSize ? dstSize - used : 0,
                "%s%s",
                used == 0 ? "" : "+",
                name);

            if (written <= 0)
                break;

            used += static_cast<size_t>(written);
            if (used >= dstSize - 1)
                break;
        }
    }

    static void DecodeTouch(u32 touchState, u16 &x, u16 &y)
    {
        const u32 rawX = touchState & 0xFFFu;
        const u32 rawY = (touchState >> 12) & 0xFFFu;
        x = static_cast<u16>((rawX * 320u + 2047u) / 4095u);
        y = static_cast<u16>((rawY * 240u + 2047u) / 4095u);
        if (x > 319) x = 319;
        if (y > 239) y = 239;
    }

    static void RecordPacket(u16 command)
    {
        if (!sInitialised)
            return;

        LightLock_Lock(&sLock);
        ++sPacketCount;
        sLastPacketMs = osGetTime();
        sLastCommand = command;
        LightLock_Unlock(&sLock);
    }

    static void RecordStatus(u16 status)
    {
        if (!sInitialised || status == 0)
            return;

        LightLock_Lock(&sLock);
        sLastError = status;
        LightLock_Unlock(&sLock);
    }

    static void RecordRead(u32 address, u32 length)
    {
        if (!sInitialised)
            return;

        LightLock_Lock(&sLock);
        ++sReadCount;
        sLastReadMs = osGetTime();
        sLastReadAddress = address;
        sLastReadLength = length;
        LightLock_Unlock(&sLock);
    }

    static void RecordInput(u16 command, u32 argument, u32 aux, u32 sequence, u16 status)
    {
        if (!sInitialised || status != 0)
            return;

        char action[40]{};
        u32 kind = ACTION_NONE;
        u32 totalMs = 0;

        if (command == 6)
        {
            DecodeHid(argument, action, sizeof(action));
            kind = ACTION_PULSE;
            totalMs = (aux & 0xFFFFu) + ((aux >> 16) & 0xFFFFu);
        }
        else if (command == 9)
        {
            u16 x = 0;
            u16 y = 0;
            DecodeTouch(argument, x, y);
            std::snprintf(action, sizeof(action), "TOUCH %u,%u", x, y);
            kind = ACTION_TOUCH;
            totalMs = (aux & 0xFFFFu) + ((aux >> 16) & 0xFFFFu);
        }
        else if (command == 10)
        {
            char buttons[28]{};
            DecodeHid(argument, buttons, sizeof(buttons));
            std::snprintf(action, sizeof(action), "LATCH %s", buttons);
            kind = ACTION_LATCH;
            totalMs = 0;
        }
        else
        {
            std::snprintf(action, sizeof(action), "CMD %u", command);
        }

        LightLock_Lock(&sLock);
        SafeCopy(sLastAction, sizeof(sLastAction), action);
        sLastSequence = sequence;
        sActionStartedMs = osGetTime();
        sActionTotalMs = totalMs;
        sActionKind = kind;
        LightLock_Unlock(&sLock);
    }

    static void RecordRelease(u32 sequence)
    {
        if (!sInitialised)
            return;

        LightLock_Lock(&sLock);
        SafeCopy(sLastAction, sizeof(sLastAction), "RELEASE_ALL");
        sLastSequence = sequence;
        sActionStartedMs = osGetTime();
        sActionTotalMs = 0;
        sActionKind = ACTION_RELEASE;
        LightLock_Unlock(&sLock);
    }

    static Snapshot GetSnapshot()
    {
        Snapshot out{};
        SafeCopy(out.lastAction, sizeof(out.lastAction), "---");

        if (!sInitialised)
            return out;

        LightLock_Lock(&sLock);
        out.lastPacketMs = sLastPacketMs;
        out.lastReadMs = sLastReadMs;
        out.actionStartedMs = sActionStartedMs;
        out.packetCount = sPacketCount;
        out.readCount = sReadCount;
        out.lastReadAddress = sLastReadAddress;
        out.lastReadLength = sLastReadLength;
        out.lastSequence = sLastSequence;
        out.actionTotalMs = sActionTotalMs;
        out.actionKind = sActionKind;
        out.lastCommand = sLastCommand;
        out.lastError = sLastError;
        SafeCopy(out.lastAction, sizeof(out.lastAction), sLastAction);
        LightLock_Unlock(&sLock);
        return out;
    }

    static const char *ActionState(const Snapshot &s, u64 now)
    {
        if (s.actionKind == ACTION_NONE)
            return "IDLE";
        if (s.actionKind == ACTION_LATCH)
            return "ACTIVE";
        if (s.actionKind == ACTION_RELEASE)
            return "COMPLETED";

        const u64 elapsed = now >= s.actionStartedMs ? now - s.actionStartedMs : 0;
        return elapsed < s.actionTotalMs ? "IN PROGRESS" : "COMPLETED";
    }

    static const char *CommandName(u16 command)
    {
        switch (command)
        {
            case 1: return "PING";
            case 2: return "GAME_INFO";
            case 3: return "QUERY";
            case 4: return "READ";
            case 5: return "INPUT_PING";
            case 6: return "INPUT_PULSE";
            case 7: return "INPUT_STATUS";
            case 8: return "RELEASE_ALL";
            case 9: return "TOUCH_PULSE";
            case 10: return "HID_LATCH";
            default: return "---";
        }
    }

    static bool Draw(const Screen &screen)
    {
        if (!screen.IsTop)
            return false;

        const Snapshot s = GetSnapshot();
        const u64 now = osGetTime();
        const bool pcConnected = s.lastPacketMs != 0 && (now - s.lastPacketMs) <= 5000;

        char line[96]{};
        u32 y = 4;

        y = screen.Draw("Pokebot Bridge v0p2", 4, y);

        std::snprintf(line, sizeof(line), "PC: %s  UDP:4952", pcConnected ? "CONNECTED" : "WAITING");
        y = screen.Draw(line, 4, y);

        if (s.readCount != 0)
            std::snprintf(line, sizeof(line), "RAM: READ OK  Reads:%lu", static_cast<unsigned long>(s.readCount));
        else
            std::snprintf(line, sizeof(line), "RAM: READY  Reads:0");
        y = screen.Draw(line, 4, y);

        y = screen.Draw("HID: READY  Physical: PASSTHROUGH", 4, y);

        std::snprintf(line, sizeof(line), "Last: %s", s.lastAction);
        y = screen.Draw(line, 4, y);

        std::snprintf(line, sizeof(line), "Seq:%lu  State:%s", static_cast<unsigned long>(s.lastSequence), ActionState(s, now));
        y = screen.Draw(line, 4, y);

        std::snprintf(line, sizeof(line), "Cmd:%s  Packets:%lu", CommandName(s.lastCommand), static_cast<unsigned long>(s.packetCount));
        y = screen.Draw(line, 4, y);

        if (s.lastError != 0)
        {
            std::snprintf(line, sizeof(line), "Last error: %u", s.lastError);
            screen.Draw(line, 4, y);
        }

        return true;
    }
}
