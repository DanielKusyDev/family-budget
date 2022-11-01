from typing import Any, cast

from icontract import require, invariant
from sqlalchemy import Column, func
from sqlalchemy.future import select, Connection
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import BinaryExpression

from app import Map
from app.config import settings
from app.domain.ports.spi_ports import DetailsRepo, StorageQuery, ListRepo, InsertRepo
from app.infra.database.tables import SqlTable


class MssqlQuery(StorageQuery):
    def __init__(self, table: SqlTable) -> None:
        self._table = table
        self._where: list[BinaryExpression] = []
        self._select_from = table
        self._select = [table]
        self._limit: int | None = None
        self._offset = 0
        self._order_by = {self._table.c.id}

    @property
    def query(self) -> Select:
        return (
            select(*self._select)
            .where(*self._where)
            .select_from(self._select_from)
            .limit(self._limit)
            .offset(self._offset)
            .order_by(*self._order_by)
        )

    def add_filters(self, filters: Map) -> "MssqlQuery":
        self._where += [self._table.c.get(field) == value for field, value in filters.items()]
        return self

    @require(lambda key: key > 0, description="Primary key must be positive.")
    def get_by_id(self, key: int) -> "MssqlQuery":
        self._where.append(self._table.c.id == key)
        return self

    @require(lambda self, column: column.name in self._table.columns)
    def get(self, column: Column, value: Any) -> "MssqlQuery":
        self._where.append(column == value)
        return self

    @require(lambda page: page > 0, description="Page must be greater than 0.")
    def paginate(self, page: int) -> "MssqlQuery":
        self._limit = settings.DEFAULT_PAGE_SIZE
        self._limit = cast(int, self._limit)
        self._offset = (page - 1) * self._limit
        self._select.append(func.count().over().label("total_count"))
        return self

    def join(self, table: SqlTable, on: BinaryExpression, outer: bool = False) -> "MssqlQuery":
        if outer:
            self._select_from = self._select_from.outerjoin(table, on)
        else:
            self._select_from = self._select_from.join(table, on)
        return self


@invariant(lambda self: not self._connection.closed, description="DB session is inactive!")
class SqlAlchemyDetailsRepo(DetailsRepo):
    def __init__(self, connection: Connection, query: StorageQuery) -> None:
        self._connection = connection
        self._query = query

    async def fetch_one(self) -> Map | None:
        item = self._connection.execute(self._query.query).unique().one_or_none()
        return dict(item) if item else None


@invariant(lambda self: not self._connection.closed, description="DB session is inactive!")
class SqlAlchemyListRepo(ListRepo):
    def __init__(self, connection: Connection, query: StorageQuery) -> None:
        self._connection = connection
        self._query = query

    async def fetch(self) -> list[Map]:
        return [dict(row) for row in self._connection.execute(self._query.query).all()]


class SqlAlchemyInsertRepo(InsertRepo):
    def __init__(self, connection: Connection, table: SqlTable) -> None:
        self._table = table
        self._connection = connection

    async def insert(self, data: Map) -> None:
        self._connection.execute(self._table.insert().values(**data))
