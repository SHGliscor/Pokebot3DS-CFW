#!/usr/bin/env python3
"""Read-only Pokémon Crystal VC RAM probe for Pokebot3DS-CFW.

The official English Crystal VC emulator mirrors the Game Boy address space at
3DS process address 0x08A23FAC + gb_address. This probe uses only the existing
Pokebot QUERY/READ transport; it never writes game memory.

Reference points used here:
- PokeReader Crystal reader: party 0xDCDF, wild 0xD206/0xD20C, egg
  0xDF7B/0xDF90, trainer ID 0xD47B.
- PKHeX PK2: DVs at PK2 +0x15/+0x16, friendship +0x1B, level +0x1F.
- Crystal VC cheats independently expose the same WRAM mapping base 0x08A23FAC.
"""

from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from dataclasses import dataclass

PORT = 4952
REQ_MAGIC = 0x5242524F
RESP_MAGIC = 0x5342524F
VERSION = 1
REQ = struct.Struct("<IHHIII")
RESP = struct.Struct("<IHHIIiI")
GAME_INFO = struct.Struct("<QI8sI")

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

CRYSTAL_EN_TID = 0x0004000000172800
VC_GB_BASE = 0x08A23FAC

GB_TRAINER_ID = 0xD47B
GB_WILD_SPECIES = 0xD206
GB_WILD_DV_ATK_DEF = 0xD20C
GB_PARTY_COUNT = 0xDCD7
GB_PARTY_MON1 = 0xDCDF
GB_PARTY_MON_SIZE = 0x30
GB_EGG_SPECIES = 0xDF7B
GB_EGG_DV_ATK_DEF = 0xDF90

SPECIES = (
    "None Bulbasaur Ivysaur Venusaur Charmander Charmeleon Charizard Squirtle Wartortle Blastoise "
    "Caterpie Metapod Butterfree Weedle Kakuna Beedrill Pidgey Pidgeotto Pidgeot Rattata Raticate "
    "Spearow Fearow Ekans Arbok Pikachu Raichu Sandshrew Sandslash NidoranF Nidorina Nidoqueen "
    "NidoranM Nidorino Nidoking Clefairy Clefable Vulpix Ninetales Jigglypuff Wigglytuff Zubat Golbat "
    "Oddish Gloom Vileplume Paras Parasect Venonat Venomoth Diglett Dugtrio Meowth Persian Psyduck "
    "Golduck Mankey Primeape Growlithe Arcanine Poliwag Poliwhirl Poliwrath Abra Kadabra Alakazam Machop "
    "Machoke Machamp Bellsprout Weepinbell Victreebel Tentacool Tentacruel Geodude Graveler Golem Ponyta "
    "Rapidash Slowpoke Slowbro Magnemite Magneton Farfetch'd Doduo Dodrio Seel Dewgong Grimer Muk Shellder "
    "Cloyster Gastly Haunter Gengar Onix Drowzee Hypno Krabby Kingler Voltorb Electrode Exeggcute Exeggutor "
    "Cubone Marowak Hitmonlee Hitmonchan Lickitung Koffing Weezing Rhyhorn Rhydon Chansey Tangela Kangaskhan "
    "Horsea Seadra Goldeen Seaking Staryu Starmie Mr._Mime Scyther Jynx Electabuzz Magmar Pinsir Tauros "
    "Magikarp Gyarados Lapras Ditto Eevee Vaporeon Jolteon Flareon Porygon Omanyte Omastar Kabuto Kabutops "
    "Aerodactyl Snorlax Articuno Zapdos Moltres Dratini Dragonair Dragonite Mewtwo Mew Chikorita Bayleef "
    "Meganium Cyndaquil Quilava Typhlosion Totodile Croconaw Feraligatr Sentret Furret Hoothoot Noctowl "
    "Ledyba Ledian Spinarak Ariados Crobat Chinchou Lanturn Pichu Cleffa Igglybuff Togepi Togetic Natu Xatu "
    "Mareep Flaaffy Ampharos Bellossom Marill Azumarill Sudowoodo Politoed Hoppip Skiploom Jumpluff Aipom "
    "Sunkern Sunflora Yanma Wooper Quagsire Espeon Umbreon Murkrow Slowking Misdreavus Unown Wobbuffet "
    "Girafarig Pineco Forretress Dunsparce Gligar Steelix Snubbull Granbull Qwilfish Scizor Shuckle Heracross "
    "Sneasel Teddiursa Ursaring Slugma Magcargo Swinub Piloswine Corsola Remoraid Octillery Delibird Mantine "
    "Skarmory Houndour Houndoom Kingdra Phanpy Donphan Porygon2 Stantler Smeargle Tyrogue Hitmontop Smoochum "
    "Elekid Magby Miltank Blissey Raikou Entei Suicune Larvitar Pupitar Tyranitar Lugia Ho-Oh Celebi"
).split()

