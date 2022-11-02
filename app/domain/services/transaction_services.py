from typing import cast

from app import Map
from app.domain.ports.api_ports import InsertCommand
from app.domain.ports.spi_ports import InsertRepo, DetailsRepo


class TransactionInsertCommand(InsertCommand):
    def __init__(self, insert_repo: InsertRepo, details_repo: DetailsRepo) -> None:
        self._insert_repo = insert_repo
        self._details_repo = details_repo
        self.pk = None

    async def create(self, data: Map) -> None:
        await self._insert_repo.insert(data)
        transaction = cast(Map, await self._details_repo.fetch_one())
        self.pk = transaction["id"]


class CategoryInsertCommand(InsertCommand):
    def __init__(self, insert_repo: InsertRepo, details_repo: DetailsRepo) -> None:
        self._insert_repo = insert_repo
        self._details_repo = details_repo
        self.pk = None

    async def create(self, data: Map) -> None:
        await self._insert_repo.insert(data)
        category = cast(Map, await self._details_repo.fetch_one())
        self.pk = category["id"]
