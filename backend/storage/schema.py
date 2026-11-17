"""Declarative base and registration of every mapped table."""

from backend.storage.base import Base

__all__ = ["Base"]
from backend.storage.equipment import tables as _equipment_tables  # noqa: F401
from backend.storage.edges import tables as _edges_tables  # noqa: F401
from backend.storage.materials import tables as _materials_tables  # noqa: F401
from backend.storage.order import tables as _order_tables  # noqa: F401
from backend.storage.part import tables as _part_tables  # noqa: F401
from backend.storage.personal import tables as _personal_tables  # noqa: F401
from backend.storage.print_run import tables as _print_run_tables  # noqa: F401
from backend.storage.reference import tables as _reference_tables  # noqa: F401
from backend.storage.user import tables as _user_tables  # noqa: F401
