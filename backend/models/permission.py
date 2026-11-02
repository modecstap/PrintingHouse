from enum import Enum


class Permission(str, Enum):
    """Enumeration of the user's available permissions."""
    FULL = "FULL"
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    NONE = "NONE"
