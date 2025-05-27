Python codes of *UXsim++*. 

If you want to import this directory, put `trafficppy.pyd` or `trafficppy.so` here.

Terminology on the internal structure of UXsim++:

- **trafficpp**: A mesoscopic traffic simulator written in C++. The main code is in `traffi.cpp`. It can be executed as a standalone program by doing `g++ test_03_gridnetwork_bench.cpp` where `test_03_gridnetwork_bench.cpp` is a scenario code.
- **trafficppy**: Python bindings for *trafficpp*. This module is intended to be imported into Python code. The main source file is `bindings.cpp`, and the compiled binary is `trafficppy.pyd` or`trafficppy.so`. Compilation should follow the instructions in `CMakeLists.txt`.
- **UXsim++** (or **uxsimpp**): A mesoscopic traffic simulator for Python. It is a wrapper for *trafficppy*, with many additional features. The main code is in `uxsimpp.py`. This can be build by `python -m build`.
