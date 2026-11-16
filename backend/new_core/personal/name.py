"""Validates stripped non-empty names for catalog entities."""

from backend.new_core.errors import InvalidInput


__all__ = ["stripped_required_name"]

def stripped_required_name(name: str, subject: str) -> str:
    """Returns the stripped name or rejects an empty result.

    :param name: raw name text.
    :param subject: label for :class:`InvalidInput`.

    :raises InvalidInput: when the stripped name is empty.

    :return: the str result.
    """
    stripped = name.strip()
    if not stripped:
        raise InvalidInput(subject=subject, reason="название не задано")
    return stripped
