
from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        name="vec.__init__",
        sources=["./vec/__init__.py"],
        extra_compile_args=["-O2"],
    )
]

setup(
    ext_modules = cythonize(extensions),
)
