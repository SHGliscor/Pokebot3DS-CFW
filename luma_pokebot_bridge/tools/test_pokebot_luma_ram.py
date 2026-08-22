#!/usr/bin/env python3
import argparse
import socket
import struct
import sys
import time

PORT = 4952
REQ_MAGIC = 0x5242524F
RESP_MAGIC = 0x5342524F
VERSION = 1
REQ = struct.Struct("<IHHIII")
RESP = struct.Struct("<IHHIIiI")
GAME_INFO = struct.Struct("<QI8sI")
QUERY_INFO = struct.Struct("<IIIII")

CMD_PING = 1
CMD_GAME_INFO = 2
CMD_QUERY = 3
CMD_READ = 4

STATUS = {
    0: "OK",
    1: "BAD_MAGIC",
    2: "BAD_VERSION",
    3: "BAD_COMMAND",
    4: "GAME_NOT_FOUND",
    5: "OPEN_FAILED",
    6: "QUERY_FAILED",
    7: "NOT_READABLE",
    8: "RANGE_INVALID",
    9: "LENGTH_INVALID",
    10: "MAP_FAILED",
    11: "INTERNAL",
}


def request(sock, host, command, argument=0, aux=0, request_id=None):
    if request_id is None:
        request_id = int(time.time() * 1000) & 0xFFFFFFFF
    packet = REQ.pack(REQ_MAGIC, VERSION, command, request_id, argument, aux)
    sock.sendto(packet, (host, PORT))
    data, _ = sock.recvfrom(2048)
    if len(data) < RESP.size:
        raise RuntimeError(f"short response: {len(data)} bytes")
    magic, version, status, rid, echoed_arg, result, payload_len = RESP.unpack_from(data)
    if magic != RESP_MAGIC:
        raise RuntimeError(f"bad response magic 0x{magic:08X}")
    if version != VERSION:
        raise RuntimeError(f"bad response version {version}")
    if rid != request_id:
        raise RuntimeError(f"request id mismatch: sent {request_id}, got {rid}")
    payload = data[RESP.size:]
    if len(payload) != payload_len:
        raise RuntimeError(f"payload length mismatch: header {payload_len}, got {len(payload)}")
    return status, result, echoed_arg, payload


def require_ok(label, response):
    status, result, echoed_arg, payload = response
    name = STATUS.get(status, f"STATUS_{status}")
    if status != 0:
        raise RuntimeError(f"{label}: FAIL {name} result=0x{result & 0xFFFFFFFF:08X}")
    return result, echoed_arg, payload


def main():
    ap = argparse.ArgumentParser(description="Pokebot-Luma v0p4 read-only RAM bridge smoke test")
    ap.add_argument("host", help="3DS IP address")
    ap.add_argument("--address", type=lambda s: int(s, 0), default=0x00100000,
                    help="address to QUERY/READ (default: 0x00100000 game code)")
    ap.add_argument("--length", type=lambda s: int(s, 0), default=0x20,
                    help="read length, 1..0x200 (default: 0x20)")
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--query-only", action="store_true", help="skip READ after QUERY")
    args = ap.parse_args()

    if not (1 <= args.length <= 0x200):
        ap.error("--length must be between 1 and 0x200")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)

    print(f"Target: {args.host}:{PORT}")

    try:
        _, _, payload = require_ok("PING", request(sock, args.host, CMD_PING))
        print(f"PING: PASS {payload.decode('ascii', errors='replace')}")

        _, _, payload = require_ok("GAME_INFO", request(sock, args.host, CMD_GAME_INFO))
        if len(payload) != GAME_INFO.size:
            raise RuntimeError(f"GAME_INFO payload size {len(payload)} != {GAME_INFO.size}")
        title_id, pid, raw_name, flags = GAME_INFO.unpack(payload)
        name = raw_name.split(b"\0", 1)[0].decode("ascii", errors="replace")
        print("GAME_INFO: PASS")
        print(f"  title=0x{title_id:016X}")
        print(f"  pid={pid}")
        print(f"  process={name}")
        print(f"  flags=0x{flags:08X}")

        _, _, payload = require_ok(
            "QUERY", request(sock, args.host, CMD_QUERY, args.address, 0))
        if len(payload) != QUERY_INFO.size:
            raise RuntimeError(f"QUERY payload size {len(payload)} != {QUERY_INFO.size}")
        base, size, perm, state, page_flags = QUERY_INFO.unpack(payload)
        print("QUERY: PASS")
        print(f"  address=0x{args.address:08X}")
        print(f"  region=0x{base:08X} + 0x{size:X}")
        print(f"  perm=0x{perm:X} state=0x{state:X} page=0x{page_flags:X}")

        if not args.query_only:
            _, _, payload = require_ok(
                "READ", request(sock, args.host, CMD_READ, args.address, args.length))
            if len(payload) != args.length:
                raise RuntimeError(f"READ returned {len(payload)} bytes, expected {args.length}")
            print(f"READ: PASS {len(payload)} bytes")
            print("  " + payload.hex(" ").upper())

        print("RAM bridge smoke test complete. No game RAM was written.")
        return 0
    except socket.timeout:
        print("FAIL: timed out waiting for UDP response", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 3
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
