cmake_minimum_required(VERSION 3.15)
project(trafficppy LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# pybind11を使ったPythonバインディング
find_package(pybind11 REQUIRED CONFIG)

# ライブラリ作成
add_library(trafficppy_lib
    uxsimpp/trafficpp/traffi.cpp
)

# Pythonモジュール作成
pybind11_add_module(trafficppy
    uxsimpp/trafficpp/bindings.cpp
)
target_link_libraries(trafficppy PRIVATE trafficppy_lib)

# インストール設定
install(TARGETS trafficppy
        LIBRARY DESTINATION uxsimpp
        COMPONENT python)

# コンパイル最適化オプション
if(MSVC)
    target_compile_options(trafficppy PRIVATE /O2)
else()
    target_compile_options(trafficppy PRIVATE -O3)
endif()

# Windows Mingw環境向けスタティックリンク
if (MINGW)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -static-libgcc -static-libstdc++ -static -O3")
endif()
