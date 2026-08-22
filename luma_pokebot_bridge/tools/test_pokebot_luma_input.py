#!/usr/bin/env python3
import argparse
import socket
import struct
import time

PORT = 4950
NEUTRAL_HID = 0x00000FFF
NEUTRAL_TOUCH = 0x02000000
NEUTRAL_CPAD = 0x007FF7FF

KEYS = {
    "A": 1 << 0,
    "B": 1 << 1,
    "SELECT": 1 << 2,
    "START": 1 << 3,
    "RIGHT": 1 << 4,
    "LEFT": 1 << 5,
    "UP": 1 << 6,
    "DOWN": 1 << 7,
    "R": 1 << 8,
    "L": 1 << 9,
    "X": 1 << 10,
    "Y": 1 << 11,
}


def packet(raw_hid: int) -> bytes:
    return struct.pack("<III", raw_hid & 0xFFF, NEUTRAL_TOUCH, NEUTRAL_CPAD)


def send_repeated(sock: socket.socket, target, raw_hid: int, count: int = 4, gap: float = 0.02):
    data = packet(raw_hid)
    for _ in range(count):
        sock.sendto(data, target)
        time.sleep(gap)


def main():
    ap = argparse.ArgumentParser(description="Pokebot-Luma v0p3 additive HID proof sender")
    ap.add_argument("ip", help="3DS IPv4 address, e.g. 192.168.0.28")
    ap.add_argument("key", choices=sorted(KEYS), help="button to pulse")
    ap.add_argument("--hold", type=float, default=0.30, help="press duration in seconds (default 0.30)")
    args = ap.parse_args()

    target = (args.ip, PORT)
    mask = KEYS[args.key]
    pressed_raw = NEUTRAL_HID & ~mask

    print(f"Target: {args.ip}:{PORT}")
    print(f"Key: {args.key}")
    print(f"Pressed raw HID: 0x{pressed_raw:03X}")
    print(f"Neutral raw HID: 0x{NEUTRAL_HID:03X}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        send_repeated(sock, target, pressed_raw)
        time.sleep(max(0.0, args.hold))
        send_repeated(sock, target, NEUTRAL_HID)

    print("Pulse sent. Physical controls should remain usable before, during, and after the pulse.")


if __name__ == "__main__":
    main()
