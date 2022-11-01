from typing import cast

from icontract import ensure, require

from app import Map
from app.domain.models import Model
from app.domain.models.output_models import Transaction, Budget, BudgetListElement, User
from app.domain.ports.api_ports import InsertCommand
from app.domain.ports.api_ports import ListView, DetailsView
from app.domain.ports.spi_ports import InsertRepo, DetailsRepo
from app.domain.ports.spi_ports import ListRepo
from app.utils import repo_result_contain_keys


class BudgetDetailsView(DetailsView):
    def __init__(self, budget_repo: ListRepo) -> None:
        self._budget_repo = budget_repo

    @staticmethod
    @ensure(lambda result: all(r.amount > 0 for r in result), description="First list must include incomes only.")
    @ensure(lambda result: all(r.amount < 0 for r in result), description="First list must include expenses only.")
    def _split_transactions(transactions: list[Transaction]) -> tuple[list[Transaction], list[Transaction]]:
        incomes = []
        expenses = []
        for transaction in transactions:
            if transaction.amount > 0:
                incomes.append(transaction)
            else:
                expenses.append(transaction)
        return incomes, expenses

    @ensure(
        lambda result: repo_result_contain_keys(
            dicts=result,
            always_required_keys=["budget_id", "budget_name", "budget_created_at"],
            optional_keys={
                "transaction_id": [
                    "transaction_id",
                    "transaction_created_at",
                    "transaction_amount",
                    "transaction_description",
                ],
                "category_id": ["category_id", "category_created_at", "category_name", "category_description"],
            },
        ),
        description="Budget data is not fetched correctly from the repo. Some values are missing.",
    )
    async def _fetch_data(self) -> list[Map]:
        return await self._budget_repo.fetch()

    async def get_one(self) -> Model | None:
        raw_data = await self._fetch_data()
        if not raw_data:
            return None

        transactions = [
            Transaction(
                **{
                    "id": item["id"],
                    "amount": item["amount"],
                    "description": item["description"],
                    "created_at": item["created_at"],
                    "category": {
                        "id": item["category_id"],
                        "name": item["category_name"],
                        "description": item["category_description"],
                        "created_at": item["category_created_at"],
                    }
                    if item.get("category_id")
                    else None,
                }
            )
            for item in raw_data
            if "transaction_data"
        ]

        incomes, expenses = self._split_transactions(transactions)
        return Budget(
            id=raw_data[0]["budget_id"],
            created_at=raw_data[0]["budget_created_at"],
            name=raw_data[0]["budget_name"],
            incomes=incomes,
            expenses=expenses,
            balance=None,  # todo
        )


class BudgetListView(ListView):
    def __init__(self, budget_repo: ListRepo) -> None:
        self._budget_repo = budget_repo
        self._total: int | None = None

    @property
    @require(
        lambda self: self._total is not None,
        description="List wasn't fetched yet! Fetch the data before accessing the count number.",
    )
    def total_count(self) -> int:
        return cast(int, self._total)

    @ensure(
        lambda result: repo_result_contain_keys(result, ["id", "name", "created_at"]),
        description="Budget data is not fetched correctly from the repo. Some values are missing.",
    )
    async def _get_budgets(self) -> list[Map]:
        return await self._budget_repo.fetch()

    async def get_many(self) -> list[Model]:
        budgets = await self._get_budgets()
        self._total = budgets[0]["total_count"] if budgets else 0
        return [BudgetListElement(id=b["id"], name=b["name"], created_at=b["created_at"]) for b in budgets]


class BudgetInsertCommand(InsertCommand):
    def __init__(
        self,
        user: User,
        budget_insert_repo: InsertRepo,
        budget_details_repo: DetailsRepo,
        budget_to_user_insert_repo: InsertRepo,
    ) -> None:
        self._user = user
        self._budget_insert_repo = budget_insert_repo
        self._budget_details_repo = budget_details_repo
        self._budget_to_user_insert_repo = budget_to_user_insert_repo

    async def create(self, data: Map) -> None:
        await self._budget_insert_repo.insert(data)
        budget = await self._budget_details_repo.fetch_one()
        await self._budget_to_user_insert_repo.insert({"budget_id": budget["id"], "user_id": self._user.id})
