from collections import defaultdict

from app import Map
from app.domain.ports.spi_ports import DetailsRepo, ListRepo

IMDB = dict[str, list[Map]]
default_db: IMDB = defaultdict(list)


class InMemoryDetailsRepo(DetailsRepo):

    _db: IMDB

    def __init__(self, entity: str, key: int) -> None:
        self._entity = entity
        self._key = key

    async def fetch_one(self) -> Map | None:
        for item in self._db[self._entity]:
            if item["id"] == self._key:
                return item
        return None


class InMemoryListRepo(ListRepo):

    _db: IMDB

    def __init__(self, entity: str, filters: Map | None = None) -> None:
        self._entity = entity
        self._filters = filters

    async def fetch(self) -> list[Map]:
        data = self._db[self._entity]
        if self._filters:
            return [item for item in data if any([getattr(item, k) == v for k, v in self._filters.items()])]
        return data


class InMemoryRepoFactory:
    def __init__(self, database: IMDB) -> None:
        self._database = database

    def create_details_repo(self, entity: str, key: int) -> InMemoryDetailsRepo:
        repo = InMemoryDetailsRepo(entity, key)
        repo._db = self._database
        return repo

    def create_list_repo(self, entity: str, filters: Map | None = None) -> InMemoryListRepo:
        repo = InMemoryListRepo(entity, filters)
        repo._db = self._database
        return repo