SHINY_ATKDEF = {0x2A, 0x3A, 0x6A, 0x7A, 0xAA, 0xBA, 0xEA, 0xFA}


@dataclass(frozen=True)
class DVs:
    attack: int
    defense: int
    speed: int
    special: int
    hp: int
    shiny: bool
    raw_atkdef: int
    raw_spespc: int


def parse_dvs(atkdef: int, spespc: int) -> DVs:
    attack = atkdef >> 4
    defense = atkdef & 0x0F
    speed = spespc >> 4
    special = spespc & 0x0F
    hp = ((attack & 1) << 3) | ((defense & 1) << 2) | ((speed & 1) << 1) | (special & 1)
    shiny = spespc == 0xAA and atkdef in SHINY_ATKDEF
    return DVs(attack, defense, speed, special, hp, shiny, atkdef, spespc)


def species_name(index: int) -> str:
    if 0 <= index < len(SPECIES):
        return SPECIES[index].replace("_", " ")
    return f"Unknown({index})"


def request(sock: socket.socket, host: str, command: int, argument: int = 0,
            aux: int = 0, request_id: int | None = None):
    if request_id is None:
        request_id = int(time.time() * 1000) & 0xFFFFFFFF
    sock.sendto(REQ.pack(REQ_MAGIC, VERSION, command, request_id, argument, aux), (host, PORT))
    data, _ = sock.recvfrom(4096)
    if len(data) < RESP.size:
        raise RuntimeError(f"short response: {len(data)} bytes")
    magic, version, status, rid, echoed_arg, result, payload_len = RESP.unpack_from(data)
    if magic != RESP_MAGIC:
        raise RuntimeError(f"bad response magic 0x{magic:08X}")
    if version != VERSION:
        raise RuntimeError(f"bad protocol version {version}")
    if rid != request_id:
        raise RuntimeError(f"request id mismatch: sent {request_id}, got {rid}")
    payload = data[RESP.size:]
    if len(payload) != payload_len:
        raise RuntimeError(f"payload length mismatch: expected {payload_len}, got {len(payload)}")
    return status, result, echoed_arg, payload


def require_ok(label: str, response):
    status, result, echoed_arg, payload = response
    if status != 0:
        name = STATUS.get(status, f"STATUS_{status}")
        raise RuntimeError(f"{label}: {name} result=0x{result & 0xFFFFFFFF:08X}")
    return result, echoed_arg, payload


class CrystalReader:
    def __init__(self, sock: socket.socket, host: str):
        self.sock = sock
        self.host = host

    @staticmethod
    def native_address(gb_address: int) -> int:
        if not 0 <= gb_address <= 0xFFFF:
            raise ValueError(f"GB address out of range: 0x{gb_address:X}")
        return VC_GB_BASE + gb_address

    def read_native(self, address: int, length: int) -> bytes:
        if not 1 <= length <= 0x200:
            raise ValueError("read length must be 1..0x200")
        _, _, payload = require_ok(
            f"READ 0x{address:08X}+0x{length:X}",
            request(self.sock, self.host, CMD_READ, address, length),
        )
        if len(payload) != length:
            raise RuntimeError(f"READ returned {len(payload)} bytes, expected {length}")
        return payload

    def read_gb(self, gb_address: int, length: int = 1) -> bytes:
        return self.read_native(self.native_address(gb_address), length)

    def trainer_id(self) -> int:
        return int.from_bytes(self.read_gb(GB_TRAINER_ID, 2), "big")

    def wild(self):
        data = self.read_gb(GB_WILD_SPECIES, GB_WILD_DV_ATK_DEF - GB_WILD_SPECIES + 2)
        species = data[0]
        dv_off = GB_WILD_DV_ATK_DEF - GB_WILD_SPECIES
        return species, parse_dvs(data[dv_off], data[dv_off + 1])

    def egg(self):
        data = self.read_gb(GB_EGG_SPECIES, GB_EGG_DV_ATK_DEF - GB_EGG_SPECIES + 2)
        species = data[0]
        dv_off = GB_EGG_DV_ATK_DEF - GB_EGG_SPECIES
        return species, parse_dvs(data[dv_off], data[dv_off + 1])

    def party(self):
        total_len = (GB_PARTY_MON1 - GB_PARTY_COUNT) + (6 * GB_PARTY_MON_SIZE)
        data = self.read_gb(GB_PARTY_COUNT, total_len)
        count = data[0]
        mons = []
        base_off = GB_PARTY_MON1 - GB_PARTY_COUNT
        for slot in range(min(count, 6)):
            start = base_off + slot * GB_PARTY_MON_SIZE
            mon = data[start:start + GB_PARTY_MON_SIZE]
            if len(mon) != GB_PARTY_MON_SIZE:
                break
            species = mon[0]
            dvs = parse_dvs(mon[0x15], mon[0x16])
            mons.append({
                "slot": slot + 1,
                "species": species,
                "dvs": dvs,
                "friendship": mon[0x1B],
                "level": mon[0x1F],
                "status": mon[0x20],
                "hp": int.from_bytes(mon[0x22:0x24], "big"),
                "max_hp": int.from_bytes(mon[0x24:0x26], "big"),
            })
        return count, mons


