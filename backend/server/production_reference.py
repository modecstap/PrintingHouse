from fastapi import APIRouter, Depends

from backend.models import Production
from backend.server.dependencies import (
    get_current_user_with_full_permission,
    get_current_user_with_read_permission,
)
from backend.storage.mappers.base_mapper import BaseMapper
from backend.storage.repositories.base import BaseRepository
from backend.storage.tables import ProductionEntity, ProductionReferenceEntity


router = APIRouter(
    prefix="/api/reference/production",
    tags=["reference/production"],
)


@router.get(
    "/",
    dependencies=[Depends(get_current_user_with_read_permission)],
)
async def get_production_reference() -> Production:
    """Возвращает производство, на которое ссылается первая строка справочника.

    Ошибки: IndexError, если справочник пуст.
    """
    references = await BaseRepository(ProductionReferenceEntity).get_entities()
    reference_entity: ProductionReferenceEntity = references[0]
    production_entity = reference_entity.production
    mapper = BaseMapper(Production, ProductionEntity)
    return mapper.entity_to_model(production_entity)


@router.put(
    "/",
    dependencies=[Depends(get_current_user_with_full_permission)],
    response_model=None,
)
async def update_production_reference(new: Production) -> Production:
    """Обновляет производство первой строки справочника. Id строки сохраняется.

    Результат: обновлённая модель Production.
    Побочные эффекты: запись ProductionEntity.
    Ошибки: IndexError, если справочник пуст.
    """
    references = await BaseRepository(ProductionReferenceEntity).get_entities()
    reference_entity: ProductionReferenceEntity = references[0]
    production_entity = reference_entity.production
    mapper = BaseMapper(Production, ProductionEntity)
    new_entity: ProductionEntity = mapper.model_to_entity(new)
    new_entity.id = production_entity.id
    await BaseRepository(ProductionEntity).update([new_entity])
    return mapper.entity_to_model(new_entity)
