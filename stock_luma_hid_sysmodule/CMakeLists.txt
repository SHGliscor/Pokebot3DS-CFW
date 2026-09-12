cmake_minimum_required(VERSION 3.12)

project(PokebotHidSysmodule C)

set(SYSMODULE_TITLEID "0004013000B0B702")
set(SYSMODULE_TARGET "pokebot-hid-sys")

add_executable(${SYSMODULE_TARGET}
    source/main.c
    source/base_heap.c
)

target_compile_features(${SYSMODULE_TARGET} PRIVATE c_std_11)
target_compile_options(${SYSMODULE_TARGET} PRIVATE
    -Wall
    -Wextra
    -Werror
    -O2
)

find_program(MAKEROM_EXE makerom REQUIRED)

set(CXI_OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${SYSMODULE_TITLEID}.cxi")
add_custom_command(
    OUTPUT "${CXI_OUTPUT}"
    COMMAND ${MAKEROM_EXE}
        -f ncch
        -nocodepadding
        -o "${CXI_OUTPUT}"
        -rsf "${CMAKE_CURRENT_SOURCE_DIR}/PokebotHidSysmodule.rsf"
        -elf "$<TARGET_FILE:${SYSMODULE_TARGET}>"
    DEPENDS ${SYSMODULE_TARGET} "${CMAKE_CURRENT_SOURCE_DIR}/PokebotHidSysmodule.rsf"
    COMMENT "Building Luma3DS external sysmodule ${SYSMODULE_TITLEID}.cxi"
    VERBATIM
)

add_custom_target(${SYSMODULE_TARGET}_cxi ALL DEPENDS "${CXI_OUTPUT}")
