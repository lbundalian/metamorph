"""
Metamorph - A flexible data transformation library.

This package provides tools for morphing and transforming data structures.
"""

__version__ = "0.1.0"

"""Metamorph - Medical data format transformation library."""
from .morphers import BaseMorpher, KDKToRDMorpher
from .models import KDKSchema, RDSchema
from .utils import DataValidator, RDSchemaConverter, validate_rd_file, validate_transformation_output

__version__ = "0.1.0"
__all__ = [
    "BaseMorpher", 
    "KDKToRDMorpher", 
    "KDKSchema", 
    "RDSchema",
    "DataValidator",
    "RDSchemaConverter",
    "validate_rd_file",
    "validate_transformation_output"
]