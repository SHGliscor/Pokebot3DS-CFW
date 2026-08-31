from __future__ import annotations

import argparse
import socket
import struct
import time

PORT = 4953
REQ_MAGIC = 0x48534250
RESP_MAGIC = 0x53534250
VERSION = 1

CMD_PING = 1
CMD_STATUS = 2

REQ = struct.Struct("<IHHI")
RESP = struct.Struct("<IHHIIIIIIii20s")

BUTTONS = [
    (0x001, "A"),
    (0x002, "B"),
    (0x004, "SELECT"),
    (0x008, "START"),
    (0x010, "RIGHT"),
    (0x020, "LEFT"),
    (0x040, "UP"),
    (0x080, "DOWN"),
    (0x100, "R"),
    (0x200, "L"),
    (0x400, "X"),
    (0x800, "Y"),
]


def button_names(keys: int) -> str:
    names = [name for bit, name in BUTTONS if keys & bit]
    return "+".join(names) if names else "NONE"


def request(sock: socket.socket, host: str, command: int, sequence: int) -> dict:
    packet = REQ.pack(REQ_MAGIC, VERSION, command, sequence)
    sock.sendto(packet, (host, PORT))
    data, remote = sock.recvfrom(4096)

    if len(data) != RESP.size:
        raise RuntimeError(f"unexpected response length {len(data)} (expected {RESP.size})")

    (
        magic,
        version,
        status,
        echoed_sequence,
        flags,
        keys,
        last_nonzero,
        changes,
        hid_index,
        hid_result,
        soc_result,
        identity,
    ) = RESP.unpack(data)

    if magic != RESP_MAGIC:
        raise RuntimeError(f"bad response magic 0x{magic:08X}")
    if version != VERSION:
        raise RuntimeError(f"protocol version {version}, expected {VERSION}")
    if echoed_sequence != sequence:
        raise RuntimeError(f"sequence mismatch {echoed_sequence} != {sequence}")

    return {
        "remote": remote,
        "status": status,
        "flags": flags,
        "keys": keys,
        "last_nonzero": last_nonzero,
        "changes": changes,
        "hid_index": hid_index,
        "hid_result": hid_result,
        "soc_result": soc_result,
        "identity": identity.split(b"\0", 1)[0].decode("ascii", "replace"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Pokebot3DS stock-Luma HID sysmodule v0p1 probe")
    parser.add_argument("ip", help="3DS IP address")
    parser.add_argument("--seconds", type=float, default=15.0, help="physical-input monitor duration")
    args = parser.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(2.0)

        sequence = int(time.time_ns() & 0x7FFFFFFF) or 1
        first = request(sock, args.ip, CMD_PING, sequence)

        print(f"PING: {'PASS' if first['status'] == 0 else 'FAIL'} {first['identity']}")
        print(f"  remote={first['remote'][0]}:{first['remote'][1]}")
        print(f"  HID={'READY' if first['flags'] & 1 else 'NOT READY'} result=0x{first['hid_result'] & 0xFFFFFFFF:08X}")
        print(f"  UDP={'READY' if first['flags'] & 2 else 'NOT READY'} result=0x{first['soc_result'] & 0xFFFFFFFF:08X}")
        print(f"  index={first['hid_index']} keys=0x{first['keys']:03X}")

        if first["status"] != 0:
            raise SystemExit(1)

        print()
        print(f"Monitoring physical buttons for {args.seconds:.0f} seconds.")
        print("Press/release physical A, then physical START on the 3DS.")
        print("No input is injected by this test.\n")

        deadline = time.monotonic() + args.seconds
        last_tuple = None
        while time.monotonic() < deadline:
            sequence = (sequence + 1) & 0x7FFFFFFF or 1
            status = request(sock, args.ip, CMD_STATUS, sequence)
            current = (
                status["keys"],
                status["last_nonzero"],
                status["changes"],
                status["hid_index"],
            )
            if current != last_tuple:
                print(
                    f"keys=0x{status['keys']:03X} {button_names(status['keys']):<12} "
                    f"seen=0x{status['last_nonzero']:03X} "
                    f"changes={status['changes']} index={status['hid_index']}"
                )
                last_tuple = current
            time.sleep(0.08)

        print("\nMonitor complete.")
        print("PASS target: A appears as 0x001 and START appears as 0x008, with changes increasing.")


if __name__ == "__main__":
    main()
