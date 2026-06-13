from enum import Enum


class Permission(str, Enum):
    """Перечисление доступных прав пользователя."""
    FULL = "FULL"
    READ = "READ"
    WRITE = "WRITE"
    DELETE = "DELETE"
    NONE = "NONE"
