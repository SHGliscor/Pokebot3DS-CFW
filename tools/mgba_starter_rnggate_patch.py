#!/usr/bin/env python3
from pathlib import Path
import sys

GATE_CODE = r"""
/* ===== Pokebot3DS-CFW mGBA Ruby starter RNG gate ===== */
#define PB3_RUBY_RNG_ADDR 0x03004818u
#define PB3_STARTER_HISTORY_MAX 128u

static bool pb3StarterArmed = false;
static bool pb3StarterResultReady = false;
static uint16_t pb3StarterSeed = 0;
static uint16_t pb3StarterHistorySeed = 0xFFFFu;
static uint32_t pb3StarterHistory[PB3_STARTER_HISTORY_MAX];
static unsigned pb3StarterHistoryCount = 0;
static unsigned pb3StarterDelayFrames = 0;
static unsigned pb3StarterFrames = 0;
static unsigned pb3StarterBlocked = 0;
static uint32_t pb3StarterConfirmedRng = 0;
static uint16_t pb3StarterOneShotKeys = 0;

static uint32_t _pb3Read32(struct mGUIRunner* runner, uint32_t address) {
	uint32_t value = 0;
	value |= (runner->core->busRead8(runner->core, address + 0) & 0xFFu) << 0;
	value |= (runner->core->busRead8(runner->core, address + 1) & 0xFFu) << 8;
	value |= (runner->core->busRead8(runner->core, address + 2) & 0xFFu) << 16;
	value |= (runner->core->busRead8(runner->core, address + 3) & 0xFFu) << 24;
	return value;
}

static bool _pb3StarterHistoryContains(uint32_t value) {
	for (unsigned i = 0; i < pb3StarterHistoryCount; ++i) {
		if (pb3StarterHistory[i] == value) return true;
	}
	return false;
}

static void _pb3StarterHistoryReset(uint16_t seed) {
	pb3StarterHistorySeed = seed;
	pb3StarterHistoryCount = 0;
	memset(pb3StarterHistory, 0, sizeof(pb3StarterHistory));
}

static void _pb3StarterHistoryAdd(uint32_t value) {
	if (pb3StarterHistoryCount >= PB3_STARTER_HISTORY_MAX) {
		memmove(
			&pb3StarterHistory[0],
			&pb3StarterHistory[1],
			(PB3_STARTER_HISTORY_MAX - 1u) * sizeof(pb3StarterHistory[0])
		);
		pb3StarterHistoryCount = PB3_STARTER_HISTORY_MAX - 1u;
	}
	pb3StarterHistory[pb3StarterHistoryCount++] = value;
}

static void _pb3StarterGateTick(struct mGUIRunner* runner) {
	if (!pb3StarterArmed) return;
#ifdef M_CORE_GBA
	if (runner->core->platform(runner->core) != mPLATFORM_GBA) return;
#else
	return;
#endif

	++pb3StarterFrames;
	if (pb3StarterFrames <= pb3StarterDelayFrames) return;

	uint32_t rng = _pb3Read32(runner, PB3_RUBY_RNG_ADDR);
	if (_pb3StarterHistoryContains(rng)) {
		++pb3StarterBlocked;
		return;
	}

	_pb3StarterHistoryAdd(rng);
	pb3StarterConfirmedRng = rng;
	pb3StarterArmed = false;
	pb3StarterResultReady = true;

	/* One emulated input poll only: enough to create a new-key A press
	 * without carrying A across many fast-forwarded frames. */
	pb3StarterOneShotKeys |= (1u << GBA_KEY_A);
}
/* ===== end Pokebot3DS-CFW mGBA Ruby starter RNG gate ===== */
"""

