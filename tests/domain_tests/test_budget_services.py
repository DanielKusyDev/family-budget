from datetime import datetime

import pytest
from pytest_mock import MockFixture

from app.domain.adapters import InMemoryRepoFactory
from app.domain.models.output_models import Budget, Transaction, Category, BudgetListElement, User
from app.domain.ports.spi_ports import ListRepo, DetailsRepo
from app.domain.services.budget_services import BudgetDetailsView, BudgetListView, BudgetInsertCommand

_DTTM = datetime(year=2022, month=11, day=1, hour=11, minute=4, second=44)
_BUDGETS = [
    {"id": 1, "name": "My budget", "created_at": _DTTM, "total_count": 3},
    {"id": 2, "name": "foo", "created_at": _DTTM, "total_count": 3},
    {"id": 3, "name": "bar", "created_at": _DTTM, "total_count": 3},
]


@pytest.fixture(scope="module")
def simple_budgets_repo() -> ListRepo:
    return InMemoryRepoFactory({"budget": _BUDGETS}).create_list_repo("budget")


@pytest.fixture(scope="module")
def detailed_budget_repo() -> ListRepo:
    return InMemoryRepoFactory(
        {
            "budget": [
                {
                    "budget_id": 1,
                    "budget_name": "My budget",
                    "budget_created_at": _DTTM,
                    "transaction_id": 1,
                    "transaction_created_at": _DTTM,
                    "transaction_amount": 101,
                    "transaction_description": "First income",
                    "category_id": 1,
                    "category_created_at": _DTTM,
                    "category_name": "CAT",
                    "category_description": "CATEGORY",
                },
                {
                    "budget_id": 1,
                    "budget_name": "My budget",
                    "budget_created_at": _DTTM,
                    "transaction_id": 1,
                    "transaction_created_at": _DTTM,
                    "transaction_amount": 77.6,
                    "transaction_description": "Second income",
                    "category_id": 1,
                    "category_created_at": _DTTM,
                    "category_name": "CAT",
                    "category_description": "CATEGORY",
                },
                {
                    "budget_id": 1,
                    "budget_name": "My budget",
                    "budget_created_at": _DTTM,
                    "transaction_id": 1,
                    "transaction_created_at": _DTTM,
                    "transaction_amount": -99,
                    "transaction_description": "Expense",
                    "category_id": 2,
                    "category_created_at": _DTTM,
                    "category_name": "CAT",
                    "category_description": "CATEGORY",
                },
            ]
        }
    ).create_list_repo("budget")

@pytest.fixture(scope="module")
def budget_insert_details_repo() -> DetailsRepo:
    return InMemoryRepoFactory({"budget": _BUDGETS}).create_details_repo("budget", key=_BUDGETS[0]["id"])


async def test_budget_details_repo(detailed_budget_repo: ListRepo) -> None:
    view = BudgetDetailsView(detailed_budget_repo)
    item = await view.get_one()
    assert item == Budget(
        id=1,
        created_at=_DTTM,
        name="My budget",
        incomes=[
            Transaction(
                id=1,
                created_at=_DTTM,
                amount=101.0,
                description="First income",
                category=Category(id=1, created_at=_DTTM, name="CAT", description="CATEGORY"),
            ),
            Transaction(
                id=1,
                created_at=_DTTM,
                amount=77.6,
                description="Second income",
                category=Category(id=1, created_at=_DTTM, name="CAT", description="CATEGORY"),
            ),
        ],
        expenses=[
            Transaction(
                id=1,
                created_at=_DTTM,
                amount=-99.0,
                description="Expense",
                category=Category(id=2, created_at=_DTTM, name="CAT", description="CATEGORY"),
            )
        ],
        balance=None,
    )


async def test_budget_list_repo(simple_budgets_repo: ListRepo) -> None:
    view = BudgetListView(simple_budgets_repo)
    assert await view.get_many() == [
        BudgetListElement(id=1, created_at=_DTTM, name="My budget"),
        BudgetListElement(id=2, created_at=_DTTM, name="foo"),
        BudgetListElement(id=3, created_at=_DTTM, name="bar"),
    ]
    assert view.total_count == 3


async def test_budget_insert_command(budget_insert_details_repo: DetailsRepo, mocker: MockFixture) -> None:
    user = User(id=1, created_at=_DTTM, email="Daniel.Kusy@liamg.moc")
    budget_insert_repo = mocker.AsyncMock()
    budget_to_user_insert_repo = mocker.AsyncMock()
    command = BudgetInsertCommand(
        user=user,
        budget_insert_repo=budget_insert_repo,
        budget_details_repo=budget_insert_details_repo,
        budget_to_user_insert_repo=budget_to_user_insert_repo,
    )
    await command.create(_BUDGETS[0])
    assert command.pk == _BUDGETS[0]["id"]
    budget_insert_repo.insert.assert_called_once_with(_BUDGETS[0])
    budget_to_user_insert_repo.insert.assert_called_once_with({"budget_id": _BUDGETS[0]["id"], "user_id": user.id})
