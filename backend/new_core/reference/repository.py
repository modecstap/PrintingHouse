"""Reference catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.reference.reference import Reference


__all__ = ["ReferenceRepository"]

class ReferenceRepository(Protocol):
    """Loads and stores named reference rows."""

    def take_all(self) -> tuple[Reference, ...]:
        """Returns every stored reference.
"""
        ...

    def save(self, reference: Reference) -> None:
        """Appends a new reference row.

        :param reference: the reference.
        """
        ...
