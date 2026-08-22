from pathlib import Path

p = Path(__file__).resolve().parents[1] / "Sources" / "Main.cpp"
text = p.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"SOC shared-memory patch expected one match, got {count}: {old[:100]!r}")
    text = text.replace(old, new, 1)


# v0p4 hardware finding:
# socInit returned E0A01BF5 (invalid address state) when given a normal plugin-heap
# allocation. 3GX socket examples allocate the SOC work area explicitly with
# Luma's custom svcControlMemoryUnsafe in the SYSTEM memory region instead.

replace_once(
    "using namespace CTRPluginFramework;\n\n",
    "using namespace CTRPluginFramework;\n\n"
    "extern \"C\" Result svcControlMemoryUnsafe(u32 *out, u32 addr0, u32 size, MemOp op, MemPerm perm);\n\n",
)

replace_once(
    "    // 3GX plugins have a much tighter heap than normal libctru applications.\n"
    "    // 64 KiB is sufficient for this tiny UDP request/reply bridge.\n"
    "    static constexpr size_t kSocBufferSize = 0x10000;\n"
    "    static bool gSocInitialized = false;\n"
    "    static bool gSrvInitialized = false;\n",
    "    // socInit requires a suitable shared-memory mapping on real 3DS hardware.\n"
    "    // v0p3 proved that a normal plugin-heap pointer is rejected with E0A01BF5.\n"
    "    static constexpr u32 kSocBufferAddress = 0x07500000u;\n"
    "    static constexpr size_t kSocBufferSize = 0x20000;\n"
    "    static bool gSocMemoryAllocated = false;\n"
    "    static bool gSocInitialized = false;\n"
    "    static bool gSrvInitialized = false;\n",
)

replace_once(
    '                static const char payload[] = "Pokebot3DS-3GX-v0p3";\n',
    '                static const char payload[] = "Pokebot3DS-3GX-v0p4";\n',
)

replace_once(
    "        if (gSocBuffer != nullptr)\n"
    "        {\n"
    "            free(gSocBuffer);\n"
    "            gSocBuffer = nullptr;\n"
    "        }\n",
    "        if (gSocMemoryAllocated)\n"
    "        {\n"
    "            u32 freed = 0;\n"
    "            svcControlMemoryUnsafe(&freed, kSocBufferAddress, kSocBufferSize,\n"
    "                                   MEMOP_FREE, MEMPERM_DONTCARE);\n"
    "            gSocMemoryAllocated = false;\n"
    "            gSocBuffer = nullptr;\n"
    "        }\n",
)

replace_once(
    '        OSD::Notify("Pokebot3DS 3GX v0p3: srvInit");\n',
    '        OSD::Notify("Pokebot3DS 3GX v0p4: srvInit");\n',
)

replace_once(
    "        gSocBuffer = static_cast<u32 *>(memalign(0x1000, kSocBufferSize));\n"
    "        if (gSocBuffer == nullptr)\n"
    "        {\n"
    "            OSD::Notify(\"Pokebot3DS: 64 KiB SOC allocation failed\");\n"
    "            gRunning = false;\n"
    "            CleanupNetwork();\n"
    "            return;\n"
    "        }\n"
    "        std::memset(gSocBuffer, 0, kSocBufferSize);\n\n"
    "        OSD::Notify(\"Pokebot3DS 3GX v0p3: socInit\");\n",
    "        OSD::Notify(\"Pokebot3DS 3GX v0p4: allocate SOC shared memory\");\n"
    "        u32 allocated = 0;\n"
    "        const Result memResult = svcControlMemoryUnsafe(\n"
    "            &allocated, kSocBufferAddress, kSocBufferSize,\n"
    "            MemOp(MEMOP_REGION_SYSTEM | MEMOP_ALLOC),\n"
    "            MemPerm(MEMPERM_READ | MEMPERM_WRITE));\n"
    "        if (R_FAILED(memResult))\n"
    "        {\n"
    "            OSD::Notify(Utils::Format(\"Pokebot3DS: SOC memory alloc failed %08lX\",\n"
    "                                     static_cast<unsigned long>(memResult)));\n"
    "            gRunning = false;\n"
    "            CleanupNetwork();\n"
    "            return;\n"
    "        }\n"
    "        gSocMemoryAllocated = true;\n"
    "        gSocBuffer = reinterpret_cast<u32 *>(kSocBufferAddress);\n"
    "        std::memset(gSocBuffer, 0, kSocBufferSize);\n\n"
    "        OSD::Notify(\"Pokebot3DS 3GX v0p4: socInit\");\n",
)

replace_once(
    '        OSD::Notify("Pokebot3DS 3GX v0p3: UDP 4952 ready");\n',
    '        OSD::Notify("Pokebot3DS 3GX v0p4: UDP 4952 ready");\n',
)

p.write_text(text, encoding="utf-8")
print("Applied Pokebot3DS v0p4 fixed SYSTEM-region SOC shared-memory patch")
