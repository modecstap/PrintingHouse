from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Type

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase, DeclarativeMeta


class BaseMapper:
    def __init__(
            self,
            model_type: Type[BaseModel],
            entity_type: Type[DeclarativeBase]
    ):
        self._model_type: Type[BaseModel] = model_type
        self._entity_type: Type[DeclarativeBase] = entity_type

    def model_to_entity(self, model: BaseModel):
        """Преобразует Pydantic-модель в ORM-сущность (включая вложенные модели)."""
        return self._convert_model(model, self._entity_type)

    def _convert_model(self, model: BaseModel, entity_cls: DeclarativeMeta):
        """Рекурсивно преобразует Pydantic-модель в ORM-объект."""
        data = {}
        for field_name in model.__fields__:
            value = getattr(model, field_name)
            data[field_name] = self._convert_value(value)
        return entity_cls(**data)

    def _convert_value(self, value):
        """Рекурсивная конвертация значений."""
        # Примитивы, Enum, Decimal, datetime и т.п. оставляем как есть
        if value is None or isinstance(value, (int, float, str, bool, bytes, Decimal, datetime, Enum)):
            return value

        # Вложенная Pydantic-модель → ORM-сущность
        if isinstance(value, BaseModel):
            entity_cls = self._resolve_entity_class(value)
            return self._convert_model(value, entity_cls)

        # Список → список ORM-сущностей
        if isinstance(value, list):
            return [self._convert_value(v) for v in value]

        # Словарь → рекурсивно обрабатываем значения
        if isinstance(value, dict):
            return {k: self._convert_value(v) for k, v in value.items()}

        # Остальные типы — без изменений
        return value

    def _resolve_entity_class(self, model: BaseModel):
        """
        Определяет ORM-класс по имени Pydantic-модели.
        Пример: PrintingCostReport → PrintingCostReportEntity
        """
        model_name = model.__class__.__name__
        entity_name = f"{model_name}Entity"

        from backend.storage.tables import __dict__ as entities
        if entity_name not in entities:
            raise ValueError(f"Не удалось найти ORM-класс '{entity_name}' для модели '{model_name}'")
        return entities[entity_name]

    def models_to_entities(self, models: list[BaseModel]):
        return [self.model_to_entity(model) for model in models]

    def entity_to_model(self, entity: DeclarativeMeta) -> BaseModel:
        """Преобразует ORM-сущность в Pydantic-модель."""

        return self._convert_entity(self._model_type, entity)

    def _convert_entity(self, model, entity):
        data = {}
        for field in model.__fields__:
            value = getattr(entity, field, None)
            data[field] = self._convert_entity_value(value)
        return model(**data)

    def _convert_entity_value(self, value):
        """Рекурсивно конвертирует ORM-сущности в Pydantic-модели."""  # можно сделать registry

        if value is None or isinstance(value, (int, float, str, bool, Decimal, datetime)):
            return value

        # Если это ORM-сущность, ищем соответствующую Pydantic-модель
        if hasattr(value, '__table__'):
            model_cls = self._resolve_model_class(value)
            return model_cls(**self._convert_entity(model_cls, value).model_dump())

        # Если список ORM-сущностей
        if isinstance(value, list):
            return [self._convert_entity_value(v) for v in value]

        # Если словарь с ORM-сущностями
        if isinstance(value, dict):
            return {k: self._convert_entity_value(v) for k, v in value.items()}

        return value

    def _resolve_model_class(self, entity: DeclarativeMeta) -> BaseModel:
        """
        Находит Pydantic-модель по ORM-сущности.
        Например: PrintingCostReportEntity → PrintingCostReport
        """
        entity_name = entity.__class__.__name__
        if not entity_name.endswith("Entity"):
            raise ValueError(f"Неправильное имя ORM-класса: {entity_name}")
        model_name = entity_name[:-6]  # убираем "Entity"
        from backend.models import __dict__ as models
        if model_name not in models:
            raise ValueError(f"Не найден Pydantic-класс {model_name}")
        return models[model_name]

    def entities_to_models(self, entities: list[DeclarativeBase]) -> list[BaseModel]:
        return [self.entity_to_model(entity) for entity in entities]
