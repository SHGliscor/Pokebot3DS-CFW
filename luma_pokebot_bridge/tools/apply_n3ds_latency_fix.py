from pathlib import Path

root = Path(__file__).resolve().parents[2] / "Luma3DS"
bridge_c = root / "sysmodules" / "rosalina" / "source" / "pokebot_ram_bridge.c"

text = bridge_c.read_text(encoding="utf-8")

# The v0p5 bridge used a lower-priority worker than Luma's native
# InputRedirection thread. Match Luma's proven 0x20 priority so the UDP/HID
# service loop is not starved on New 3DS scheduling configurations.
old_thread = """                                 0x24, CORE_SYSTEM)))"""
new_thread = """                                 0x20, CORE_SYSTEM)))"""
if old_thread not in text:
    raise SystemExit("Pokebot bridge thread-priority marker not found")
text = text.replace(old_thread, new_thread, 1)

# Avoid depending on SOC's blocking poll timeout for command latency. The
# New-3DS support probe showed a very repeatable ~100-150 ms RTT despite no
# packet failures, while an original 3DS on the same bridge behaves normally.
# Poll SOC non-blocking, then yield the ARM11 worker for 2 ms when idle. This
# keeps command dispatch and firmware-owned HID pulse expiry responsive without
# a hot busy loop.
old_poll = """        int pollres = socPoll(&pfd, 1, 20);
        if (pollres > 0 && (pfd.revents & POLLIN))
        {
            PokebotRequest req;
            struct sockaddr_in remote;
            socklen_t remoteLen = sizeof(remote);
            ssize_t n = socRecvfrom(sock, &req, sizeof(req), 0,
                                    (struct sockaddr *)&remote, &remoteLen);
            if (n < 0)
                break;
            if ((u32)n != sizeof(req))
                continue;

            pokebotRamBridgePackets++;
            Pokebot_HandleRequest(sock, &remote, remoteLen, &req);
        }
        else if (pollres < -10000)
            break;
"""
new_poll = """        int pollres = socPoll(&pfd, 1, 0);
        if (pollres > 0 && (pfd.revents & POLLIN))
        {
            PokebotRequest req;
            struct sockaddr_in remote;
            socklen_t remoteLen = sizeof(remote);
            ssize_t n = socRecvfrom(sock, &req, sizeof(req), 0,
                                    (struct sockaddr *)&remote, &remoteLen);
            if (n < 0)
                break;
            if ((u32)n != sizeof(req))
                continue;

            pokebotRamBridgePackets++;
            Pokebot_HandleRequest(sock, &remote, remoteLen, &req);
        }
        else if (pollres < -10000)
            break;
        else
            svcSleepThread(2 * 1000 * 1000LL);
"""
if old_poll not in text:
    raise SystemExit("Pokebot bridge poll-loop marker not found")
text = text.replace(old_poll, new_poll, 1)

# Make the hardware-test binary self-identifying without changing protocol
# framing or RAM read semantics.
text = text.replace('"Pokebot3DS-Luma-v0p5"', '"Pokebot3DS-Luma-v0p6-n3ds"', 1)

bridge_c.write_text(text, encoding="utf-8")
