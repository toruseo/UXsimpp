# Instruction for developers

This document is the developer instruction of UXsim++ for AI coding agents and humans.
All developers must follow this instructions strictly.

## Repository structure

This repository is for the UXsim++ (also terms as uxsimpp) package.
It is a Python package with C++ binary by pybind11.

The components of this package is as follows.

- trafficpp: A mesoscopic traffic simulator written in C++. The main code is in `traffi.cpp`.
- trafficppy: Python bindings for trafficpp. This module is intended to be imported into Python code. The main source file is `bindings.cpp`,.
- UXsim++ (also terms as uxsimpp): A mesoscopic traffic simulator for Python. It is a wrapper for trafficppy, with many additional features. The main code is in `uxsimpp.py`.

The directory structure is as follows.

- /uxsimpp : the Python module
- /uxsimpp/trafficpp : the C++ code
- /tests : Test codes for Python and C++
- /demos_and_examples : Example codes using UXsim++
- /.github : CI and other files

The important files are as follows.

- /instruction_for_developers.md : This document
- /BUILD.md : How to build
- /pypoject.toml : Project file for the Python package
- /CMakeLists.txt : Build file for C++ codes
- /uxsimpp/__init__.py : The init code of UXsim++ package
- /uxsimpp/uxsimpp.py : The main code of UXsim++ package
- /uxsimpp/trafficpp/bindings.cpp : pybind11-based binding for C++ simulator trafficpp
- /uxsimpp/trafficpp/traffi.cpp : The main code of C++ simulator trafficpp
- /uxsimpp/trafficpp/traffi.h : The header file of C++ simulator trafficpp

These structures must be preserved under any circumstances.

## Critical Files - Handle with Extra Care

Files that require special attention when modifying:
- traffi.cpp: Core simulation logic
- bindings.cpp: Python-C++ interface
- uxsimpp.py: Main Python API

## Tests - this is nessesary

When updating the C++ codes of trafficpp, always confirm that the updates pass the following C++ test first.
This C++ test needs to be executed once a certain portion of the functionality implementation is completed, even if not all tasks from the user have been completed.

```
g++ tests/test_03_gridnetwork.cpp && ./a.out
```

After confirming the test pass, always confirm that the updates pass the following Python test.
This is an integration test that confirms the soundness of the entire module of UXsim++.

```
pip install -e . && pytest tests/test_verifications.py
```

When updating the Python code of UXsim++, always confirm that the updates pass the above Python test as well.


## Coding styles

### Naming Conventions

PascalCase for classes, snake_case for functions and variables for both of Python and C++.

### Comments

Do not break a long sentence across multiple lines. 
Only insert line breaks at the end of a complete sentence.

Python docstring must be written using the Numpy style as follows.

```python
def example_function(param1, param2="default"):
    """
    Example function. Brief explanation of this function should be described here.

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter. Default is "default".

    Returns
    -------
    bool
    """
    return True
```

For pybind11 bindings, the docstring must be written in the same way as above.
For example, the following is a correct docstring for a pybind11 binding.

```cpp
py::function("example_function", &example_function, 
    py::arg("param1"), py::arg("param2") = "default",
    R"docstring(
    Example function. Brief explanation of this function should be described here.

    Parameters
    ----------
    param1 : int
        The first parameter.
    param2 : str
        The second parameter. Default is "default".

    Returns
    -------
    bool
    )docstring");
```

For C++ codes, the code must follow the Doxygen style.
The function documentation must be written in the following way.

```cpp
/**
 * @brief Example function. Brief explanation of this function should be described here.
 * 
 * @param param1 The first parameter.
 * @param param2 The second parameter. Default is "default".
 * @return bool
 */
bool example_function(int param1, string param2 = "default") {
    return true;
}
```

## Other tips

- Adding new dependencies is not recommended. Requests users permission if necessary.
- Comments should be simple and concise. Simple codes do not require comments.
- Let the code fail fast with standard Python/C++ errors unless absolutely necessary. Avoid try-catch blocks or defensive programming with if-checks before operations
