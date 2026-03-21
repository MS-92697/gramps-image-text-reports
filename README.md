# Detailed Reports with images (Gramps)

This repository implements the
* Detailed Ancestral Report with all images
* Detailed Descendant Report with all images
for Gramps v6.

## Installation

Gramps (version 6) and `make` is required. You can install the plugins
via `make install-...`. Installing into debian and flatpak based systems
is supported.

## Authors

The code is largely based on the great work of Jon Schewe who implemented
the detailed descendant report. It has been adapted to derive from the
original Gramps reports of ancestors / descendants, and abstracted to
reuse it for the ancestral report, too.

## Development

It's recommended to set up a virtual environment with `python3 -m venv .venv/`
and install `uv` there within the activated environment: `pip install uv`.