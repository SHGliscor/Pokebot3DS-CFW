#!/usr/bin/env python3
from pathlib import Path
import sys

RTC_CODE = r"""
/* ===== Pokebot3DS-CFW mGBA RTC diagnostics ===== */
static unsigned _pb3RtcBcd(unsigned value) {
    return (value % 10) | (((value / 10) % 10) << 4);
}

static bool _pb3RtcLeapYear(unsigned year) {
    return ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0));
}

static uint16_t _pb3RubyRev1RtcSeed(const struct tm* date) {
    /* Match pokeruby v1.1's ConvertDateToDayCount + RtcGetMinuteCount.
     * Ruby/Sapphire before the Berry Glitch fix intentionally omit year 0.
     * RtcGetMinuteCount also uses the raw BCD hour/minute bytes directly.
     */
    unsigned year = date->tm_year >= 100 ? (unsigned) (date->tm_year - 100) : (unsigned) date->tm_year;
    unsigned month = (unsigned) date->tm_mon + 1;
    unsigned day = (unsigned) date->tm_mday;
    static const unsigned daysInMonth[12] = {
        31,28,31,30,31,30,31,31,30,31,30,31
    };

    uint32_t dayCount = 0;
    for (int i = (int) year - 1; i > 0; --i) {
        dayCount += 365;
        if (_pb3RtcLeapYear((unsigned) i)) ++dayCount;
    }
    for (unsigned i = 1; i < month; ++i) {
        dayCount += daysInMonth[i - 1];
    }
    if (month > 2 && _pb3RtcLeapYear(year)) ++dayCount;
    dayCount += day;

    uint32_t minuteCount =
        1440u * dayCount +
        60u * _pb3RtcBcd((unsigned) date->tm_hour) +
        _pb3RtcBcd((unsigned) date->tm_min);

    return (uint16_t) (((minuteCount >> 16) ^ (minuteCount & 0xFFFFu)) & 0xFFFFu);
}

static const char* _pb3RtcTypeName(enum mRTCGenericType type) {
    switch (type) {
    case RTC_NO_OVERRIDE: return "WALLCLOCK";
    case RTC_FIXED: return "FIXED";
    case RTC_FAKE_EPOCH: return "FAKE_EPOCH";
    case RTC_WALLCLOCK_OFFSET: return "WALLCLOCK_OFFSET";
    default: return type >= RTC_CUSTOM_START ? "CUSTOM" : "UNKNOWN";
    }
}

static void _pb3RtcReply(struct mGUIRunner* runner, const struct sockaddr_in* peer, socklen_t peerLen) {
    bool gbaRtc = false;
    int64_t cartOffset = 0;

#ifdef M_CORE_GBA
    if (runner->core->platform(runner->core) == mPLATFORM_GBA) {
        struct GBA* gba = (struct GBA*) runner->core->board;
        gbaRtc = !!(gba->memory.hw.devices & HW_RTC);
        cartOffset = gba->memory.hw.rtc.offset;
    }
#endif

    struct mRTCSource* rtcSource = &runner->core->rtc.d;
    if (rtcSource->sample) rtcSource->sample(rtcSource);
    time_t raw = rtcSource->unixTime ? rtcSource->unixTime(rtcSource) : time(0);
    time_t emulated = raw - (time_t) cartOffset;

    struct tm date;
    localtime_r(&emulated, &date);

    uint16_t seed = _pb3RubyRev1RtcSeed(&date);
    enum mRTCGenericType type = runner->core->rtc.override;
    bool live = type == RTC_NO_OVERRIDE || type == RTC_WALLCLOCK_OFFSET;

    char out[256];
    snprintf(
        out, sizeof(out),
        "PB3 RTC LIVE=%d TYPE=%s GBA_RTC=%d UNIX=%lld OFFSET=%lld LOCAL=%04d-%02d-%02dT%02d:%02d:%02d SEED=%04X",
        live ? 1 : 0,
        _pb3RtcTypeName(type),
        gbaRtc ? 1 : 0,
        (long long) raw,
        (long long) cartOffset,
        date.tm_year + 1900,
        date.tm_mon + 1,
        date.tm_mday,
        date.tm_hour,
        date.tm_min,
        date.tm_sec,
        seed
    );
    _pb3Send(peer, peerLen, out);
}
/* ===== end Pokebot3DS-CFW mGBA RTC diagnostics ===== */
"""

def replace_once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected exactly one marker, found {count}")
    return text.replace(old, new, 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: mgba_rtcprobe_patch.py <path-to-src/platform/3ds/main.c>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    if "Pokebot3DS-CFW mGBA RTC diagnostics" in text:
        print("RTC diagnostics patch already applied")
        return

    text = replace_once(
        text,
        "#include <3ds/gpu/gx.h>\n",
        "#include <3ds/gpu/gx.h>\n#include <time.h>\n",
        "time include",
    )

    poll_marker = "static void _pb3BridgePoll(struct mGUIRunner* runner) {"
    text = replace_once(
        text,
        poll_marker,
        RTC_CODE + "\n\n" + poll_marker,
        "RTC helper insertion",
    )

    # RTC command must be handled before UNKNOWN.
    old = '\t_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");\n}'
    new = '''\tif (!strcmp(cmd, "RTC")) {
\t\t_pb3RtcReply(runner, &peer, peerLen);
\t\treturn;
\t}

\t_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");
}'''
    text = replace_once(text, old, new, "RTC command")

    path.write_text(text, encoding="utf-8")
    print(f"Applied Pokebot3DS-CFW mGBA RTC diagnostics patch to {path}")

if __name__ == "__main__":
    main()
