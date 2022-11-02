import pytest

from app.domain.adapters import InMemoryRepoFactory, IMDB
from app.domain.ports.spi_ports import InsertRepo, DetailsRepo
from app.domain.services.transaction_services import TransactionInsertCommand, CategoryInsertCommand


@pytest.fixture
def transaction_insert_repo(in_memory_db: IMDB) -> InsertRepo:
    return InMemoryRepoFactory(in_memory_db).create_insert_repo("transaction")


@pytest.fixture
def transaction_details_repo(in_memory_db: IMDB) -> DetailsRepo:
    in_memory_db["transaction"].append({"id": 1})
    return InMemoryRepoFactory(in_memory_db).create_details_repo("transaction", 1)


@pytest.fixture
def category_insert_repo(in_memory_db: IMDB) -> InsertRepo:
    return InMemoryRepoFactory(in_memory_db).create_insert_repo("category")


@pytest.fixture
def category_details_repo(in_memory_db: IMDB) -> DetailsRepo:
    in_memory_db["category"].append({"id": 1})
    return InMemoryRepoFactory(in_memory_db).create_details_repo("category", 1)


async def test_transaction_insert_command(
    transaction_insert_repo: InsertRepo, transaction_details_repo: DetailsRepo, in_memory_db: IMDB
) -> None:
    command = TransactionInsertCommand(transaction_insert_repo, transaction_details_repo)
    transaction = {"amount": 124, "name": "TRANSACTION", "description": "DESC", "category_id": 1, "budget_id": 1}
    await command.create(transaction)
    assert command.pk == 1
    assert transaction in in_memory_db["transaction"]


async def test_category_insert_command(
    category_insert_repo: InsertRepo, category_details_repo: DetailsRepo, in_memory_db: IMDB
) -> None:
    command = CategoryInsertCommand(category_insert_repo, category_details_repo)
    category = {"name": "category", "description": "DESC"}
    await command.create(category)
    assert command.pk == 1
    assert category in in_memory_db["category"]
