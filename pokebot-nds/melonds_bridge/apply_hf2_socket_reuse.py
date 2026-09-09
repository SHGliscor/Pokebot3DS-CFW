#!/usr/bin/env python3
from pathlib import Path
import sys


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected one match, got {n}")
    return text.replace(old, new, 1)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: apply_hf2_socket_reuse.py <melonDS-switch-upscale-folder>")
        return 2

    root = Path(sys.argv[1]).resolve()
    cpp = root / "src/frontend/switch/PokebotBridge.cpp"
    maincpp = root / "src/frontend/switch/main.cpp"

    text = cpp.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "Thread ServerThread{};\nbool ThreadCreated = false;\nstd::atomic<bool> Running{false};",
        "Thread ServerThread{};\nbool ThreadCreated = false;\nbool SocketOwned = false;\nstd::atomic<int> ServerStatus{0}; // 0=stopped, 1=starting, 2=listening, negative=error\nstd::atomic<bool> Running{false};",
        "bridge globals",
    )

    text = replace_once(
        text,
        '        std::printf("PokebotBridge: socket() failed: %d\\n", errno);\n        Running.store(false, std::memory_order_release);',
        '        std::printf("PokebotBridge: socket() failed: %d\\n", errno);\n        ServerStatus.store(-1, std::memory_order_release);\n        Running.store(false, std::memory_order_release);',
        "socket failure status",
    )
    text = replace_once(
        text,
        '        ListenSocket.store(-1, std::memory_order_release);\n        Running.store(false, std::memory_order_release);\n        return;\n    }\n\n    if (listen(server, 1) < 0)',
        '        ListenSocket.store(-1, std::memory_order_release);\n        ServerStatus.store(-2, std::memory_order_release);\n        Running.store(false, std::memory_order_release);\n        return;\n    }\n\n    if (listen(server, 1) < 0)',
        "bind failure status",
    )
    text = replace_once(
        text,
        '        ListenSocket.store(-1, std::memory_order_release);\n        Running.store(false, std::memory_order_release);\n        return;\n    }\n\n    std::printf("PokebotBridge: listening on TCP %u\\n", Port);',
        '        ListenSocket.store(-1, std::memory_order_release);\n        ServerStatus.store(-3, std::memory_order_release);\n        Running.store(false, std::memory_order_release);\n        return;\n    }\n\n    ServerStatus.store(2, std::memory_order_release);\n    std::printf("PokebotBridge: listening on TCP %u\\n", Port);',
        "listen failure/status",
    )

    old_init = '''bool Init()\n{\n    if (Running.load(std::memory_order_acquire))\n        return true;\n\n    Result rc = socketInitializeDefault();\n    if (R_FAILED(rc))\n    {\n        std::printf("PokebotBridge: socketInitializeDefault failed: 0x%08X\\n", rc);\n        return false;\n    }\n\n    State.store(CommandState::Idle, std::memory_order_release);\n    Running.store(true, std::memory_order_release);\n\n    rc = threadCreate(&ServerThread, ServerMain, nullptr, nullptr, 0x10000, 0x2C, -2);\n    if (R_FAILED(rc))\n    {\n        std::printf("PokebotBridge: threadCreate failed: 0x%08X\\n", rc);\n        Running.store(false, std::memory_order_release);\n        socketExit();\n        return false;\n    }\n\n    ThreadCreated = true;\n    threadStart(&ServerThread);\n    return true;\n}\n'''

    new_init = '''bool Init()\n{\n    if (ServerStatus.load(std::memory_order_acquire) == 2)\n        return true;\n\n    Result rc = socketInitializeDefault();\n    SocketOwned = R_SUCCEEDED(rc);\n    if (R_FAILED(rc))\n    {\n        // melonDS networking (for example cURL/RetroAchievements) may already own\n        // libnx's socket driver. In that case socketInitializeDefault returns\n        // AlreadyInitialized, but BSD sockets are usable and must be reused.\n        int probe = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);\n        if (probe < 0)\n        {\n            std::printf("PokebotBridge: socket init unavailable: rc=0x%08X errno=%d\\n", rc, errno);\n            return false;\n        }\n        close(probe);\n        std::printf("PokebotBridge: reusing existing libnx socket service (rc=0x%08X)\\n", rc);\n    }\n\n    State.store(CommandState::Idle, std::memory_order_release);\n    ServerStatus.store(1, std::memory_order_release);\n    Running.store(true, std::memory_order_release);\n\n    rc = threadCreate(&ServerThread, ServerMain, nullptr, nullptr, 0x10000, 0x2C, -2);\n    if (R_FAILED(rc))\n    {\n        std::printf("PokebotBridge: threadCreate failed: 0x%08X\\n", rc);\n        ServerStatus.store(-4, std::memory_order_release);\n        Running.store(false, std::memory_order_release);\n        if (SocketOwned) socketExit();\n        SocketOwned = false;\n        return false;\n    }\n\n    ThreadCreated = true;\n    threadStart(&ServerThread);\n\n    // Do not report success merely because the thread was created. Wait until\n    // bind()+listen() really succeeded, otherwise the PC only sees ECONNREFUSED.\n    for (int i = 0; i < 200; ++i)\n    {\n        int status = ServerStatus.load(std::memory_order_acquire);\n        if (status == 2)\n            return true;\n        if (status < 0 || !Running.load(std::memory_order_acquire))\n            break;\n        svcSleepThread(10000000); // 10 ms, maximum startup wait ~2 s\n    }\n\n    std::printf("PokebotBridge: listener startup failed, status=%d\\n",\n        ServerStatus.load(std::memory_order_acquire));\n    Running.store(false, std::memory_order_release);\n    int server = ListenSocket.load(std::memory_order_acquire);\n    if (server >= 0) shutdown(server, SHUT_RDWR);\n    if (ThreadCreated)\n    {\n        threadWaitForExit(&ServerThread);\n        threadClose(&ServerThread);\n        ThreadCreated = false;\n    }\n    if (SocketOwned) socketExit();\n    SocketOwned = false;\n    return false;\n}\n'''
    text = replace_once(text, old_init, new_init, "Init replacement")

    text = replace_once(
        text,
        "    RemotePressedMask = 0;\n    RemoteFramesRemaining = 0;\n    socketExit();\n}",
        "    RemotePressedMask = 0;\n    RemoteFramesRemaining = 0;\n    ServerStatus.store(0, std::memory_order_release);\n    if (SocketOwned) socketExit();\n    SocketOwned = false;\n}",
        "socket ownership deinit",
    )

    cpp.write_text(text, encoding="utf-8")

    m = maincpp.read_text(encoding="utf-8")
    m = replace_once(
        m,
        "    PokebotBridge::Init();\n}\n\nvoid DeInit()",
        "    const bool pokebotBridgeReady = PokebotBridge::Init();\n    g_notification.Show(pokebotBridgeReady\n        ? \"Pokebot-nds bridge ONLINE - TCP 4953\"\n        : \"Pokebot-nds bridge FAILED - TCP 4953\");\n}\n\nvoid DeInit()",
        "visible bridge startup status",
    )
    maincpp.write_text(m, encoding="utf-8")

    print("PASS: HF2 socket reuse + listener verification applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
