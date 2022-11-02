from app import Map
from app.domain.ports.api_ports import InsertCommand
from app.domain.ports.spi_ports import InsertRepo


class TransactionInsertCommand(InsertCommand):
    def __init__(self, transaction_repo: InsertRepo) -> None:
        self._transaction_repo = transaction_repo

    async def create(self, data: Map) -> None:
        await self._transaction_repo.insert(data)


class CategoryInsertCommand(InsertCommand):
    def __init__(self, category_repo: InsertRepo) -> None:
        self._category_repo = category_repo

    async def create(self, data: Map) -> None:
        await self._category_repo.insert(data)
