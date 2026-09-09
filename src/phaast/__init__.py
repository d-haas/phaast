"""
    Python implementation of GET-PHAAST
    (Phaast Heuristic Algorithm for Atomic Structure Tuning)

    A framework for dynamic application of heuristic algorithms
    for global minima structures search
"""

from . import vector, structure, calculators, computer, surface_explorator

__version__ = "0.1.2"

__all__ = [
    "vector",
    "structure",
    "calculators",
    "computer",
    "surface_explorator",
    "__version__",
]
