#!/usr/bin/env python3
from pathlib import Path
import sys

BRIDGE_CODE = r"""
/* ===== Pokebot3DS-CFW mGBA Probe 1 bridge ===== */
#define PB3_PORT 4953
#define PB3_MAX_READ 128

static Socket pb3Socket = INVALID_SOCKET;
static bool pb3SocketSubsystem = false;
static uint16_t pb3RemoteKeys = 0;
static u64 pb3RemoteKeysUntil = 0;

static uint16_t _pb3KeyMask(const char* name) {
#ifdef M_CORE_GBA
	if (!strcmp(name, "A")) return 1u << GBA_KEY_A;
	if (!strcmp(name, "B")) return 1u << GBA_KEY_B;
	if (!strcmp(name, "SELECT")) return 1u << GBA_KEY_SELECT;
	if (!strcmp(name, "START")) return 1u << GBA_KEY_START;
	if (!strcmp(name, "RIGHT")) return 1u << GBA_KEY_RIGHT;
	if (!strcmp(name, "LEFT")) return 1u << GBA_KEY_LEFT;
	if (!strcmp(name, "UP")) return 1u << GBA_KEY_UP;
	if (!strcmp(name, "DOWN")) return 1u << GBA_KEY_DOWN;
	if (!strcmp(name, "R")) return 1u << GBA_KEY_R;
	if (!strcmp(name, "L")) return 1u << GBA_KEY_L;
#endif
	return 0;
}

static void _pb3Send(const struct sockaddr_in* peer, socklen_t peerLen, const char* text) {
	if (SOCKET_FAILED(pb3Socket)) return;
	sendto(pb3Socket, text, strlen(text), 0, (const struct sockaddr*) peer, peerLen);
}

static void _pb3BridgeInit(void) {
	if (!pb3SocketSubsystem) {
		SocketSubsystemInit();
		pb3SocketSubsystem = true;
	}

	pb3Socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (SOCKET_FAILED(pb3Socket)) return;

	int yes = 1;
	setsockopt(pb3Socket, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));

	struct sockaddr_in bindInfo;
	memset(&bindInfo, 0, sizeof(bindInfo));
	bindInfo.sin_family = AF_INET;
	bindInfo.sin_port = htons(PB3_PORT);
	bindInfo.sin_addr.s_addr = INADDR_ANY;

	if (bind(pb3Socket, (const struct sockaddr*) &bindInfo, sizeof(bindInfo)) < 0) {
		SocketClose(pb3Socket);
		pb3Socket = INVALID_SOCKET;
		return;
	}
	SocketSetBlocking(pb3Socket, false);
}

static void _pb3BridgeDeinit(void) {
	if (!SOCKET_FAILED(pb3Socket)) {
		SocketClose(pb3Socket);
		pb3Socket = INVALID_SOCKET;
	}
	if (pb3SocketSubsystem) {
		SocketSubsystemDeinit();
		pb3SocketSubsystem = false;
	}
}

static void _pb3BridgePoll(struct mGUIRunner* runner) {
	if (SOCKET_FAILED(pb3Socket)) return;

	char in[256];
	struct sockaddr_in peer;
	socklen_t peerLen = sizeof(peer);
	int n = recvfrom(pb3Socket, in, sizeof(in) - 1, 0, (struct sockaddr*) &peer, &peerLen);
	if (n <= 0) return;
	in[n] = '\0';

	if (strncmp(in, "PB3 ", 4)) return;
	char* cmd = in + 4;

	if (!strcmp(cmd, "PING")) {
		_pb3Send(&peer, peerLen, "PB3 PONG PROBE1");
		return;
	}

	if (!strcmp(cmd, "GAME")) {
		struct mGameInfo info;
		memset(&info, 0, sizeof(info));
		runner->core->getGameInfo(runner->core, &info);
		char out[128];
		snprintf(out, sizeof(out), "PB3 GAME %s %s %s", info.system, info.code, info.title);
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strcmp(cmd, "STATUS")) {
		struct mGameInfo info;
		memset(&info, 0, sizeof(info));
		runner->core->getGameInfo(runner->core, &info);
		char out[128];
		snprintf(out, sizeof(out), "PB3 STATUS PROBE1 GAME=%s FAST=%d KEYS=%03X",
			info.code, frameLimiter ? 0 : 1, pb3RemoteKeys);
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strncmp(cmd, "READ ", 5)) {
		char* p = cmd + 5;
		char* end = NULL;
		unsigned long address = strtoul(p, &end, 16);
		if (end == p) {
			_pb3Send(&peer, peerLen, "PB3 ERR READ_ADDRESS");
			return;
		}
		while (*end == ' ') ++end;
		unsigned long length = strtoul(end, NULL, 0);
		if (length < 1) length = 1;
		if (length > PB3_MAX_READ) length = PB3_MAX_READ;

		char out[32 + PB3_MAX_READ * 2 + 1];
		int pos = snprintf(out, sizeof(out), "PB3 DATA %08lX %lu ", address, length);
		for (unsigned long i = 0; i < length && pos + 2 < (int) sizeof(out); ++i) {
			unsigned v = runner->core->busRead8(runner->core, (uint32_t) address + (uint32_t) i) & 0xFF;
			pos += snprintf(out + pos, sizeof(out) - pos, "%02X", v);
		}
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strncmp(cmd, "KEY ", 4)) {
		char name[16] = {0};
		unsigned ms = 100;
		if (sscanf(cmd + 4, "%15s %u", name, &ms) < 1) {
			_pb3Send(&peer, peerLen, "PB3 ERR KEY_SYNTAX");
			return;
		}
		uint16_t mask = _pb3KeyMask(name);
		if (!mask) {
			_pb3Send(&peer, peerLen, "PB3 ERR KEY_NAME");
			return;
		}
		if (ms < 16) ms = 16;
		if (ms > 5000) ms = 5000;
		pb3RemoteKeys = mask;
		pb3RemoteKeysUntil = osGetTime() + ms;
		char out[64];
		snprintf(out, sizeof(out), "PB3 OK KEY %s %u", name, ms);
		_pb3Send(&peer, peerLen, out);
		return;
	}

	if (!strcmp(cmd, "SOFTRESET")) {
#ifdef M_CORE_GBA
		pb3RemoteKeys =
			(1u << GBA_KEY_A) |
			(1u << GBA_KEY_B) |
			(1u << GBA_KEY_START) |
			(1u << GBA_KEY_SELECT);
		pb3RemoteKeysUntil = osGetTime() + 250;
		_pb3Send(&peer, peerLen, "PB3 OK SOFTRESET");
#else
		_pb3Send(&peer, peerLen, "PB3 ERR NOT_GBA");
#endif
		return;
	}

	if (!strncmp(cmd, "FAST ", 5)) {
		int on = atoi(cmd + 5) ? 1 : 0;
		frameLimiter = !on;
		_pb3Send(&peer, peerLen, on ? "PB3 OK FAST 1" : "PB3 OK FAST 0");
		return;
	}

	_pb3Send(&peer, peerLen, "PB3 ERR UNKNOWN");
}
/* ===== end Pokebot3DS-CFW mGBA Probe 1 bridge ===== */
"""

