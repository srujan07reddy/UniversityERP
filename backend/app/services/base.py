from typing import Any, Dict, Generic, List, Optional, Sequence, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.schemas.response import PaginationMetadata

ModelType = TypeVar("ModelType")
RepoType = TypeVar("RepoType", bound=BaseRepository)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, RepoType]):
    """
    Generic Business Service Layer.
    Enforces that business operations, validation rules, and domain events
    live in the service layer, keeping API route handlers concise and decoupled.
    """

    def __init__(self, repository: RepoType, session: AsyncSession):
        self.repository = repository
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        """Retrieve single resource by primary key."""
        return await self.repository.get_by_id(id)

    async def list_paginated(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[Sequence[ModelType], PaginationMetadata]:
        """
        Fetch paginated records along with calculated pagination metadata.
        """
        offset = (page - 1) * page_size
        items = await self.repository.get_multi(offset=offset, limit=page_size)
        total_items = await self.repository.count()
        metadata = PaginationMetadata.create(page=page, page_size=page_size, total_items=total_items)
        return items, metadata

    async def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Create resource with business rule enforcement and commit."""
        instance = await self.repository.create(obj_in)
        await self.session.commit()
        return instance

    async def update(
        self,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update resource with business rule enforcement and commit."""
        updated = await self.repository.update(db_obj=db_obj, obj_in=obj_in)
        await self.session.commit()
        return updated

    async def delete(self, id: Any) -> Optional[ModelType]:
        """Delete resource by primary key and commit."""
        deleted = await self.repository.delete_by_id(id)
        if deleted:
            await self.session.commit()
        return deleted

