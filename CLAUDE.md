# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UXsim++ is a fast mesoscopic traffic simulator written in C++ with Python bindings.

**Architecture**: Three-layer design
- `trafficpp/traffi.cpp` + `traffi.h`: C++ simulation core
- `trafficpp/bindings.cpp`: pybind11 Python bindings  
- `uxsimpp.py`: High-level Python API wrapper

## Essential Commands

### Development Setup
```bash
# Create virtual environment and install development dependencies
python -m venv venv && source venv/bin/activate
pip install scikit-build-core pybind11 cmake ninja pytest build

# Development installation (editable)
pip install -e .
```

### Testing
```bash
# Run C++ unit tests first (must pass before Python tests)
g++ tests/test_03_gridnetwork.cpp -o test03 && ./test03

# Run Python integration and verification tests 
pytest tests/test_verification.py -v

# Run tests in parallel
pytest -n auto tests/test_functions.py --durations=0 -v
```

### Building
```bash
# Build distribution packages
python -m build

# Clean rebuild (if needed)
pip uninstall uxsimpp && pip install -e .
```

## Development Workflow

1. **C++ Changes**: Modify `uxsimpp/trafficpp/traffi.cpp` or `traffi.h`
2. **Test C++**: Run C++ unit tests to verify core logic
3. **Update Bindings**: Modify `uxsimpp/trafficpp/bindings.cpp` if new C++ functions need Python exposure
4. **Rebuild**: `pip install -e .` to recompile C++ extensions
5. **Test Integration**: Run Python tests to verify Python-C++ integration

## Key Architecture Notes

**C++ Core Classes** (traffi.cpp):
- `World`: Main simulation container
- `Node`: Network intersections
- `Link`: Road segments connecting nodes  
- `Vehicle`: Individual vehicles with routing

**Python API** (uxsimpp.py):
- Imports C++ classes via `from . import trafficppy`
- Provides functions like `newWorld()`, `addNode()`, `addLink()`, `adddemand()`
- Additional utilities in `analyzer.py` and `utils.py`

**Critical Files for Changes**:
- `uxsimpp/trafficpp/traffi.cpp`: Core simulation algorithms
- `uxsimpp/trafficpp/bindings.cpp`: Python-C++ interface
- `uxsimpp/uxsimpp.py`: Main Python API

## Dependencies and Requirements

- **C++17** standard required
- **CMake** ≥3.15 
- **Python** ≥3.9
- **Core dependencies**: numpy, matplotlib, pillow, tqdm, scipy, pandas
- **Build dependencies**: scikit-build-core, pybind11, cmake, ninja

## Testing Strategy

Always test C++ unit tests before Python integration tests. The C++ tests are faster and will catch core logic issues early. Python tests verify the complete Python-C++ integration works correctly.

## Other tips

- Adding new dependencies is not recommended. Requests users permission if necessary.
- Comments should be simple and concise. Simple codes do not require comments.
- Let the code fail fast with standard Python/C++ errors unless absolutely necessary. Avoid try-catch blocks or defensive programming with if-checks before operations
- Do not break a long comment sentence across multiple lines. Only insert line breaks at the end of a complete sentence.