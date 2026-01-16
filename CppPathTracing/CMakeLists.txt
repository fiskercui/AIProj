cmake_minimum_required(VERSION 3.10)
project(CppPathTracing)

# 设置 C++ 标准
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 添加源文件目录
include_directories(${PROJECT_SOURCE_DIR}/src)
include_directories(${PROJECT_SOURCE_DIR}/external)

# 收集所有源文件
file(GLOB SOURCES "src/*.cpp")

# 创建可执行文件
add_executable(path_tracer ${SOURCES})

# Windows 特定设置
if(WIN32)
    # 在 Release 模式下优化
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        target_compile_options(path_tracer PRIVATE /O2)
    endif()
endif()

# 输出目录设置
set_target_properties(path_tracer PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")