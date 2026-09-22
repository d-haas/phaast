# GET-PHAAST

An acronym for Phaast Heuristic Algorithm for Atomic Structure Tuning, is a
software developed with the intention of providing a readable and modular
library to execute a set of heuristic algorithms for global-minima search

## Instalation instructions

- **Creating a Python virtual environment**:

Install a python environment manager or create a virtual environment with
python's built-in *venv* module.
Pyenv is recommended for its simplicity, instalation and usage instructions are
available in its [Repo](https://github.com/pyenv/pyenv)

- **Installing dependencies**:

GET-PHAAST only needs cython as mandatory dependency so, for the headless usage
of phaast, it can be installed in your virtual environment with:

```
pip install cython
```

If the GUI is needed, then a full dependency command is installed as:

```
pip install cython pyopengl pyopengl-accelerate pyopengltk
```

- **Installing GET-PHAAST**:

Then the framework is simply installed using pip in the repository, for example:

```
pip install .
```

If your workdir is the repository directory.
