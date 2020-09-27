cmake_minimum_required (VERSION 3.2)
project (CPPConverter LANGUAGES CXX)
set(CMAKE_BUILD_TYPE Debug)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)



####
## export C_INCLUDE_PATH=/usr/local/include
## export CPLUS_INCLUDE_PATH=/usr/local/include

# clear an error when using cmake in macOS
if (${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
    set(CMAKE_MACOSX_RPATH 1)
    # Fix linking on 10.14+. See https://stackoverflow.com/questions/54068035
    LINK_DIRECTORIES(/usr/local/lib)
    # a temporary fix for mac
    SET(CMAKE_C_FLAGS_DEBUG " -L/usr/local/lib -lglib-2.0 -lintl -Wno-unused-command-line-argument")
endif()



file(GLOB ALL_SRC ${PROJECT_SOURCE_DIR}/*.cpp)
add_executable(CPPConverter ${ALL_SRC})
target_link_libraries(CPPConverter pthread)