def replace_once(text, old, new, name):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{name}: expected exactly one marker, found {count}")
    return text.replace(old, new, 1)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: mgba_probe1_patch.py <path-to-src/platform/3ds/main.c>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    if "Pokebot3DS-CFW mGBA Probe 1 bridge" in text:
        print("Probe 1 patch already applied")
        return

    text = replace_once(
        text,
        "#include <mgba-util/threading.h>\n",
        "#include <mgba-util/threading.h>\n#include <mgba-util/socket.h>\n",
        "socket include",
    )

    text = replace_once(
        text,
        "static bool core2;\n",
        "static bool core2;\n\n" + BRIDGE_CODE + "\n",
        "bridge insertion",
    )

    old_poll = """static uint16_t _pollGameInput(struct mGUIRunner* runner) {
\tUNUSED(runner);

\thidScanInput();
\tuint32_t activeKeys = hidKeysHeld();
\tuint16_t keys = mInputMapKeyBits(&runner->core->inputMap, _3DS_INPUT, activeKeys, 0);
\tkeys |= (activeKeys >> 24) & 0xF0;
\treturn keys;
}"""
    new_poll = """static uint16_t _pollGameInput(struct mGUIRunner* runner) {
\t_pb3BridgePoll(runner);

\thidScanInput();
\tuint32_t activeKeys = hidKeysHeld();
\tuint16_t keys = mInputMapKeyBits(&runner->core->inputMap, _3DS_INPUT, activeKeys, 0);
\tkeys |= (activeKeys >> 24) & 0xF0;

\tif (pb3RemoteKeys && osGetTime() >= pb3RemoteKeysUntil) {
\t\tpb3RemoteKeys = 0;
\t}
\tkeys |= pb3RemoteKeys;
\treturn keys;
}"""
    text = replace_once(text, old_poll, new_poll, "game input hook")

    text = replace_once(
        text,
        "\tptmuInit();\n\tmcuHwcInit();\n\tcamInit();\n",
        "\tptmuInit();\n\tmcuHwcInit();\n\tcamInit();\n\t_pb3BridgeInit();\n",
        "bridge init",
    )

    text = replace_once(
        text,
        "\tGUIFontDestroy(font);\n\t_cleanup();\n\treturn 0;\n}",
        "\tGUIFontDestroy(font);\n\t_pb3BridgeDeinit();\n\t_cleanup();\n\treturn 0;\n}",
        "bridge shutdown",
    )

    text = replace_once(
        text,
        "static void _cleanup(void) {\n",
        "static void _cleanup(void) {\n\t_pb3BridgeDeinit();\n",
        "cleanup deinit",
    )

    text = replace_once(
        text,
        "static void _cleanup(void) {\n\t_pb3BridgeDeinit();\n",
        "static void _pb3BridgeDeinit(void);\n\nstatic void _cleanup(void) {\n\t_pb3BridgeDeinit();\n",
        "bridge deinit declaration",
    )

    path.write_text(text, encoding="utf-8")
    print(f"Applied Pokebot3DS-CFW mGBA Probe 1 patch to {path}")

if __name__ == "__main__":
    main()
