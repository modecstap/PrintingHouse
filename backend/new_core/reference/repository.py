"""Reference catalog contract."""

from __future__ import annotations

from typing import Protocol

from backend.new_core.reference.reference import Reference


class ReferenceRepository(Protocol):
    """Loads and stores named reference rows."""

    def take_all(self) -> tuple[Reference, ...]:
        """Returns every stored reference.

        :return: references in store order. None: an empty tuple.
        """
        ...

    def save(self, reference: Reference) -> None:
        """Appends a new reference row.

        :param reference:

        :return: nothing. Existing rows are not changed.
        """
        ...
