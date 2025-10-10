from pydantic import BaseModel

from backend.storage.exceptions.not_found_exception import NotFoundException
from backend.storage.mappers.base_mapper import BaseMapper
from backend.storage.repositories.base import BaseRepository


class CRUDAccessor:

    def __init__(
            self,
            repository: BaseRepository,
            mapper: BaseMapper
    ):
        self._main_repository: BaseRepository = repository
        self._main_mapper: BaseMapper = mapper

    async def get_models(self) -> list[BaseModel]:
        async with self._main_repository.create_session() as session:
            entities = await self._main_repository.get_entities(session=session)
            models = self._main_mapper.entities_to_models(entities)
        return models

    async def get_model_by_id(self, entity_id: int) -> BaseModel:
        async with self._main_repository.create_session() as session:
            entity = await self._main_repository.get_entity_by_id(entity_id, session=session)
            if entity is None:
                raise NotFoundException(entity_id)
            model = self._main_mapper.entity_to_model(entity)
            return model

    async def add_models(self, models: list[BaseModel]) -> list[BaseModel]:
        async with self._main_repository.create_session() as session:
            entities = self._main_mapper.models_to_entities(models)
            inserted_entities = await self._main_repository.insert(entities, session=session)
            return self._main_mapper.entities_to_models(inserted_entities)

    async def delete_models(self, ids: list[int]):
        await self._main_repository.delete(ids)

    async def update_models(self, models: list[BaseModel]) -> list[BaseModel]:
        async with self._main_repository.create_session() as session:
            entities = self._main_mapper.models_to_entities(models)
            updated_entities = await self._main_repository.update(entities, session=session)
            return self._main_mapper.entities_to_models(updated_entities)
