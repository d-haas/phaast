# GET-PHAAST

**`Linux` | `Python 3.13+`**

An acronym for
GETMM's (Group's name) Phaast Heuristic Algorithm for Atomic Structure Tuning,
is a software developed with the intention of providing a readable and modular
library to execute a set of heuristic algorithms for global-minima search

- [Instalation](#instalation)
- [Running](#running)

## Instalation

### Creating a Python virtual environment

Install a python environment manager or create a virtual environment with
python's built-in *venv* module.
Pyenv is recommended for its simplicity, instalation and usage instructions are
available in its [Repo](https://github.com/pyenv/pyenv).

Python version 3.13 and above are needed and it is **HIGHLY** recommended that a
free-threaded python version is used (Example: 3.13.11t in Pyenv), or else the
structure comparison procedure total time will be higher than geometry
optimization.


### Dependencies

GET-PHAAST only needs cython as mandatory dependency so, for the headless usage
of phaast, it can be installed in your virtual environment with:

```
pip install cython
```

If the GUI is needed, then a full dependency command is installed as:

```
pip install cython pyopengl pyopengl-accelerate pyopengltk
```

[xTB](https://github.com/grimme-lab/xtb) is needed in your `$PATH` for basic
searches with the built-in genetic algorithm

Searches using the optional DFT package will also require inserting
[Orca](https://www.faccts.de/orca/) in your `$PATH`

### Installing GET-PHAAST

Then the framework is simply installed using pip in the repository, for example:
```
pip install .
```

If your workdir is the repository directory.

> A PyPI library with pre-compiled binaries will be added a little after the
repository is made public.

## Running

### Python interface
Examples are present in the `examples` directory to show how the library can be
used.

### Command-line interface (CLI)

The command-line allows a user to run GET-PHAAST's genetic algorithm with just
one obligatory flags (e.g. `phaast C6H6`).
Additional optional flags are present in the [Manual](manual.pdf)

### Graphical user interface (GUI)

The GET-PHAAST's GUI, a tool to manage structures as well as genetic algorithm
results, can be accessed through the `phaast-gui` command. 
