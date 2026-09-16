#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
import socket
import struct
import time

PORT = 4952
REQ_MAGIC = 0x5242524F
RESP_MAGIC = 0x5342524F
VERSION = 1

CMD_PING = 1
CMD_INPUT_PING = 5
CMD_INPUT_PULSE = 6
CMD_INPUT_STATUS = 7
CMD_RELEASE_ALL = 8
CMD_TOUCH_PULSE = 9
CMD_HID_LATCH = 10

REQ = struct.Struct("<IHHIII")
RESP = struct.Struct("<IHHIIiI")
CAPS = struct.Struct("<IIIIII")
INPUT_STATUS = struct.Struct("<IIIII")

HID_NEUTRAL = 0xFFF
CAP_EXPECTED = 0xCF
LEGACY_ACTIVE = 1 << 1

STATE_NAMES = {
    0: "IDLE",
    1: "ACCEPTED",
    2: "IN_PROGRESS",
    3: "COMPLETED",
    4: "ALREADY_COMPLETED",
    5: "ABORTED",
    6: "NOT_FOUND",
}
STATUS_NAMES = {
    0: "OK",
    1: "BAD_MAGIC",
    2: "BAD_VERSION",
    3: "BAD_COMMAND",
    12: "INPUT_INVALID",
    13: "INPUT_BUSY",
    14: "INPUT_LEGACY_ACTIVE",
    15: "INPUT_PATCH_FAILED",
}
BUTTON_BITS = {
    "A": 0, "B": 1, "SELECT": 2, "START": 3,
    "RIGHT": 4, "LEFT": 5, "UP": 6, "DOWN": 7,
    "R": 8, "L": 9, "X": 10, "Y": 11,
}


class BridgeError(RuntimeError):
    pass


class Client:
    def __init__(self, host: str, timeout: float = 1.0):
        self.host = host
        self.timeout = timeout
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)
        self.seq = random.randint(1, 0x7FFFFFFF)

    def close(self):
        self.sock.close()

    def next_seq(self) -> int:
        self.seq = (self.seq + 1) & 0x7FFFFFFF
        if self.seq == 0:
            self.seq = 1
        return self.seq

    def request(self, command: int, argument: int = 0, aux: int = 0,
                *, request_id: int | None = None, retry: bool = True):
        rid = self.next_seq() if request_id is None else request_id & 0xFFFFFFFF
        pkt = REQ.pack(REQ_MAGIC, VERSION, command, rid,
                       argument & 0xFFFFFFFF, aux & 0xFFFFFFFF)
        attempts = 2 if retry else 1
        for attempt in range(attempts):
            try:
                self.sock.sendto(pkt, (self.host, PORT))
                deadline = time.monotonic() + self.timeout
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise socket.timeout()
                    self.sock.settimeout(remaining)
                    data, _ = self.sock.recvfrom(2048)
                    if len(data) < RESP.size:
                        continue
                    magic, version, status, echo, echo_arg, result, n = RESP.unpack_from(data)
                    if magic != RESP_MAGIC or version != VERSION or echo != rid:
                        continue
                    payload = data[RESP.size:RESP.size+n]
                    if len(payload) != n:
                        raise BridgeError("truncated response payload")
                    return status, result, payload, rid
            except socket.timeout:
                if attempt + 1 >= attempts:
                    raise TimeoutError(f"command {command} request {rid} timed out")
        raise TimeoutError(f"command {command} timed out")

    @staticmethod
    def decode_status(payload: bytes):
        if len(payload) != INPUT_STATUS.size:
            raise BridgeError(f"input status length {len(payload)}, expected {INPUT_STATUS.size}")
        seq, state, raw, remaining, runtime = INPUT_STATUS.unpack(payload)
        return {
            "sequence": seq,
            "state": state,
            "state_name": STATE_NAMES.get(state, f"STATE_{state}"),
            "raw_hid": raw,
            "remaining_ms": remaining,
            "runtime_flags": runtime,
        }

    def ping(self):
        status, result, payload, _ = self.request(CMD_PING)
        if status != 0:
            raise BridgeError(f"PING {STATUS_NAMES.get(status, status)} result={result}")
        text = payload.decode("ascii", errors="replace")
        print(f"PING: PASS {text}")
        return text

    def input_ping(self):
        status, result, payload, _ = self.request(CMD_INPUT_PING)
        if status != 0:
            raise BridgeError(f"INPUT_PING {STATUS_NAMES.get(status, status)} result={result}")
        if len(payload) != CAPS.size:
            raise BridgeError(f"caps length {len(payload)}, expected {CAPS.size}")
        protocol, caps, runtime, neutral, max_hold, max_settle = CAPS.unpack(payload)
        print("INPUT_PING: PASS")
        print(f"  protocol={protocol}")
        print(f"  caps=0x{caps:08X}")
        print(f"  runtime=0x{runtime:08X}")
        print(f"  neutral=0x{neutral:03X}")
        print(f"  max_hold={max_hold} ms")
        print(f"  max_settle={max_settle} ms")
        if protocol != 1 or (caps & CAP_EXPECTED) != CAP_EXPECTED:
            raise BridgeError("required acknowledged-controller capabilities missing")
        if runtime & LEGACY_ACTIVE:
            raise BridgeError("native Rosalina InputRedirection UDP 4950 is active; disable it")
        if neutral != HID_NEUTRAL:
            raise BridgeError("unexpected neutral HID")
        return caps

    def wait_terminal(self, seq: int, timeout_s: float = 3.0):
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            time.sleep(0.04)
            status, result, payload, _ = self.request(CMD_INPUT_STATUS, seq)
            if status != 0:
                raise BridgeError(f"INPUT_STATUS {STATUS_NAMES.get(status, status)} result={result}")
            info = self.decode_status(payload)
            if info["state"] in (3, 4):
                if info["raw_hid"] != HID_NEUTRAL:
                    raise BridgeError("terminal pulse is not neutral")
                return info
            if info["state"] in (5, 6):
                raise BridgeError(f"sequence {seq} ended {info['state_name']}")
        raise TimeoutError(f"sequence {seq} did not complete")

    def release_all(self):
        status, result, payload, _ = self.request(CMD_RELEASE_ALL)
        if status != 0:
            raise BridgeError(f"RELEASE_ALL {STATUS_NAMES.get(status, status)} result={result}")
        info = self.decode_status(payload)
        if info["raw_hid"] != HID_NEUTRAL:
            raise BridgeError("RELEASE_ALL did not return neutral HID")
        print("RELEASE_ALL: PASS")
        return info

    def pulse(self, button: str, hold_ms: int, settle_ms: int):
        bit = BUTTON_BITS[button]
        raw = HID_NEUTRAL & ~(1 << bit)
        seq = self.next_seq()
        aux = (hold_ms & 0xFFFF) | ((settle_ms & 0xFFFF) << 16)
        print(f"Pulse {button}: seq={seq} raw=0x{raw:03X} hold={hold_ms} settle={settle_ms}")
        status, result, payload, _ = self.request(
            CMD_INPUT_PULSE, raw, aux, request_id=seq, retry=False
        )
        if status != 0:
            raise BridgeError(f"INPUT_PULSE {STATUS_NAMES.get(status, status)} result={result}")
        initial = self.decode_status(payload)
        print(f"  accepted state={initial['state_name']} remaining={initial['remaining_ms']} ms")
        terminal = self.wait_terminal(seq, max(3.0, (hold_ms + settle_ms) / 1000.0 + 2.0))
        print(f"  terminal={terminal['state_name']} raw=0x{terminal['raw_hid']:03X}")
        print(f"{button} PULSE: PASS")

    def touch(self, touch_state: int, hold_ms: int, settle_ms: int):
        seq = self.next_seq()
        aux = (hold_ms & 0xFFFF) | ((settle_ms & 0xFFFF) << 16)
        print(f"Touch: seq={seq} state=0x{touch_state:08X} hold={hold_ms} settle={settle_ms}")
        status, result, payload, _ = self.request(
            CMD_TOUCH_PULSE, touch_state, aux, request_id=seq, retry=False
        )
        if status != 0:
            raise BridgeError(f"TOUCH_PULSE {STATUS_NAMES.get(status, status)} result={result}")
        initial = self.decode_status(payload)
        print(f"  accepted state={initial['state_name']} remaining={initial['remaining_ms']} ms")
        terminal = self.wait_terminal(seq, max(3.0, (hold_ms + settle_ms) / 1000.0 + 2.0))
        print(f"  terminal={terminal['state_name']} raw=0x{terminal['raw_hid']:03X}")
        print("TOUCH_PULSE: PASS")

    def latch(self, button: str, seconds: float):
        bit = BUTTON_BITS[button]
        raw = HID_NEUTRAL & ~(1 << bit)
        seq = self.next_seq()
        print(f"Latch {button}: seq={seq} raw=0x{raw:03X}")
        status, result, payload, _ = self.request(
            CMD_HID_LATCH, raw, 0, request_id=seq, retry=False
        )
        if status != 0:
            raise BridgeError(f"HID_LATCH {STATUS_NAMES.get(status, status)} result={result}")
        info = self.decode_status(payload)
        if info["state"] not in (1, 2):
            raise BridgeError(f"latch not active: {info['state_name']}")
        print(f"  active state={info['state_name']}")
        print(f"  Holding for {seconds:.2f}s. Try a DIFFERENT real button/touch now.")
        time.sleep(max(0.0, seconds))
        self.release_all()
        print(f"{button} LATCH + RELEASE_ALL: PASS")


