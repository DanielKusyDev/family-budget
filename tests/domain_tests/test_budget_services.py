from datetime import datetime

from app import Map
from app.domain.models.output_models import Budget, Transaction, Category, BudgetListElement
from app.domain.ports.spi_ports import ListRepo
from app.domain.services.budget_services import BudgetDetailsView, BudgetListView

_DTTM = datetime(year=2022, month=11, day=1, hour=11, minute=4, second=44)
_BUDGETS = [
    {"id": 1, "name": "My budget", "created_at": _DTTM, "total_count": 3},
    {"id": 2, "name": "foo", "created_at": _DTTM, "total_count": 3},
    {"id": 3, "name": "bar", "created_at": _DTTM, "total_count": 3},
]


class FakeBudgetRepoForDetailsView(ListRepo):
    async def fetch(self) -> list[Map]:
        return [
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


class FakeBudgetRepoForListView(ListRepo):
    async def fetch(self) -> list[Map]:
        return _BUDGETS


async def test_budget_details_repo() -> None:
    view = BudgetDetailsView(FakeBudgetRepoForDetailsView())
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


async def test_budget_list_repo() -> None:
    view = BudgetListView(FakeBudgetRepoForListView())
    assert await view.get_many() == [
        BudgetListElement(id=1, created_at=_DTTM, name="My budget"),
        BudgetListElement(id=2, created_at=_DTTM, name="foo"),
        BudgetListElement(id=3, created_at=_DTTM, name="bar"),
    ]
    assert view.total_count == 3
