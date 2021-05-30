cmake_minimum_required(VERSION 3.12)

set(CMAKE_C_COMPILER /usr/bin/clang)

option(ENABLE_TEST OFF)

set(BPF_OUTPUT_DIR ${CMAKE_BINARY_DIR}/bpf/
    CACHE STRING "Output dir for eBPF object files")

set(OPENWRT_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/../../openwrt/staging_dir/target-mips_24kc_musl/usr/include/"
    CACHE STRING "Include dir of targeted OpenWRT build")

set(TARGET_BPF "udp_broadcast_bridge_kern")
set(TARGET_OBJ "obj")

project(${TARGET_BPF} C)

add_library(${TARGET_BPF} OBJECT)

target_sources(${TARGET_BPF} PRIVATE
    "${CMAKE_SOURCE_DIR}/src/xdp_drop_kern.c")

if(ENABLE_TEST)
    message("-- Compiling bpf modules for current kernel")
    target_compile_options(${TARGET_BPF} PRIVATE -O2 -Wall -target bpf)
else()
    message("-- Compiling bpf modules for OpenWRT kernel")
    target_compile_options(${TARGET_BPF} PRIVATE -O2 -Wall -target bpfeb) # big endian
    target_include_directories(${TARGET_BPF} PRIVATE ${OPENWRT_INCLUDE_DIR})
endif()

add_custom_command(OUTPUT ${BPF_OUTPUT_DIR}
    COMMAND mkdir -p ${BPF_OUTPUT_DIR}
    COMMAND cp $<TARGET_OBJECTS:${TARGET_BPF}> ${BPF_OUTPUT_DIR})

add_custom_target(${TARGET_OBJ} ALL DEPENDS ${BPF_OUTPUT_DIR})
add_dependencies(${TARGET_OBJ} ${TARGET_BPF})
