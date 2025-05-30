# UXsim++ Documentation

This directory contains the Sphinx documentation for UXsim++, a fast mesoscopic traffic simulator written in C++ with Python bindings.

## Quick Start

To build the documentation:

```bash
cd docs
make html
```

The generated HTML documentation will be available in `build/html/index.html`.

## Prerequisites

### Required Packages

Install the following packages for documentation building:

```bash
pip install sphinx sphinx-autobuild furo nbsphinx recommonmark
```

Or if using system-wide installation:

```bash
pip install --break-system-packages sphinx sphinx-autobuild furo nbsphinx recommonmark
```

### System Requirements

- **Python 3.9+**
- **Sphinx 8.0+**
- **C++ compiler** (for rebuilding bindings if needed)

## Documentation Structure

```
docs/
├── source/
│   ├── conf.py              # Sphinx configuration
│   ├── index.rst            # Main documentation page
│   ├── tech_ref.rst         # Technical reference
│   ├── uxsimpp.rst          # Python API reference
│   └── _autosummary/        # Auto-generated API docs
├── build/                   # Generated documentation
├── Makefile                 # Build commands
└── README.md               # This file
```

## Building Documentation

### Standard Build

```bash
cd docs
make html
```

### GitHub Pages Build

To build and copy HTML files to `/docs/` root for GitHub Pages:

```bash
cd docs
make github-pages
```

This command:
1. Builds the documentation with `make html`
2. Copies all HTML files from `build/html/` to `/docs/` root
3. Ready for GitHub Pages publishing from `/docs` folder

### Clean Build

To rebuild everything from scratch:

```bash
cd docs
make clean
make html
# or for GitHub Pages
make clean
make github-pages
```

### Clean All Files

To clean build files AND GitHub Pages files in docs root:

```bash
cd docs
make clean-all
```

### Live Reload Development

For development with automatic rebuilding:

```bash
cd docs
sphinx-autobuild source build/html
```

Then open http://localhost:8000 in your browser.

## Documentation Features

### Auto-Generated API Documentation

The documentation automatically generates API reference from:

1. **Python Wrapper Classes** (`uxsimpp.py`):
   - `uxsimpp.World`
   - `uxsimpp.Node` 
   - `uxsimpp.Link`
   - `uxsimpp.Vehicle`

2. **C++ Bound Classes** (`trafficppy` module):
   - `uxsimpp.trafficppy.World`
   - `uxsimpp.trafficppy.Node`
   - `uxsimpp.trafficppy.Link`
   - `uxsimpp.trafficppy.Vehicle`

### Docstring Integration

All C++ methods and attributes are documented via pybind11 docstrings defined in `uxsimpp/trafficpp/bindings.cpp`.

## Updating Documentation

### Adding New Python Functions

1. Add docstrings to your Python functions in standard format
2. Documentation will be automatically included via autosummary

### Adding New C++ Bindings

1. Add pybind11 bindings in `uxsimpp/trafficpp/bindings.cpp`
2. Include docstrings as the last parameter to `.def()` calls:
   ```cpp
   .def("method_name", &Class::method_name, "Method description")
   ```
3. Rebuild the C++ extension:
   ```bash
   pip install -e .
   ```
4. Rebuild documentation:
   ```bash
   cd docs && make clean && make html
   ```

### Configuration

Key configuration options in `docs/source/conf.py`:

- **Extensions**: `sphinx.ext.autosummary`, `sphinx.ext.autodoc`, etc.
- **Theme**: `furo` (modern, clean theme)
- **Autosummary**: Automatically generates API documentation
- **Napoleon**: Supports Google/NumPy style docstrings

## Troubleshooting

### Common Issues

1. **"sphinx-build: not found"**
   - Install Sphinx: `pip install sphinx`

2. **"No module named 'uxsimpp'"**
   - Install the package: `pip install -e .` from project root

3. **Missing docstrings for C++ methods**
   - Check that docstrings are added to bindings.cpp
   - Rebuild C++ extension with `pip install -e .`

4. **Autosummary not updating**
   - Use `make clean && make html` for full rebuild

### Build Warnings

The build may show warnings about duplicate object descriptions. These are harmless and occur due to both Python wrapper and C++ bound classes being documented.

## File Organization

- **conf.py**: Main Sphinx configuration
- **index.rst**: Documentation homepage with table of contents
- **tech_ref.rst**: Technical API reference with autosummary directives
- **uxsimpp.rst**: Basic module documentation
- **_autosummary/**: Auto-generated detailed API documentation

## Contributing

When adding new features:

1. Add comprehensive docstrings to all new functions/methods
2. Update relevant .rst files if needed
3. Test documentation build with `make html`
4. Ensure no broken links or missing references

For C++ bindings, always include meaningful docstrings in the pybind11 `.def()` calls to ensure proper documentation generation.