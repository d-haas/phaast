from setuptools import setup, Extension
from Cython.Build import cythonize

extensions = [
    Extension("phaast.vector", sources = ["src/phaast/vector.pyx"], include_dirs = ["src", "src/phaast"]),
    Extension("phaast.structure.test_vec", sources = ["src/phaast/structure/test_vec.pyx"], include_dirs = ["src", "src/phaast"]),
]

setup(
    ext_modules=cythonize(
        extensions,
        language_level = 3,
        include_path = ["src", "src/phaast"],
        #force = True,
    )
)
