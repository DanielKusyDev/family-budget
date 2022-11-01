from abc import ABC, abstractmethod
from typing import Any

from app import Map


class StorageQuery(ABC):
    @property
    @abstractmethod
    def query(self) -> Any:
        """
        Return a query object to use to read from storage. Might be any kind of object, depends on the storage itself.
        For instance if the SQL Database is used, the query would be a SQL query string.
        """
        raise NotImplementedError


class ListRepo(ABC):
    @abstractmethod
    async def fetch(self) -> list[Map]:
        """Fetch a list of entities from the storage."""
        raise NotImplementedError


class DetailsRepo(ABC):
    @abstractmethod
    async def fetch_one(self) -> Map | None:
        """Fetch single item from the storage."""
        raise NotImplementedError


class InsertRepo(ABC):
    @abstractmethod
    async def insert(self, data: Map) -> None:
        """Fetch a list of entities from the storage."""
        raise NotImplementedError
