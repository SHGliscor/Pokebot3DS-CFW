#!/usr/bin/env python3
from pathlib import Path
import sys

GATE_CODE = r"""
/* ===== Pokebot3DS-CFW mGBA Ruby starter RNG gate ===== */
#define PB3_RUBY_RNG_ADDR 0x03004818u
#define PB3_RUBY_GMAIN_CB2_ADDR 0x03001774u
#define PB3_RUBY_STARTER_CB2 0x08109EA0u
#define PB3_STARTER_HISTORY_CAPACITY 32768u
#define PB3_STARTER_GUARD_DEFAULT 64u
#define PB3_STARTER_GUARD_MAX 512u
#define PB3_RNG_A 0x41C64E6Du
#define PB3_RNG_C 0x00006073u
#define PB3_RNG_A_INV 0xEEB9EB65u

static bool pb3StarterArmed = false;
static bool pb3StarterResultReady = false;
static uint16_t pb3StarterSeed = 0;
static uint16_t pb3StarterCurrentSeed = 0xFFFFu;
static uint32_t pb3StarterHistory[PB3_STARTER_HISTORY_CAPACITY];
static bool pb3StarterHistoryHasZero = false;
static unsigned pb3StarterHistoryCount = 0;
static unsigned pb3StarterSeedArms = 0;
static unsigned pb3StarterSeedChanges = 0;
static unsigned pb3StarterGuardCalls = PB3_STARTER_GUARD_DEFAULT;
static unsigned pb3StarterDelayFrames = 0;
static unsigned pb3StarterFrames = 0;
static unsigned pb3StarterBlocked = 0;
static unsigned pb3StarterNearBlocked = 0;
static unsigned pb3StarterBlockedTotal = 0;
static unsigned pb3StarterNearBlockedTotal = 0;
static int pb3StarterLastDistance = 0;
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

static unsigned _pb3StarterHistoryHash(uint32_t value) {
	value ^= value >> 16;
	value *= 0x7FEB352Du;
	value ^= value >> 15;
	value *= 0x846CA68Bu;
	value ^= value >> 16;
	return value & (PB3_STARTER_HISTORY_CAPACITY - 1u);
}

static bool _pb3StarterHistoryContains(uint32_t value) {
	if (value == 0) return pb3StarterHistoryHasZero;
	unsigned slot = _pb3StarterHistoryHash(value);
	for (unsigned i = 0; i < PB3_STARTER_HISTORY_CAPACITY; ++i) {
		uint32_t current = pb3StarterHistory[slot];
		if (current == 0) return false;
		if (current == value) return true;
		slot = (slot + 1u) & (PB3_STARTER_HISTORY_CAPACITY - 1u);
	}
	return false;
}

static uint32_t _pb3RngNext(uint32_t value) {
	return PB3_RNG_A * value + PB3_RNG_C;
}

static uint32_t _pb3RngPrev(uint32_t value) {
	return PB3_RNG_A_INV * (value - PB3_RNG_C);
}

/* Return signed LCG-call distance to a used confirmation state.
 *  0  = exact reuse
 * +N  = candidate is N calls before a used state
 * -N  = candidate is N calls after a used state
 * 9999 = outside the guard band
 *
 * The guard exists because hardware evidence showed the same generated PID
 * arising from confirmation states 1-2 LCG calls apart: Ruby consumed a
 * different number of Random() calls between A confirmation and Random32().
 * Exact-value uniqueness alone therefore cannot guarantee unique generations.
 */
static int _pb3StarterHistoryDistance(uint32_t value) {
	if (_pb3StarterHistoryContains(value)) return 0;

	uint32_t forward = value;
	uint32_t backward = value;
	for (unsigned distance = 1; distance <= pb3StarterGuardCalls; ++distance) {
		forward = _pb3RngNext(forward);
		if (_pb3StarterHistoryContains(forward)) return (int) distance;

		backward = _pb3RngPrev(backward);
		if (_pb3StarterHistoryContains(backward)) return -(int) distance;
	}
	return 9999;
}

static void _pb3StarterHistoryReset(void) {
	pb3StarterCurrentSeed = 0xFFFFu;
	pb3StarterHistoryHasZero = false;
	pb3StarterHistoryCount = 0;
	pb3StarterSeedArms = 0;
	pb3StarterSeedChanges = 0;
	pb3StarterBlockedTotal = 0;
	pb3StarterNearBlockedTotal = 0;
	pb3StarterLastDistance = 0;
	memset(pb3StarterHistory, 0, sizeof(pb3StarterHistory));
}

static bool _pb3StarterHistoryAdd(uint32_t value) {
	if (_pb3StarterHistoryContains(value)) return true;
	if (pb3StarterHistoryCount >= PB3_STARTER_HISTORY_CAPACITY) return false;

	if (value == 0) {
		pb3StarterHistoryHasZero = true;
		++pb3StarterHistoryCount;
		return true;
	}

	unsigned slot = _pb3StarterHistoryHash(value);
	for (unsigned i = 0; i < PB3_STARTER_HISTORY_CAPACITY; ++i) {
		if (pb3StarterHistory[slot] == 0) {
			pb3StarterHistory[slot] = value;
			++pb3StarterHistoryCount;
			return true;
		}
		slot = (slot + 1u) & (PB3_STARTER_HISTORY_CAPACITY - 1u);
	}
	return false;
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
	int distance = _pb3StarterHistoryDistance(rng);
	if (distance != 9999) {
		++pb3StarterBlocked;
		++pb3StarterBlockedTotal;
		pb3StarterLastDistance = distance;
		if (distance != 0) {
			++pb3StarterNearBlocked;
			++pb3StarterNearBlockedTotal;
		}
		return;
	}

	if (!_pb3StarterHistoryAdd(rng)) {
		pb3StarterArmed = false;
		return;
	}
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

	if (!strncmp(cmd, "KEY1 ", 5)) {
		char name[16] = {0};
		if (sscanf(cmd + 5, "%15s", name) < 1) {
			_pb3Send(&peer, peerLen, "PB3 ERR KEY1_SYNTAX");
			return;
		}
		uint16_t mask = _pb3KeyMask(name);
		if (!mask) {
			_pb3Send(&peer, peerLen, "PB3 ERR KEY1_NAME");
			return;
		}
		pb3StarterOneShotKeys |= mask;
		char out[64];
		snprintf(out, sizeof(out), "PB3 OK KEY1 %s", name);
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strcmp(cmd, "STARTER_OPEN")) {
#ifdef M_CORE_GBA
		struct mGameInfo info;
		memset(&info, 0, sizeof(info));
		runner->core->getGameInfo(runner->core, &info);
		if (strcmp(info.code, "AXVE")) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_UNSUPPORTED_GAME");
			return;
		}

		uint32_t cb2 = _pb3Read32(runner, PB3_RUBY_GMAIN_CB2_ADDR) & ~1u;
		char out[96];
		if (cb2 == PB3_RUBY_STARTER_CB2) {
			snprintf(out, sizeof(out), "PB3 STARTER_OPEN SCREEN CB=%08lX", (unsigned long) cb2);
		} else {
			pb3StarterOneShotKeys |= (1u << GBA_KEY_A);
			snprintf(out, sizeof(out), "PB3 STARTER_OPEN PRESSED CB=%08lX", (unsigned long) cb2);
		}
		_pb3Send(&peer, peerLen, out);
#else
		_pb3Send(&peer, peerLen, "PB3 ERR NOT_GBA");
#endif
		return;
	}

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
		unsigned guard = PB3_STARTER_GUARD_DEFAULT;
		if (sscanf(cmd + 12, "%x %u %u", &seed, &delay, &guard) < 1) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_ARM_SYNTAX");
			return;
		}
		if (delay > 240u) delay = 240u;
		if (guard > PB3_STARTER_GUARD_MAX) guard = PB3_STARTER_GUARD_MAX;
		pb3StarterGuardCalls = guard;
		uint16_t seed16 = (uint16_t) (seed & 0xFFFFu);
		if (pb3StarterHistoryCount >= PB3_STARTER_HISTORY_CAPACITY) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_HISTORY_FULL");
			return;
		}
		if (pb3StarterCurrentSeed == 0xFFFFu) {
			pb3StarterCurrentSeed = seed16;
			pb3StarterSeedArms = 1;
		} else if (pb3StarterCurrentSeed != seed16) {
			pb3StarterCurrentSeed = seed16;
			pb3StarterSeedArms = 1;
			++pb3StarterSeedChanges;
		} else {
			++pb3StarterSeedArms;
		}

		pb3StarterSeed = seed16;
		pb3StarterDelayFrames = delay;
		pb3StarterFrames = 0;
		pb3StarterBlocked = 0;
		pb3StarterNearBlocked = 0;
		pb3StarterLastDistance = 0;
		pb3StarterResultReady = false;
		pb3StarterArmed = true;

		char out[320];
		snprintf(
			out, sizeof(out),
			"PB3 OK STARTER_ARM SEED=%04X DELAY=%u SESSION_USED=%u SEED_ARMS=%u SEED_CHANGES=%u GUARD=%u",
			pb3StarterSeed, pb3StarterDelayFrames, pb3StarterHistoryCount,
			pb3StarterSeedArms, pb3StarterSeedChanges, pb3StarterGuardCalls
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
				"PB3 STARTER_RESULT READY SEED=%04X RNG=%08lX SESSION_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED=%u NEAR=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u LAST_DIST=%d GUARD=%u FRAMES=%u CAPACITY=%u",
				pb3StarterSeed,
				(unsigned long) pb3StarterConfirmedRng,
				pb3StarterHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				pb3StarterBlocked,
				pb3StarterNearBlocked,
				pb3StarterBlockedTotal,
				pb3StarterNearBlockedTotal,
				pb3StarterLastDistance,
				pb3StarterGuardCalls,
				pb3StarterFrames,
				PB3_STARTER_HISTORY_CAPACITY
			);
		} else if (pb3StarterArmed) {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT PENDING SEED=%04X SESSION_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED=%u NEAR=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u LAST_DIST=%d GUARD=%u FRAMES=%u CAPACITY=%u",
				pb3StarterSeed,
				pb3StarterHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				pb3StarterBlocked,
				pb3StarterNearBlocked,
				pb3StarterBlockedTotal,
				pb3StarterNearBlockedTotal,
				pb3StarterLastDistance,
				pb3StarterGuardCalls,
				pb3StarterFrames,
				PB3_STARTER_HISTORY_CAPACITY
			);
		} else {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT IDLE SEED=%04X SESSION_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u GUARD=%u CAPACITY=%u",
				pb3StarterCurrentSeed == 0xFFFFu ? 0u : pb3StarterCurrentSeed,
				pb3StarterHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				pb3StarterBlockedTotal,
				pb3StarterNearBlockedTotal,
				pb3StarterGuardCalls,
				PB3_STARTER_HISTORY_CAPACITY
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
		_pb3StarterHistoryReset();
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

    poll_marker = "static void _pb3BridgePoll(struct mGUIRunner* runner) {"
    text = replace_once(
        text,
        poll_marker,
        GATE_CODE + "\n\n" + poll_marker,
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
