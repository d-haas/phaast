from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="vec.__init__",
        sources=["./vec/__init__.pyx"],
        #extra_compile_args=["-O3"],
    ),
    Extension(
        name="structure.creator.dot_universe",
        sources=["./structure/creator/dot_universe.py"],
    )
]

setup(
    ext_modules = cythonize(
        [
            extension
            for extension
            in extensions
            if not isinstance(extension, str)
        ]
    ),
)
