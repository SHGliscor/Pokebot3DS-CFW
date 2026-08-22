from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"overlay patch expected exactly one match, got {count}: {old[:80]!r}")
    text = text.replace(old, new, 1)


replace_once(
    "#include <CTRPluginFramework.hpp>\n",
    "#include <CTRPluginFramework.hpp>\n#include \"BridgeOverlay.hpp\"\n",
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
    '                static const char payload[] = "Pokebot3DS-3GX-v0p2";\n',
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
print("Applied Pokebot3DS v0p2 bridge status overlay patch")
