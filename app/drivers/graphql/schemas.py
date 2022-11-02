from datetime import datetime
from typing import TypeVar, Generic

import strawberry

GenericType = TypeVar("GenericType")


@strawberry.type
class Page(Generic[GenericType]):
    items: GenericType
    page: int
    total: int
    size: int


@strawberry.type
class BudgetListElementSchema:
    id: int
    name: str


@strawberry.type
class Category:
    id: int
    name: str
    description: str | None


@strawberry.input
class CategoryInputSchema:
    name: str
    description: str | None


@strawberry.type
class Transaction:
    amount: float
    description: str | None = None
    category: Category | None = None


@strawberry.input
class TransactionInputSchema:
    amount: float
    budget_id: int
    description: str | None = None
    category_id: int | None = None


@strawberry.type
class BudgetDetailsSchema:
    id: int
    created_at: datetime
    name: str
    incomes: list[Transaction]
    expenses: list[Transaction]
    balance: float | None = None


@strawberry.type
class UserToken:
    access_token: str


@strawberry.input
class FilterSchema:
    key: str
    value: str


@strawberry.input
class SignInForm:
    email: str
    password: str
