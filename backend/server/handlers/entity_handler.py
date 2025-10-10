from typing import List

from fastapi import HTTPException, status
from pydantic import BaseModel

from backend.storage.access_services.crud_accessor import CRUDAccessor
from backend.storage.exceptions.not_found_exception import NotFoundException


class EntityHandler:
    MODEL = BaseModel
    INSERT_MODEL = BaseModel
    UPDATE_MODEL = BaseModel

    def __init__(self, service: CRUDAccessor):
        self._service = service

    async def get_all(self) -> List[MODEL]:
        try:
            return await self._service.get_models()
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def get(self, id: int) -> MODEL:
        try:
            return await self._service.get_model_by_id(id)
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=str(e))

    async def create(self, data: INSERT_MODEL) -> MODEL:
        created_models = await self._service.add_models([data])
        return created_models[0]

    async def create_bulk(self, data: List[INSERT_MODEL]) -> List[MODEL]:
        created_models = await self._service.add_models(data)
        return created_models

    async def update(self, id: int, data: UPDATE_MODEL) -> MODEL:
        data.id = id
        updated_models = await self._service.update_models([data])
        return updated_models[0]

    async def update_bulk(self, data: List[UPDATE_MODEL]) -> List[MODEL]:
        updated_models = await self._service.update_models(data)
        return updated_models

    async def delete(self, id: int) -> dict:
        await self._service.delete_models([id])
        return {"message": "Deleted successfully", "status_code": status.HTTP_200_OK}
