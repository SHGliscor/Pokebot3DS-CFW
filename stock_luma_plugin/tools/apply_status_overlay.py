from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"bridge patch expected exactly one match, got {count}: {old[:80]!r}")
    text = text.replace(old, new, 1)


# v0p2 status overlay instrumentation.
replace_once(
    "#include <CTRPluginFramework.hpp>\n",
    "#include <CTRPluginFramework.hpp>\n#include \"BridgeOverlay.hpp\"\n",
)

replace_once(
    "#include <arpa/inet.h>\n",
    "#include <arpa/inet.h>\n#include <errno.h>\n",
)

replace_once(
    "    static constexpr size_t kSocBufferSize = 0x100000;\n",
    "    // 3GX plugins have a much tighter heap than normal libctru applications.\n"
    "    // 64 KiB is sufficient for this tiny UDP request/reply bridge.\n"
    "    static constexpr size_t kSocBufferSize = 0x10000;\n"
    "    static bool gSocInitialized = false;\n"
    "    static bool gSrvInitialized = false;\n",
)

replace_once(
    "    static void SendResponse(int sock, const sockaddr_in &remote, socklen_t remoteLen,\n"
    "                             const Request &req, Status status, s32 result = 0,\n"
    "                             const void *payload = nullptr, u32 payloadLength = 0)\n"
    "    {\n",
    "    static void SendResponse(int sock, const sockaddr_in &remote, socklen_t remoteLen,\n"
    "                             const Request &req, Status status, s32 result = 0,\n"
    "                             const void *payload = nullptr, u32 payloadLength = 0)\n"
    "    {\n"
    "        BridgeOverlay::RecordStatus(static_cast<u16>(status));\n",
)

replace_once(
    "    static void HandleRequest(int sock, const sockaddr_in &remote, socklen_t remoteLen,\n"
    "                              const Request &req)\n"
    "    {\n",
    "    static void HandleRequest(int sock, const sockaddr_in &remote, socklen_t remoteLen,\n"
    "                              const Request &req)\n"
    "    {\n"
    "        BridgeOverlay::RecordPacket(req.command);\n",
)

replace_once(
    '                static const char payload[] = "Pokebot3DS-3GX-v0p1";\n',
    '                static const char payload[] = "Pokebot3DS-3GX-v0p3";\n',
)

replace_once(
    "                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, data, req.aux);\n",
    "                BridgeOverlay::RecordRead(req.argument, req.aux);\n"
    "                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, data, req.aux);\n",
)

replace_once(
    "                const Status status = StartInput(req, kind, input);\n"
    "                SendResponse(sock, remote, remoteLen, req, status,\n",
    "                const Status status = StartInput(req, kind, input);\n"
    "                BridgeOverlay::RecordInput(req.command, req.argument, req.aux, req.requestId,\n"
    "                                           static_cast<u16>(status));\n"
    "                SendResponse(sock, remote, remoteLen, req, status,\n",
)

replace_once(
    "                gInput = ActiveInput{};\n"
    "                LightLock_Unlock(&gInputLock);\n"
    "                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &input, sizeof(input));\n",
    "                gInput = ActiveInput{};\n"
    "                LightLock_Unlock(&gInputLock);\n"
    "                BridgeOverlay::RecordRelease(req.requestId);\n"
    "                SendResponse(sock, remote, remoteLen, req, STATUS_OK, 0, &input, sizeof(input));\n",
)

# v0p3: initialize srv: before SOC, reduce the aligned SOC work buffer,
# retry socket creation briefly and bind to the console's actual Wi-Fi address.
server_start = text.find("    static void ServerThreadMain(void *)\n")
server_end = text.find("    static bool Start()\n", server_start)
if server_start < 0 or server_end < 0:
    raise SystemExit("bridge patch could not locate ServerThreadMain/Start markers")

