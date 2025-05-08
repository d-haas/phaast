from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="vec.__init__",
        sources=["./vec/__init__.pyx"],
        #extra_compile_args=["-O3"],
    ),
    Extension(
        name="structure.creator.radi_universe",
        sources=["./structure/creator/radi_universe.pyx"],
        #extra_compile_args=["-O3"],
    ),
    Extension(
        name="structure.__init__",
        sources=["./structure/__init__.pyx"],
        #extra_compile_args=["-O2"],
    ),
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
