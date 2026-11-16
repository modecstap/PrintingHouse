"""Shared catalog persistence errors."""


__all__ = ["CatalogIdOccupied"]

class CatalogIdOccupied(Exception):
    """Reports that a catalog id is already stored."""
