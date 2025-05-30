# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# GitHub Pages target: build HTML and copy to docs root
github-pages: html
	@echo "Copying HTML files for GitHub Pages..."
	@cp -r build/html/* .
	@echo "HTML files copied to docs/ root for GitHub Pages"

# Clean including GitHub Pages files
clean-all: clean
	@echo "Cleaning GitHub Pages files..."
	@rm -f *.html *.js
	@rm -rf _static _sources
	@rm -f .buildinfo
	@echo "GitHub Pages files cleaned"
