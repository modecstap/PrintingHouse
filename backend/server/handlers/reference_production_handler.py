from backend.models import Production
from backend.storage.mappers.base_mapper import BaseMapper
from backend.storage.repositories.base import BaseRepository
from backend.storage.tables import ProductionReferenceEntity, ProductionEntity


class ReferenceProductionHandler:
    async def get(self) -> Production:
        """
        Находит производственную запись, на которую ссылается
        первая запись справочного списка
        """
        references = await BaseRepository(ProductionReferenceEntity).get_entities()
        reference_entity: ProductionReferenceEntity = references[0]

        production_entity = reference_entity.production
        mapper = BaseMapper(Production, ProductionEntity)

        production = mapper.entity_to_model(production_entity)
        return production

    async def update(self, new: Production):
        references = await BaseRepository(ProductionReferenceEntity).get_entities()
        reference_entity: ProductionReferenceEntity = references[0]

        production_entity = reference_entity.production
        mapper = BaseMapper(Production, ProductionEntity)

        new_entity: ProductionEntity = mapper.model_to_entity(new)
        new_entity.id = production_entity.id

        await BaseRepository(ProductionEntity).update([new_entity])

        return mapper.entity_to_model(new_entity)
