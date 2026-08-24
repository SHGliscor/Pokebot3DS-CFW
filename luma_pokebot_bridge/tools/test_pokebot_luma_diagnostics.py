#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import random
import socket
import struct

PORT = 4952
REQ_MAGIC = 0x5242524F
RESP_MAGIC = 0x5342524F
VERSION = 1
CMD_DIAGNOSTICS = 13

REQ = struct.Struct("<IHHIII")
RESP = struct.Struct("<IHHIIiI")
DIAGNOSTICS = struct.Struct("<14I32s")


def read_diagnostics(host: str, timeout: float) -> dict:
    request_id = random.randint(1, 0x7FFFFFFF)
    packet = REQ.pack(REQ_MAGIC, VERSION, CMD_DIAGNOSTICS, request_id, 0, 0)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        sock.sendto(packet, (host, PORT))
        data, _ = sock.recvfrom(2048)

    if len(data) < RESP.size:
        raise RuntimeError(f"short response: {len(data)} bytes")
    magic, version, status, echoed_id, _, result, payload_length = RESP.unpack_from(data)
    if magic != RESP_MAGIC or version != VERSION:
        raise RuntimeError("invalid bridge response header")
    if echoed_id != request_id:
        raise RuntimeError("request ID mismatch")
    if status != 0:
        raise RuntimeError(f"diagnostics status={status} result=0x{result & 0xFFFFFFFF:08X}")

    payload = data[RESP.size:]
    if len(payload) != payload_length or len(payload) != DIAGNOSTICS.size:
        raise RuntimeError(
            f"diagnostics payload size={len(payload)}, expected={DIAGNOSTICS.size}"
        )

    values = DIAGNOSTICS.unpack(payload)
    build_id = values[14].split(b"\0", 1)[0].decode("ascii", errors="replace")
    model = {1: "Old 3DS", 2: "New 3DS"}.get(values[1], f"Unknown ({values[1]})")
    return {
        "diagnostics_protocol": values[0],
        "console_model_code": values[1],
        "console_model": model,
        "bridge_priority": values[2],
        "bridge_priority_hex": f"0x{values[2]:02X}",
        "idle_yield_us": values[3],
        "firmware_revision": values[4],
        "build_flags": f"0x{values[5]:08X}",
        "bridge_packets": values[6],
        "bridge_reads": values[7],
        "input_commands": values[8],
        "hid_assert_writes": values[9],
        "hid_neutral_writes": values[10],
        "hid_pulse_commands": values[11],
        "hid_latch_commands": values[12],
        "last_assert_raw_hid": f"0x{values[13]:03X}",
        "build_id": build_id,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pokebot-Luma v0p7 runtime diagnostics")
    parser.add_argument("host", help="3DS IP address")
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        info = read_diagnostics(args.host, args.timeout)
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("RUNTIME DIAGNOSTICS: PASS")
            for key, value in info.items():
                print(f"  {key}: {value}")

        if info["diagnostics_protocol"] != 1:
            raise RuntimeError("unsupported diagnostics protocol")
        if info["console_model_code"] not in (1, 2):
            raise RuntimeError("firmware did not identify the console model")
        if info["bridge_priority"] != 0x20:
            raise RuntimeError(
                f"wrong compiled bridge priority: {info['bridge_priority_hex']}"
            )
        if info["firmware_revision"] != 7 or info["build_id"] != "v0p7-runtime-diag":
            raise RuntimeError("unexpected firmware build identity")
        return 0
    except Exception as exc:
        print(f"RUNTIME DIAGNOSTICS: FAIL: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
