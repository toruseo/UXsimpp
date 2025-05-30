# Build and Distribution Instructions for the uxsimpp Package

This document outlines the steps required to build and prepare the uxsimpp package for distribution.

## Prerequisites

The following software must be installed:

- Python 3.9 or later
- C++ compiler
  - Windows: Visual Studio Build Tools
  - Linux: GCC
  - macOS: Clang
- CMake

## Setting Up the Development Environment

### Virtual Environment

```
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### Installing Required Packages

```
pip install scikit-build-core pybind11 cmake ninja pytest build
```


## Running Tests

Verify that the package functions correctly by executing the following test:

```
pytest tests/test_verification.py -v
```

## Creating Distribution Packages


### Building Source Distributions and Wheel Packages

```
python -m build
```

Executing this command will generate the following files in the `dist` directory:

- `uxsimpp-0.1.0.tar.gz` - Source distribution
- `uxsimpp-0.1.0-cp39-cp39-win_amd64.whl` - Wheel package (file name varies by platform)

## Testing the Built Package

### Uninstall Existing Package

```
pip uninstall -y uxsimpp
```

### Install the Built Wheel Package

```
pip install dist/uxsimpp-0.1.0*.whl
```

### Run Tests

```
pytest tests/test_verification.py -v
```

## Publishing to PyPI

### Install Required Tools

```
pip install twine
```

### Upload to TestPyPI (for testing purposes)

```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

### Upload to Production PyPI

```
twine upload dist/*
```