def main():
    ap = argparse.ArgumentParser(description="Pokebot-Luma v0p5 acknowledged controller tester")
    ap.add_argument("ip", help="3DS IPv4 address")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("ping", help="PING + INPUT_PING capability check")
    sub.add_parser("release", help="RELEASE_ALL only")

    p = sub.add_parser("pulse", help="firmware-timed button pulse")
    p.add_argument("button", choices=sorted(BUTTON_BITS))
    p.add_argument("--hold", type=int, default=300)
    p.add_argument("--settle", type=int, default=120)

    t = sub.add_parser("touch", help="firmware-timed raw touch-state pulse")
    t.add_argument("--state", type=lambda x: int(x, 0), default=0x01EA97FF,
                   help="raw HID touch state; default is proven ORAS Run coordinate")
    t.add_argument("--hold", type=int, default=120)
    t.add_argument("--settle", type=int, default=120)

    l = sub.add_parser("latch", help="latch a button until RELEASE_ALL")
    l.add_argument("button", choices=sorted(BUTTON_BITS))
    l.add_argument("--seconds", type=float, default=1.5)

    args = ap.parse_args()
    client = Client(args.ip)
    try:
        print(f"Target: {args.ip}:{PORT}")
        client.ping()
        client.input_ping()
        if args.cmd == "ping":
            print("ACKNOWLEDGED CONTROLLER CAPABILITY TEST: PASS")
        elif args.cmd == "release":
            client.release_all()
        elif args.cmd == "pulse":
            client.pulse(args.button, args.hold, args.settle)
        elif args.cmd == "touch":
            client.touch(args.state, args.hold, args.settle)
        elif args.cmd == "latch":
            client.latch(args.button, args.seconds)
        print("No game RAM was written.")
        return 0
    except Exception as exc:
        print(f"FAIL: {exc}")
        try:
            client.release_all()
        except Exception:
            pass
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
