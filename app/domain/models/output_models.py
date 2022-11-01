from app.domain.models import Model


class Category(Model):
    name: str
    description: str | None


class Transaction(Model):
    amount: float
    description: str | None = None
    category: Category | None = None


class Budget(Model):
    name: str
    incomes: list[Transaction]
    expenses: list[Transaction]
    balance: float | None = None


class BudgetListElement(Model):
    name: str