COMMAND_CODE = r"""
	if (!strncmp(cmd, "STARTER_ARM ", 12)) {
#ifdef M_CORE_GBA
		struct mGameInfo info;
		memset(&info, 0, sizeof(info));
		runner->core->getGameInfo(runner->core, &info);
		if (strcmp(info.code, "AXVE")) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_UNSUPPORTED_GAME");
			return;
		}

		unsigned seed = 0;
		unsigned delay = 0;
		if (sscanf(cmd + 12, "%x %u", &seed, &delay) < 1) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_ARM_SYNTAX");
			return;
		}
		if (delay > 240u) delay = 240u;
		uint16_t seed16 = (uint16_t) (seed & 0xFFFFu);
		if (pb3StarterHistorySeed != seed16) {
			_pb3StarterHistoryReset(seed16);
		}

		pb3StarterSeed = seed16;
		pb3StarterDelayFrames = delay;
		pb3StarterFrames = 0;
		pb3StarterBlocked = 0;
		pb3StarterResultReady = false;
		pb3StarterArmed = true;

		char out[128];
		snprintf(
			out, sizeof(out),
			"PB3 OK STARTER_ARM SEED=%04X DELAY=%u USED=%u",
			pb3StarterSeed, pb3StarterDelayFrames, pb3StarterHistoryCount
		);
		_pb3Send(&peer, peerLen, out);
#else
		_pb3Send(&peer, peerLen, "PB3 ERR NOT_GBA");
#endif
		return;
	}

	if (!strcmp(cmd, "STARTER_RESULT")) {
		char out[192];
		if (pb3StarterResultReady) {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT READY SEED=%04X RNG=%08lX USED=%u BLOCKED=%u FRAMES=%u",
				pb3StarterSeed,
				(unsigned long) pb3StarterConfirmedRng,
				pb3StarterHistoryCount,
				pb3StarterBlocked,
				pb3StarterFrames
			);
		} else if (pb3StarterArmed) {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT PENDING SEED=%04X USED=%u BLOCKED=%u FRAMES=%u",
				pb3StarterSeed,
				pb3StarterHistoryCount,
				pb3StarterBlocked,
				pb3StarterFrames
			);
		} else {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT IDLE SEED=%04X USED=%u",
				pb3StarterHistorySeed == 0xFFFFu ? 0u : pb3StarterHistorySeed,
				pb3StarterHistoryCount
			);
		}
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strcmp(cmd, "STARTER_CANCEL")) {
		pb3StarterArmed = false;
		pb3StarterResultReady = false;
		pb3StarterOneShotKeys = 0;
		_pb3Send(&peer, peerLen, "PB3 OK STARTER_CANCEL");
		return;
	}

	if (!strcmp(cmd, "STARTER_CLEAR")) {
		pb3StarterArmed = false;
		pb3StarterResultReady = false;
		pb3StarterOneShotKeys = 0;
		_pb3StarterHistoryReset(0xFFFFu);
		_pb3Send(&peer, peerLen, "PB3 OK STARTER_CLEAR");
		return;
	}

"""

def replace_once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected exactly one marker, found {count}")
    return text.replace(old, new, 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: mgba_starter_rnggate_patch.py <path-to-src/platform/3ds/main.c>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    if "Pokebot3DS-CFW mGBA Ruby starter RNG gate" in text:
        print("Starter RNG gate patch already applied")
        return

    rtc_marker = "/* ===== end Pokebot3DS-CFW mGBA RTC diagnostics ===== */"
    text = replace_once(
        text,
        rtc_marker,
        rtc_marker + "\n\n" + GATE_CODE,
        "starter gate helper insertion",
    )

    unknown = '\t_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");\n}'
    text = replace_once(
        text,
        unknown,
        COMMAND_CODE + unknown,
        "starter gate commands",
    )

    text = replace_once(
        text,
        "\t_pb3BridgePoll(runner);\n\n\thidScanInput();",
        "\t_pb3BridgePoll(runner);\n\t_pb3StarterGateTick(runner);\n\n\thidScanInput();",
        "starter gate poll hook",
    )

    text = replace_once(
        text,
        "\tkeys |= pb3RemoteKeys;\n\treturn keys;",
        "\tkeys |= pb3RemoteKeys;\n\tkeys |= pb3StarterOneShotKeys;\n\tpb3StarterOneShotKeys = 0;\n\treturn keys;",
        "starter one-shot input hook",
    )

    path.write_text(text, encoding="utf-8")
    print(f"Applied Pokebot3DS-CFW Ruby starter RNG gate patch to {path}")

if __name__ == "__main__":
    main()
