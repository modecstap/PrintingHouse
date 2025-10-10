from typing import Type, TypeVar, cast

from src.storage.factories.repository_factory.repository_config import RepositoryConfig
from src.storage.repositories import BaseRepository
from src.storage.tables import MaterialList, Order, Product, Station, Transaction, TypeInfo, UsedTransactionList

T = TypeVar("T", bound=BaseRepository)


class RepositoryFactory:
    _repository_classes: dict[str, tuple[Type[BaseRepository], RepositoryConfig]] = {}
    _instances: dict[str, BaseRepository] = {}
    _required: set[str] = {
        "material_list",
        "order",
        "product",
        "station",
        "transaction",
        "type_info",
        "used_transaction"
    }

    @classmethod
    def initialize(cls):
        cls.register(RepositoryConfig("material_list", MaterialList), BaseRepository)
        cls.register(RepositoryConfig("order", Order), BaseRepository)
        cls.register(RepositoryConfig("product", Product), BaseRepository)
        cls.register(RepositoryConfig("station", Station), BaseRepository)
        cls.register(RepositoryConfig("transaction", Transaction), BaseRepository)
        cls.register(RepositoryConfig("type_info", TypeInfo), BaseRepository)
        cls.register(RepositoryConfig("used_transaction", UsedTransactionList), BaseRepository)

    @classmethod
    def register(cls, configuration: RepositoryConfig, repository_cls: Type[BaseRepository]):
        cls._repository_classes[configuration.name] = (repository_cls, configuration)

    @classmethod
    def repository_registration_decorator(cls, configuration: RepositoryConfig):
        def decorator(repository_cls: Type[BaseRepository]):
            RepositoryFactory.register(configuration, repository_cls)
            return repository_cls

        return decorator

    @classmethod
    def get_repository_as(cls, name: str, expected_cls: Type[T]) -> T:
        repo = cls.get_repository(name)
        if not isinstance(repo, expected_cls):
            raise TypeError(
                f"Репозиторий '{name}' должен быть экземпляром {expected_cls.__name__}, "
                f"но получен {type(repo).__name__}"
            )
        return cast(T, repo)

    @classmethod
    def get_repository(cls, repository_name: str) -> BaseRepository:
        if repository_name not in cls._repository_classes:
            raise ValueError(f"Репозиторий '{repository_name}' не зарегистрирован")

        if repository_name not in cls._instances:
            repository_cls, configuration = cls._repository_classes[repository_name]
            cls._instances[repository_name] = repository_cls(configuration.entity)

        return cls._instances[repository_name]

    @classmethod
    def validate_required(cls):
        missing = cls._required - cls._repository_classes.keys()
        if missing:
            raise RuntimeError(f"Не зарегистрированы обязательные репозитории: {', '.join(sorted(missing))}")

    @classmethod
    def clear(cls):
        cls._repository_classes.clear()
        cls._instances.clear()

    @classmethod
    def list_registered(cls) -> list[str]:
        return list(cls._repository_classes.keys())
