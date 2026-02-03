"""
    Python implementation of P.H.A.A.S.T
    (Phaast Heuristic Algorithm for Atomic Structure Tuning)

    A framework for dynamic application of heuristic algorithms
    for global minima structures search
"""

from . import vector, structure, calculators, computer, surface_explorator

__version__ = "0.1.0"

__all__ = [
    "vector",
    "structure",
    "calculators",
    "computer",
    "surface_explorator",
    "__version__",
]