network_block = r'''    static void CleanupNetwork()
    {
        if (gSocket >= 0)
        {
            close(gSocket);
            gSocket = -1;
        }

        if (gSocInitialized)
        {
            socExit();
            gSocInitialized = false;
        }

        if (gSocBuffer != nullptr)
        {
            free(gSocBuffer);
            gSocBuffer = nullptr;
        }

        if (gSrvInitialized)
        {
            srvExit();
            gSrvInitialized = false;
        }
    }

    static void ServerThreadMain(void *)
    {
        OSD::Notify("Pokebot3DS 3GX v0p3: srvInit");
        const Result srvResult = srvInit();
        if (R_FAILED(srvResult))
        {
            OSD::Notify(Utils::Format("Pokebot3DS: srvInit failed %08lX",
                                     static_cast<unsigned long>(srvResult)));
            gRunning = false;
            return;
        }
        gSrvInitialized = true;

        gSocBuffer = static_cast<u32 *>(memalign(0x1000, kSocBufferSize));
        if (gSocBuffer == nullptr)
        {
            OSD::Notify("Pokebot3DS: 64 KiB SOC allocation failed");
            gRunning = false;
            CleanupNetwork();
            return;
        }
        std::memset(gSocBuffer, 0, kSocBufferSize);

        OSD::Notify("Pokebot3DS 3GX v0p3: socInit");
        const Result socResult = socInit(gSocBuffer, kSocBufferSize);
        if (R_FAILED(socResult))
        {
            OSD::Notify(Utils::Format("Pokebot3DS: socInit failed %08lX",
                                     static_cast<unsigned long>(socResult)));
            gRunning = false;
            CleanupNetwork();
            return;
        }
        gSocInitialized = true;

        for (int attempt = 0; attempt < 15 && gSocket < 0; ++attempt)
        {
            gSocket = socket(AF_INET, SOCK_DGRAM, 0);
            if (gSocket < 0)
                svcSleepThread(100000000LL); // 100 ms
        }
        if (gSocket < 0)
        {
            OSD::Notify(Utils::Format("Pokebot3DS: UDP socket failed errno=%d", errno));
            gRunning = false;
            CleanupNetwork();
            return;
        }

        sockaddr_in local{};
        local.sin_family = AF_INET;
        local.sin_port = htons(kPort);
        local.sin_addr.s_addr = gethostid();

        if (bind(gSocket, reinterpret_cast<sockaddr *>(&local), sizeof(local)) < 0)
        {
            OSD::Notify(Utils::Format("Pokebot3DS: UDP 4952 bind failed errno=%d", errno));
            gRunning = false;
            CleanupNetwork();
            return;
        }

        OSD::Notify("Pokebot3DS 3GX v0p3: UDP 4952 ready");

        while (gRunning)
        {
            Request req{};
            sockaddr_in remote{};
            socklen_t remoteLen = sizeof(remote);
            const int received = recvfrom(gSocket, &req, sizeof(req), 0,
                                          reinterpret_cast<sockaddr *>(&remote), &remoteLen);
            if (received < 0)
            {
                if (!gRunning)
                    break;
                svcSleepThread(10000000LL); // 10 ms
                continue;
            }
            if (received != static_cast<int>(sizeof(req)))
                continue;
            HandleRequest(gSocket, remote, remoteLen, req);
        }

        CleanupNetwork();
    }

'''
text = text[:server_start] + network_block + text[server_end:]

replace_once(
    "        LightLock_Init(&gInputLock);\n"
    "        gInput = ActiveInput{};\n",
    "        LightLock_Init(&gInputLock);\n"
    "        BridgeOverlay::Init();\n"
    "        OSD::Run(BridgeOverlay::Draw);\n"
    "        gInput = ActiveInput{};\n",
)

replace_once(
    "        gRunning = false;\n"
    "        LightLock_Lock(&gInputLock);\n",
    "        gRunning = false;\n"
    "        OSD::Stop(BridgeOverlay::Draw);\n"
    "        LightLock_Lock(&gInputLock);\n",
)

p.write_text(text, encoding="utf-8")
print("Applied Pokebot3DS v0p3 status overlay + SOC initialization patch")
