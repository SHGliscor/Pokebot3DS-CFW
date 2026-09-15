#!/usr/bin/env python3
from pathlib import Path
import sys

GATE_CODE = r"""
/* ===== Pokebot3DS-CFW mGBA Ruby/Sapphire starter generation-aware RNG gate ===== */
#define PB3_RS_RNG_ADDR 0x03004818u
#define PB3_RS_GMAIN_CB2_ADDR 0x03001774u
#define PB3_RS_STARTER_CB2 0x08109EA0u

/* Enough for ~49 hours at 670 starters/hour. */
#define PB3_STARTER_HISTORY_CAPACITY 32768u
#define PB3_GENERATION_HISTORY_CAPACITY 32768u

/* Hardware tracing on Ruby v1.1 currently observes PID generation 55-58
 * Random() calls after the frame-local confirmation state. Keep a deliberately
 * wider window. STARTER_RECORD expands this automatically if hardware ever
 * reports an offset outside it. */
#define PB3_GEN_WINDOW_DEFAULT_MIN 48u
#define PB3_GEN_WINDOW_DEFAULT_MAX 72u
#define PB3_GEN_WINDOW_MAX 255u

static bool pb3StarterArmed = false;
static bool pb3StarterResultReady = false;
static uint16_t pb3StarterSeed = 0;
static uint16_t pb3StarterCurrentSeed = 0xFFFFu;

static uint32_t pb3StarterHistory[PB3_STARTER_HISTORY_CAPACITY];
static bool pb3StarterHistoryHasZero = false;
static unsigned pb3StarterHistoryCount = 0;

static uint32_t pb3GenerationHistory[PB3_GENERATION_HISTORY_CAPACITY];
static bool pb3GenerationHistoryHasZero = false;
static unsigned pb3GenerationHistoryCount = 0;

static unsigned pb3StarterSeedArms = 0;
static unsigned pb3StarterSeedChanges = 0;
static unsigned pb3StarterDelayFrames = 0;
static unsigned pb3StarterFrames = 0;

static unsigned pb3StarterExactBlocked = 0;
static unsigned pb3StarterGenerationBlocked = 0;
static unsigned pb3StarterExactBlockedTotal = 0;
static unsigned pb3StarterGenerationBlockedTotal = 0;
static unsigned pb3StarterLastPredictedPidCalls = 0;

static unsigned pb3GenerationWindowMin = PB3_GEN_WINDOW_DEFAULT_MIN;
static unsigned pb3GenerationWindowMax = PB3_GEN_WINDOW_DEFAULT_MAX;

static uint32_t pb3StarterConfirmedRng = 0;
static uint16_t pb3StarterOneShotKeys = 0;

static bool _pb3StarterGameSupported(struct mGUIRunner* runner) {
	struct mGameInfo info;
	memset(&info, 0, sizeof(info));
	runner->core->getGameInfo(runner->core, &info);
	return !strcmp(info.code, "AXVE") || !strcmp(info.code, "AXPE");
}

static uint32_t _pb3Read32(struct mGUIRunner* runner, uint32_t address) {
	uint32_t value = 0;
	value |= (runner->core->busRead8(runner->core, address + 0) & 0xFFu) << 0;
	value |= (runner->core->busRead8(runner->core, address + 1) & 0xFFu) << 8;
	value |= (runner->core->busRead8(runner->core, address + 2) & 0xFFu) << 16;
	value |= (runner->core->busRead8(runner->core, address + 3) & 0xFFu) << 24;
	return value;
}

static unsigned _pb3HistoryHash(uint32_t value, unsigned capacity) {
	value ^= value >> 16;
	value *= 0x7FEB352Du;
	value ^= value >> 15;
	value *= 0x846CA68Bu;
	value ^= value >> 16;
	return value & (capacity - 1u);
}

static bool _pb3SetContains(
	const uint32_t* table, unsigned capacity, bool hasZero, uint32_t value
) {
	if (value == 0) return hasZero;
	unsigned slot = _pb3HistoryHash(value, capacity);
	for (unsigned i = 0; i < capacity; ++i) {
		uint32_t current = table[slot];
		if (current == 0) return false;
		if (current == value) return true;
		slot = (slot + 1u) & (capacity - 1u);
	}
	return false;
}

static bool _pb3SetAdd(
	uint32_t* table,
	unsigned capacity,
	bool* hasZero,
	unsigned* count,
	uint32_t value
) {
	if (_pb3SetContains(table, capacity, *hasZero, value)) return true;
	if (*count >= capacity) return false;

	if (value == 0) {
		*hasZero = true;
		++(*count);
		return true;
	}

	unsigned slot = _pb3HistoryHash(value, capacity);
	for (unsigned i = 0; i < capacity; ++i) {
		if (table[slot] == 0) {
			table[slot] = value;
			++(*count);
			return true;
		}
		slot = (slot + 1u) & (capacity - 1u);
	}
	return false;
}

static bool _pb3StarterHistoryContains(uint32_t value) {
	return _pb3SetContains(
		pb3StarterHistory,
		PB3_STARTER_HISTORY_CAPACITY,
		pb3StarterHistoryHasZero,
		value
	);
}

static bool _pb3StarterHistoryAdd(uint32_t value) {
	return _pb3SetAdd(
		pb3StarterHistory,
		PB3_STARTER_HISTORY_CAPACITY,
		&pb3StarterHistoryHasZero,
		&pb3StarterHistoryCount,
		value
	);
}

static bool _pb3GenerationHistoryContains(uint32_t value) {
	return _pb3SetContains(
		pb3GenerationHistory,
		PB3_GENERATION_HISTORY_CAPACITY,
		pb3GenerationHistoryHasZero,
		value
	);
}

static bool _pb3GenerationHistoryAdd(uint32_t value) {
	return _pb3SetAdd(
		pb3GenerationHistory,
		PB3_GENERATION_HISTORY_CAPACITY,
		&pb3GenerationHistoryHasZero,
		&pb3GenerationHistoryCount,
		value
	);
}

static uint32_t _pb3RngNext(uint32_t value) {
	return 0x41C64E6Du * value + 0x00006073u;
}

/* Return the PID-call offset that would reproduce a recorded real generation,
 * or 0 when this confirmation state is safe in the observed generation window.
 *
 * If PID low occurs N Random() calls after confirmation, generation_pre_rng is
 * N-1 LCG advances after confirmation. The PC reconstructs that exact state
 * from the final PK3 and records it back with STARTER_RECORD. */
static unsigned _pb3PredictedGenerationCollision(uint32_t confirmRng) {
	if (!pb3GenerationHistoryCount) return 0;

	uint32_t state = confirmRng;
	for (unsigned offset = 1; offset < pb3GenerationWindowMax; ++offset) {
		state = _pb3RngNext(state);
		unsigned pidCalls = offset + 1u;
		if (pidCalls < pb3GenerationWindowMin) continue;
		if (_pb3GenerationHistoryContains(state)) return pidCalls;
	}
	return 0;
}

static void _pb3StarterHistoryReset(void) {
	pb3StarterCurrentSeed = 0xFFFFu;
	pb3StarterHistoryHasZero = false;
	pb3StarterHistoryCount = 0;
	pb3GenerationHistoryHasZero = false;
	pb3GenerationHistoryCount = 0;
	pb3StarterSeedArms = 0;
	pb3StarterSeedChanges = 0;
	pb3StarterExactBlockedTotal = 0;
	pb3StarterGenerationBlockedTotal = 0;
	pb3StarterLastPredictedPidCalls = 0;
	pb3GenerationWindowMin = PB3_GEN_WINDOW_DEFAULT_MIN;
	pb3GenerationWindowMax = PB3_GEN_WINDOW_DEFAULT_MAX;
	memset(pb3StarterHistory, 0, sizeof(pb3StarterHistory));
	memset(pb3GenerationHistory, 0, sizeof(pb3GenerationHistory));
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

	uint32_t rng = _pb3Read32(runner, PB3_RS_RNG_ADDR);

	/* Keep exact confirmation-state uniqueness as a cheap first layer. */
	if (_pb3StarterHistoryContains(rng)) {
		++pb3StarterExactBlocked;
		++pb3StarterExactBlockedTotal;
		return;
	}

	/* The old ±64 confirmation-state guard blocked nearly every later frame.
	 * Instead, only reject a confirmation state when its predicted real
	 * generation_pre_rng would reproduce one we actually observed before. */
	unsigned predictedPidCalls = _pb3PredictedGenerationCollision(rng);
	if (predictedPidCalls) {
		++pb3StarterGenerationBlocked;
		++pb3StarterGenerationBlockedTotal;
		pb3StarterLastPredictedPidCalls = predictedPidCalls;
		return;
	}

	if (!_pb3StarterHistoryAdd(rng)) {
		pb3StarterArmed = false;
		return;
	}

	pb3StarterConfirmedRng = rng;
	pb3StarterArmed = false;
	pb3StarterResultReady = true;

	/* Exactly one emulated input poll: no held-A carry into later frames. */
	pb3StarterOneShotKeys |= (1u << GBA_KEY_A);
}
/* ===== end Pokebot3DS-CFW mGBA Ruby starter generation-aware RNG gate ===== */
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
		if (!_pb3StarterGameSupported(runner)) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_UNSUPPORTED_GAME");
			return;
		}

		uint32_t cb2 = _pb3Read32(runner, PB3_RS_GMAIN_CB2_ADDR) & ~1u;
		char out[96];
		if (cb2 == PB3_RS_STARTER_CB2) {
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
		if (!_pb3StarterGameSupported(runner)) {
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

		if (
			pb3StarterHistoryCount >= PB3_STARTER_HISTORY_CAPACITY ||
			pb3GenerationHistoryCount >= PB3_GENERATION_HISTORY_CAPACITY
		) {
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
		pb3StarterExactBlocked = 0;
		pb3StarterGenerationBlocked = 0;
		pb3StarterLastPredictedPidCalls = 0;
		pb3StarterResultReady = false;
		pb3StarterArmed = true;

		char out[256];
		snprintf(
			out, sizeof(out),
			"PB3 OK STARTER_ARM SEED=%04X DELAY=%u SESSION_USED=%u GEN_USED=%u SEED_ARMS=%u SEED_CHANGES=%u WIN_MIN=%u WIN_MAX=%u",
			pb3StarterSeed,
			pb3StarterDelayFrames,
			pb3StarterHistoryCount,
			pb3GenerationHistoryCount,
			pb3StarterSeedArms,
			pb3StarterSeedChanges,
			pb3GenerationWindowMin,
			pb3GenerationWindowMax
		);
		_pb3Send(&peer, peerLen, out);
#else
		_pb3Send(&peer, peerLen, "PB3 ERR NOT_GBA");
#endif
		return;
	}

	if (!strncmp(cmd, "STARTER_RECORD ", 15)) {
		unsigned long generationPre = 0;
		unsigned pidCalls = 0;
		if (sscanf(cmd + 15, "%lx %u", &generationPre, &pidCalls) < 1) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_RECORD_SYNTAX");
			return;
		}

		if (!_pb3GenerationHistoryAdd((uint32_t) generationPre)) {
			_pb3Send(&peer, peerLen, "PB3 ERR STARTER_HISTORY_FULL");
			return;
		}

		if (pidCalls > 0 && pidCalls <= PB3_GEN_WINDOW_MAX) {
			if (pidCalls < pb3GenerationWindowMin) {
				pb3GenerationWindowMin = pidCalls > 4u ? pidCalls - 4u : 1u;
			}
			if (pidCalls > pb3GenerationWindowMax) {
				unsigned widened = pidCalls + 4u;
				pb3GenerationWindowMax =
					widened > PB3_GEN_WINDOW_MAX ? PB3_GEN_WINDOW_MAX : widened;
			}
		}

		char out[160];
		snprintf(
			out, sizeof(out),
			"PB3 OK STARTER_RECORD GEN=%08lX GEN_USED=%u WIN_MIN=%u WIN_MAX=%u",
			generationPre,
			pb3GenerationHistoryCount,
			pb3GenerationWindowMin,
			pb3GenerationWindowMax
		);
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strcmp(cmd, "STARTER_RESULT")) {
		char out[512];
		unsigned blocked = pb3StarterExactBlocked + pb3StarterGenerationBlocked;
		unsigned blockedTotal =
			pb3StarterExactBlockedTotal + pb3StarterGenerationBlockedTotal;

		if (pb3StarterResultReady) {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT READY SEED=%04X RNG=%08lX SESSION_USED=%u GEN_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED=%u NEAR=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u LAST_DIST=%u GUARD=0 EXACT=%u EXACT_TOTAL=%u GEN_BLOCKED=%u GEN_BLOCKED_TOTAL=%u PRED_CALLS=%u WIN_MIN=%u WIN_MAX=%u FRAMES=%u CAPACITY=%u",
				pb3StarterSeed,
				(unsigned long) pb3StarterConfirmedRng,
				pb3StarterHistoryCount,
				pb3GenerationHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				blocked,
				pb3StarterGenerationBlocked,
				blockedTotal,
				pb3StarterGenerationBlockedTotal,
				pb3StarterLastPredictedPidCalls,
				pb3StarterExactBlocked,
				pb3StarterExactBlockedTotal,
				pb3StarterGenerationBlocked,
				pb3StarterGenerationBlockedTotal,
				pb3StarterLastPredictedPidCalls,
				pb3GenerationWindowMin,
				pb3GenerationWindowMax,
				pb3StarterFrames,
				PB3_STARTER_HISTORY_CAPACITY
			);
		} else if (pb3StarterArmed) {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT PENDING SEED=%04X SESSION_USED=%u GEN_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED=%u NEAR=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u LAST_DIST=%u GUARD=0 EXACT=%u EXACT_TOTAL=%u GEN_BLOCKED=%u GEN_BLOCKED_TOTAL=%u PRED_CALLS=%u WIN_MIN=%u WIN_MAX=%u FRAMES=%u CAPACITY=%u",
				pb3StarterSeed,
				pb3StarterHistoryCount,
				pb3GenerationHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				blocked,
				pb3StarterGenerationBlocked,
				blockedTotal,
				pb3StarterGenerationBlockedTotal,
				pb3StarterLastPredictedPidCalls,
				pb3StarterExactBlocked,
				pb3StarterExactBlockedTotal,
				pb3StarterGenerationBlocked,
				pb3StarterGenerationBlockedTotal,
				pb3StarterLastPredictedPidCalls,
				pb3GenerationWindowMin,
				pb3GenerationWindowMax,
				pb3StarterFrames,
				PB3_STARTER_HISTORY_CAPACITY
			);
		} else {
			snprintf(
				out, sizeof(out),
				"PB3 STARTER_RESULT IDLE SEED=%04X SESSION_USED=%u GEN_USED=%u SEED_ARMS=%u SEED_CHANGES=%u BLOCKED_TOTAL=%u NEAR_TOTAL=%u GUARD=0 EXACT_TOTAL=%u GEN_BLOCKED_TOTAL=%u WIN_MIN=%u WIN_MAX=%u CAPACITY=%u",
				pb3StarterCurrentSeed == 0xFFFFu ? 0u : pb3StarterCurrentSeed,
				pb3StarterHistoryCount,
				pb3GenerationHistoryCount,
				pb3StarterSeedArms,
				pb3StarterSeedChanges,
				blockedTotal,
				pb3StarterGenerationBlockedTotal,
				pb3StarterExactBlockedTotal,
				pb3StarterGenerationBlockedTotal,
				pb3GenerationWindowMin,
				pb3GenerationWindowMax,
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

    if "Pokebot3DS-CFW mGBA Ruby starter generation-aware RNG gate" in text:
        print("Starter generation-aware RNG gate patch already applied")
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
    print(f"Applied Pokebot3DS-CFW Ruby/Sapphire generation-aware RNG gate patch to {path}")

if __name__ == "__main__":
    main()
