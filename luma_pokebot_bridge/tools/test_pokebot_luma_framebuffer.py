from __future__ import annotations

import argparse
from pathlib import Path
import socket
import struct
import time

REQ_MAGIC = 0x5242524F
RESP_MAGIC = 0x5342524F
WIRE_VERSION = 1
PORT = 4952

REQ = struct.Struct("<IHHIII")
RESP = struct.Struct("<IHHIIiI")
FB_INFO = struct.Struct("<IIIIII")

CMD_FRAMEBUFFER_INFO = 11
CMD_FRAMEBUFFER_READ = 12

SCREEN_IDS = {
    "top": 0,
    "top-left": 0,
    "top-right": 1,
    "bottom": 2,
    "bot": 2,
}

STATUS_NAMES = {
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
    12: "INPUT_INVALID",
    13: "INPUT_BUSY",
    14: "INPUT_LEGACY_ACTIVE",
    15: "INPUT_PATCH_FAILED",
    16: "FRAMEBUFFER_INVALID",
    17: "FRAMEBUFFER_UNSUPPORTED",
}


class BridgeError(RuntimeError):
    pass


class Bridge:
    def __init__(self, host: str, timeout: float = 1.0):
        self.remote = (host, PORT)
        self.timeout = max(0.2, float(timeout))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(self.timeout)
        self.sequence = int(time.time_ns() & 0x7FFFFFFF) or 1

    def close(self):
        self.sock.close()

    def next_id(self):
        self.sequence = (self.sequence + 1) & 0x7FFFFFFF
        if self.sequence == 0:
            self.sequence = 1
        return self.sequence

    def request(self, command: int, argument: int = 0, aux: int = 0, retries: int = 2) -> bytes:
        request_id = self.next_id()
        packet = REQ.pack(
            REQ_MAGIC,
            WIRE_VERSION,
            command,
            request_id,
            argument & 0xFFFFFFFF,
            aux & 0xFFFFFFFF,
        )

        for attempt in range(retries + 1):
            self.sock.sendto(packet, self.remote)
            deadline = time.monotonic() + self.timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                self.sock.settimeout(remaining)
                try:
                    data, _ = self.sock.recvfrom(4096)
                except socket.timeout:
                    break
                if len(data) < RESP.size:
                    continue
                magic, version, status, echoed_id, echoed_arg, result, payload_len = RESP.unpack_from(data)
                if magic != RESP_MAGIC or version != WIRE_VERSION or echoed_id != request_id:
                    continue
                payload = data[RESP.size:]
                if len(payload) != payload_len:
                    raise BridgeError(f"payload mismatch {len(payload)} != {payload_len}")
                if status != 0:
                    name = STATUS_NAMES.get(status, f"UNKNOWN_{status}")
                    raise BridgeError(
                        f"command {command} failed: {name} "
                        f"result=0x{result & 0xFFFFFFFF:08X}"
                    )
                return payload

        raise BridgeError(
            f"UDP/{PORT} timeout after {retries + 1} attempt(s)"
        )

    def framebuffer_info(self, selector: int):
        payload = self.request(CMD_FRAMEBUFFER_INFO, selector, 0)
        if len(payload) != FB_INFO.size:
            raise BridgeError(
                f"framebuffer info payload {len(payload)} != {FB_INFO.size}"
            )
        values = FB_INFO.unpack(payload)
        keys = (
            "selector",
            "width",
            "height",
            "bytes_per_pixel",
            "max_pixels_per_read",
            "flags",
        )
        return dict(zip(keys, values))

    def framebuffer_span(self, selector: int, y: int, x: int, count: int) -> bytes:
        if not (0 <= selector <= 2):
            raise ValueError("invalid selector")
        if not (0 <= y <= 0xFF):
            raise ValueError("invalid y")
        if not (0 <= x <= 0xFFFF):
            raise ValueError("invalid x")
        argument = (selector & 0xFF) | ((y & 0xFF) << 8) | ((x & 0xFFFF) << 16)
        payload = self.request(CMD_FRAMEBUFFER_READ, argument, count)
        expected = count * 3
        if len(payload) != expected:
            raise BridgeError(
                f"framebuffer span payload {len(payload)} != {expected}"
            )
        return payload


def write_bmp(path: Path, width: int, height: int, bgr: bytes):
    row_size = width * 3
    padding = (-row_size) & 3
    stride = row_size + padding
    image_size = stride * height
    file_size = 54 + image_size

    header = bytearray(54)
    header[0:2] = b"BM"
    struct.pack_into("<I", header, 2, file_size)
    struct.pack_into("<I", header, 10, 54)
    struct.pack_into("<I", header, 14, 40)
    struct.pack_into("<i", header, 18, width)
    struct.pack_into("<i", header, 22, height)
    struct.pack_into("<H", header, 26, 1)
    struct.pack_into("<H", header, 28, 24)
    struct.pack_into("<I", header, 34, image_size)

    with path.open("wb") as f:
        f.write(header)
        for y in range(height):
            start = y * row_size
            f.write(bgr[start:start + row_size])
            if padding:
                f.write(b"\0" * padding)


def capture(bridge: Bridge, selector: int, output: Path):
    info = bridge.framebuffer_info(selector)
    width = info["width"]
    height = info["height"]
    bpp = info["bytes_per_pixel"]
    max_pixels = info["max_pixels_per_read"]

    if bpp != 3:
        raise BridgeError(f"unsupported bytes/pixel: {bpp}")
    if width <= 0 or height <= 0 or max_pixels <= 0:
        raise BridgeError(f"invalid framebuffer info: {info}")

    print(
        f"Framebuffer: selector={selector} {width}x{height} "
        f"BGR8 max_pixels={max_pixels} flags=0x{info['flags']:08X}"
    )

    frame = bytearray(width * height * 3)
    for y in range(height):
        row_offset = y * width * 3
        x = 0
        while x < width:
            count = min(max_pixels, width - x)
            chunk = bridge.framebuffer_span(selector, y, x, count)
            dst = row_offset + x * 3
            frame[dst:dst + len(chunk)] = chunk
            x += count
        if y % 30 == 0 or y == height - 1:
            print(f"  line {y + 1}/{height}")

    write_bmp(output, width, height, bytes(frame))
    print(f"Saved: {output}")


def main():
    parser = argparse.ArgumentParser(
        description="Capture Pokebot-Luma framebuffer over UDP 4952."
    )
    parser.add_argument("host", help="3DS IP address")
    parser.add_argument(
        "screen",
        choices=sorted(SCREEN_IDS),
        help="top/top-left/top-right/bottom",
    )
    parser.add_argument(
        "output",
        nargs="?",
        help="output BMP path (default: pokebot_<screen>.bmp)",
    )
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()

    selector = SCREEN_IDS[args.screen]
    output = Path(
        args.output
        or f"pokebot_{args.screen.replace('-', '_')}.bmp"
    )

    bridge = Bridge(args.host, timeout=args.timeout)
    try:
        capture(bridge, selector, output)
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