def dv_text(dvs: DVs) -> str:
    return (
        f"A/D/Spe/Spc/HP={dvs.attack}/{dvs.defense}/{dvs.speed}/{dvs.special}/{dvs.hp} "
        f"raw={dvs.raw_atkdef:02X}{dvs.raw_spespc:02X} "
        f"SHINY={'YES' if dvs.shiny else 'no'}"
    )


def print_snapshot(reader: CrystalReader, raw: bool = False) -> None:
    tid = reader.trainer_id()
    print(f"Trainer ID: {tid} (0x{tid:04X})")

    count, party = reader.party()
    print(f"Party count: {count}" + ("  [INVALID > 6]" if count > 6 else ""))
    for mon in party:
        print(
            f"  Slot {mon['slot']}: {species_name(mon['species'])} #{mon['species']}  "
            f"Lv{mon['level']}  HP {mon['hp']}/{mon['max_hp']}  "
            f"Friendship {mon['friendship']}  {dv_text(mon['dvs'])}"
        )

    wild_species, wild_dvs = reader.wild()
    wild_state = "valid/stale buffer" if 1 <= wild_species <= 251 else "inactive/invalid buffer"
    print(f"Wild buffer: {species_name(wild_species)} #{wild_species}  {dv_text(wild_dvs)}  [{wild_state}]")

    egg_species, egg_dvs = reader.egg()
    egg_state = "generated/stale buffer" if 1 <= egg_species <= 251 else "inactive/invalid buffer"
    print(f"Egg buffer:  {species_name(egg_species)} #{egg_species}  {dv_text(egg_dvs)}  [{egg_state}]")

    if raw:
        print("Address map:")
        for label, gb in (
            ("Trainer ID", GB_TRAINER_ID),
            ("Wild species", GB_WILD_SPECIES),
            ("Wild DVs", GB_WILD_DV_ATK_DEF),
            ("Party count", GB_PARTY_COUNT),
            ("Party mon 1", GB_PARTY_MON1),
            ("Egg species", GB_EGG_SPECIES),
            ("Egg DVs", GB_EGG_DV_ATK_DEF),
        ):
            print(f"  {label:12s}: GB 0x{gb:04X} -> 3DS 0x{reader.native_address(gb):08X}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Pokebot3DS-CFW Pokémon Crystal VC read-only RAM probe")
    ap.add_argument("host", help="3DS IP address")
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--watch", action="store_true", help="continuously refresh RAM snapshot")
    ap.add_argument("--interval", type=float, default=0.5, help="watch refresh interval in seconds")
    ap.add_argument("--raw", action="store_true", help="show GB -> 3DS mapped addresses")
    args = ap.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    print(f"Target: {args.host}:{PORT}")

    try:
        _, _, ping = require_ok("PING", request(sock, args.host, CMD_PING))
        print(f"PING: PASS {ping.decode('ascii', errors='replace')}")

        try:
            _, _, payload = require_ok("GAME_INFO", request(sock, args.host, CMD_GAME_INFO))
        except RuntimeError as exc:
            if "GAME_NOT_FOUND" in str(exc):
                raise RuntimeError(
                    "Crystal is running but this boot.firm may not include Crystal VC target support. "
                    "Use the Gen 2 Crystal probe boot.firm."
                ) from exc
            raise

        if len(payload) != GAME_INFO.size:
            raise RuntimeError(f"GAME_INFO payload size {len(payload)} != {GAME_INFO.size}")
        title_id, pid, raw_name, flags = GAME_INFO.unpack(payload)
        process_name = raw_name.split(b"\0", 1)[0].decode("ascii", errors="replace")
        print(f"GAME_INFO: title=0x{title_id:016X} pid={pid} process={process_name} flags=0x{flags:08X}")
        if title_id != CRYSTAL_EN_TID:
            raise RuntimeError(
                f"Expected English Crystal VC title 0x{CRYSTAL_EN_TID:016X}, got 0x{title_id:016X}"
            )

        reader = CrystalReader(sock, args.host)
        print(f"Crystal WRAM mapping: 3DS 0x{VC_GB_BASE:08X} + GB address")

        if not args.watch:
            print_snapshot(reader, args.raw)
            print("PASS: Crystal VC RAM snapshot read successfully. No game RAM was written.")
            return 0

        print("Watching Crystal RAM. Press Ctrl+C to stop.")
        while True:
            print("\n" + "=" * 72)
            print_snapshot(reader, args.raw)
            time.sleep(max(0.1, args.interval))

    except KeyboardInterrupt:
        print("\nStopped.")
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
