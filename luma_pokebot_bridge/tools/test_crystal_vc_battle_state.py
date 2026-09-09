#!/usr/bin/env python3
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
CMD_READ = 4

STATUS = {
    0: "OK", 1: "BAD_MAGIC", 2: "BAD_VERSION", 3: "BAD_COMMAND",
    4: "GAME_NOT_FOUND", 5: "OPEN_FAILED", 6: "QUERY_FAILED",
    7: "NOT_READABLE", 8: "RANGE_INVALID", 9: "LENGTH_INVALID",
    10: "MAP_FAILED", 11: "INTERNAL",
}

CRYSTAL_EN_TID = 0x0004000000172800
VC_GB_BASE = 0x08A23FAC

# pret/pokecrystal / PokeReader aligned WRAM symbols.
GB_BATTLE_MODE = 0xD22D      # 0 overworld, 1 wild, 2 trainer
GB_BATTLE_TYPE = 0xD230
GB_WILD_SPECIES = 0xD206
GB_WILD_DV_ATK_DEF = 0xD20C
GB_PARTY_COUNT = 0xDCD7
GB_PARTY_MON1 = 0xDCDF
GB_PARTY_MON_SIZE = 0x30

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
BATTLE_MODE_NAMES = {0: "OVERWORLD", 1: "WILD", 2: "TRAINER"}

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
        request_id = int(time.time_ns() // 1_000_000) & 0xFFFFFFFF
    pkt = REQ.pack(REQ_MAGIC, VERSION, command, request_id, argument, aux)
    sock.sendto(pkt, (host, PORT))
    data, _ = sock.recvfrom(4096)
    if len(data) < RESP.size:
        raise RuntimeError(f"short response: {len(data)} bytes")
    magic, version, status, rid, echoed_arg, result, payload_len = RESP.unpack_from(data)
    if magic != RESP_MAGIC or version != VERSION or rid != request_id:
        raise RuntimeError("invalid bridge response header")
    payload = data[RESP.size:]
    if len(payload) != payload_len:
        raise RuntimeError(f"payload mismatch: {len(payload)} != {payload_len}")
    if status != 0:
        name = STATUS.get(status, f"STATUS_{status}")
        raise RuntimeError(f"{name} result=0x{result & 0xFFFFFFFF:08X}")
    return payload

class CrystalReader:
    def __init__(self, sock: socket.socket, host: str):
        self.sock = sock
        self.host = host

    @staticmethod
    def native_address(gb_address: int) -> int:
        return VC_GB_BASE + gb_address

    def read_gb(self, gb_address: int, length: int = 1) -> bytes:
        if not 1 <= length <= 0x200:
            raise ValueError("length must be 1..0x200")
        return request(
            self.sock, self.host, CMD_READ,
            self.native_address(gb_address), length
        )

    def battle_state(self):
        data = self.read_gb(GB_BATTLE_MODE, GB_BATTLE_TYPE - GB_BATTLE_MODE + 1)
        return data[0], data[GB_BATTLE_TYPE - GB_BATTLE_MODE]

    def wild(self):
        data = self.read_gb(
            GB_WILD_SPECIES,
            GB_WILD_DV_ATK_DEF - GB_WILD_SPECIES + 2
        )
        species = data[0]
        off = GB_WILD_DV_ATK_DEF - GB_WILD_SPECIES
        return species, parse_dvs(data[off], data[off + 1])

    def party_lead(self):
        count = self.read_gb(GB_PARTY_COUNT, 1)[0]
        if count == 0 or count > 6:
            return count, None
        mon = self.read_gb(GB_PARTY_MON1, GB_PARTY_MON_SIZE)
        return count, {
            "species": mon[0],
            "level": mon[0x1F],
            "hp": int.from_bytes(mon[0x22:0x24], "big"),
            "max_hp": int.from_bytes(mon[0x24:0x26], "big"),
            "dvs": parse_dvs(mon[0x15], mon[0x16]),
        }

def dv_text(d: DVs) -> str:
    return (
        f"A/D/Spe/Spc/HP={d.attack}/{d.defense}/{d.speed}/{d.special}/{d.hp} "
        f"raw={d.raw_atkdef:02X}{d.raw_spespc:02X} "
        f"SHINY={'YES' if d.shiny else 'no'}"
    )

def snapshot(reader: CrystalReader):
    mode, battle_type = reader.battle_state()
    species, dvs = reader.wild()
    count, lead = reader.party_lead()
    return {
        "mode": mode,
        "mode_name": BATTLE_MODE_NAMES.get(mode, f"UNKNOWN({mode})"),
        "battle_type": battle_type,
        "species": species,
        "species_name": species_name(species),
        "dvs": dvs,
        "party_count": count,
        "lead": lead,
    }

def print_full(s):
    print(f"Battle mode: {s['mode']} {s['mode_name']}  battle_type=0x{s['battle_type']:02X}")
    if s["lead"] is None:
        print(f"Party count: {s['party_count']}")
    else:
        lead = s["lead"]
        print(
            f"Party lead: {species_name(lead['species'])} #{lead['species']} "
            f"Lv{lead['level']} HP {lead['hp']}/{lead['max_hp']} {dv_text(lead['dvs'])}"
        )
    state = "ACTIVE WILD" if s["mode"] == 1 else "stale/not-active"
    print(
        f"Wild buffer: {s['species_name']} #{s['species']} "
        f"{dv_text(s['dvs'])} [{state}]"
    )

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Pokebot3DS-CFW Crystal VC battle-state / fresh-wild probe"
    )
    ap.add_argument("host", help="3DS IP address")
    ap.add_argument("--timeout", type=float, default=2.0)
    ap.add_argument("--watch", action="store_true", help="watch only meaningful state changes")
    ap.add_argument("--interval", type=float, default=0.10)
    ap.add_argument("--raw", action="store_true", help="show mapped addresses")
    args = ap.parse_args()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)
        print(f"Target: {args.host}:{PORT}")

        ping = request(sock, args.host, CMD_PING)
        print(f"PING: PASS {ping.decode('ascii', errors='replace')}")

        game = request(sock, args.host, CMD_GAME_INFO)
        if len(game) != GAME_INFO.size:
            raise RuntimeError(f"GAME_INFO size {len(game)} != {GAME_INFO.size}")
        title_id, pid, raw_name, flags = GAME_INFO.unpack(game)
        name = raw_name.split(b"\0", 1)[0].decode("ascii", errors="replace")
        print(
            f"GAME_INFO: title=0x{title_id:016X} pid={pid} "
            f"process={name} flags=0x{flags:08X}"
        )
        if title_id != CRYSTAL_EN_TID:
            raise RuntimeError(
                f"Expected English Crystal VC 0x{CRYSTAL_EN_TID:016X}, "
                f"got 0x{title_id:016X}"
            )

        reader = CrystalReader(sock, args.host)
        if args.raw:
            print("Address map:")
            for label, gb in (
                ("Battle mode", GB_BATTLE_MODE),
                ("Battle type", GB_BATTLE_TYPE),
                ("Wild species", GB_WILD_SPECIES),
                ("Wild DVs", GB_WILD_DV_ATK_DEF),
            ):
                print(
                    f"  {label:12s}: GB 0x{gb:04X} -> "
                    f"3DS 0x{reader.native_address(gb):08X}"
                )

        if not args.watch:
            s = snapshot(reader)
            print_full(s)
            print("PASS: battle-state snapshot read successfully.")
            return 0

        print("Watching meaningful Crystal battle changes. Ctrl+C to stop.")
        prev_mode = None
        prev_sig = None
        encounter_no = 0

        try:
            while True:
                s = snapshot(reader)
                sig = (s["species"], s["dvs"].raw_atkdef, s["dvs"].raw_spespc)

                if s["mode"] != prev_mode:
                    print(
                        f"\nSTATE: {BATTLE_MODE_NAMES.get(prev_mode, prev_mode)}"
                        f" -> {s['mode_name']}"
                    )

                if s["mode"] == 1 and (prev_mode != 1 or sig != prev_sig):
                    encounter_no += 1
                    print(
                        f"ACTIVE WILD #{encounter_no}: "
                        f"{s['species_name']} #{s['species']} "
                        f"{dv_text(s['dvs'])}"
                    )
                    if s["dvs"].shiny:
                        print(">>> SHINY WILD DETECTED FROM RAM <<<")

                if s["mode"] == 2 and prev_mode != 2:
                    print("ACTIVE TRAINER BATTLE")

                prev_mode = s["mode"]
                prev_sig = sig
                time.sleep(max(0.05, args.interval))
        except KeyboardInterrupt:
            print("\nStopped.")
            return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except socket.timeout:
        print("FAIL: timed out waiting for UDP response", file=sys.stderr)
        raise SystemExit(2)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(3)
