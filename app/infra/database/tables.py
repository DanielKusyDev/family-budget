from typing import Any

from sqlalchemy import Table, Column, MetaData, Integer, DateTime, func, Float, String, ForeignKey

METADATA = MetaData()


def get_common_fields() -> list[Column]:
    """Get a common set of meta columns present in all the tables."""
    return [
        Column("id", Integer, primary_key=True),
        Column("created_at", DateTime, nullable=False, default=func.current_timestamp()),
    ]


class SqlTable(Table):
    def __new__(cls, table_name: str, *args: Any, **kw: Any) -> Table:
        meta_fields = get_common_fields()
        table = super().__new__(cls, table_name, METADATA, *meta_fields, *args, **kw)
        return table


user = SqlTable(
    "user",
    Column("email", String(255), unique=True, nullable=False),
    Column("password", String(100), nullable=False),
)

budget = SqlTable(
    "budget",
    Column("name", String(255), unique=True, nullable=False),
)

category = SqlTable(
    "category",
    Column("name", String(255), unique=True, nullable=False),
    Column("description", String(1023)),
)

transaction = SqlTable(
    "transaction",
    Column("amount", Float(), nullable=False),
    Column("description", String(1023)),
    Column("category_id", Integer, ForeignKey("category.id", name="transaction_category_fk")),
    Column("budget_id", Integer, ForeignKey("budget.id", name="transaction_budget_fk")),
)


user_to_budget = SqlTable(
    "user_to_budget",
    Column("budget_id", Integer, ForeignKey("budget.id", name="user_to_budget_budget_fk")),
    Column("user_id", Integer, ForeignKey("user.id", name="user_to_budget_user_fk")),
)
