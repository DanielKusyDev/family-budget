from typing import cast

from sqlalchemy import and_, desc
from strawberry.types import Info

from app.domain.models.output_models import BudgetListElement, User, Budget
from app.domain.services.budget_services import BudgetListView, BudgetInsertCommand, BudgetDetailsView
from app.domain.services.transaction_services import TransactionInsertCommand, CategoryInsertCommand
from app.domain.services.user_services import SignUpCommand, SignInDbCommand, UserAuthenticationView
from app.drivers.graphql.schemas import (
    BudgetListElementSchema,
    Page,
    FilterSchema,
    SignInForm,
    UserToken,
    BudgetDetailsSchema,
    TransactionInputSchema,
    CategoryInputSchema,
)
from app.infra.database.repos import SqlAlchemyListRepo, MssqlQuery, SqlAlchemyInsertRepo, SqlAlchemyDetailsRepo
from app.infra.database.tables import budget, user, user_to_budget, transaction, category


async def _get_user(access_token: str) -> User:
    user_view = UserAuthenticationView(access_token)
    if not user_view:
        raise PermissionError("Forbidden.")
    return cast(User, await user_view.authenticate())


async def get_budget_details(info: Info, budget_id: int, access_token: str) -> BudgetDetailsSchema:
    user_data = await _get_user(access_token)
    query = (
        MssqlQuery(budget)
        .get_by_id(budget_id)
        .join(user_to_budget, and_(user_to_budget.c.budget_id == budget.c.id, user_to_budget.c.user_id == user_data.id))
        .join(transaction, transaction.c.budget_id == budget.c.id, outer=True)
        .join(category, category.c.id == transaction.c.category_id, outer=True)
        .override_select(
            budget.c.id.label("budget_id"),
            budget.c.name.label("budget_name"),
            budget.c.created_at.label("budget_created_at"),
            transaction.c.id.label("transaction_id"),
            transaction.c.created_at.label("transaction_created_at"),
            transaction.c.amount.label("transaction_amount"),
            transaction.c.description.label("transaction_description"),
            category.c.id.label("category_id"),
            category.c.created_at.label("category_created_at"),
            category.c.name.label("category_name"),
            category.c.description.label("category_description"),
        )
    )
    repo = SqlAlchemyListRepo(connection=info.context["connection"], query=query)
    view = BudgetDetailsView(repo)
    budget_data = cast(Budget, await view.get_one())
    return BudgetDetailsSchema(
        id=budget_data.id,
        created_at=budget_data.created_at,
        name=budget_data.name,
        incomes=budget_data.incomes,
        expenses=budget_data.expenses,
        balance=budget_data.balance,
    )


async def get_budgets_list(
    info: Info, page: int, access_token: str, filters: list[FilterSchema] | None = None
) -> Page[list[BudgetListElementSchema]]:
    user_data = await _get_user(access_token)
    query = (
        MssqlQuery(budget)
        .paginate(page)
        .join(
            user_to_budget,
            and_(user_to_budget.c.budget_id == budget.c.id, user_to_budget.c.user_id == user_data.id),
        )
    )
    if filters:
        query.add_filters({f.key: f.value for f in filters})
    repo = SqlAlchemyListRepo(connection=info.context["connection"], query=query)
    view = BudgetListView(repo)
    items = cast(list[BudgetListElement], await view.get_many())
    budgets = [BudgetListElementSchema(id=item.id, name=item.name) for item in items]
    return Page(items=budgets, page=page, total=view.total_count, size=len(budgets))


async def sign_in(info: Info, user_data: SignInForm) -> UserToken:
    query = MssqlQuery(user).get(user.c.email, user_data.email)
    sign_in_command = SignInDbCommand(SqlAlchemyDetailsRepo(connection=info.context["connection"], query=query))
    token = await sign_in_command.sign_in(user_data.password)
    return UserToken(access_token=token)


async def sign_up(info: Info, user_data: SignInForm) -> UserToken:
    connection = info.context["connection"]
    with connection.begin():
        sign_up_command = SignUpCommand(SqlAlchemyInsertRepo(connection=connection, table=user))
        await sign_up_command.create(user_data.__dict__)
    return await sign_in(info, user_data)


async def create_budget(info: Info, budget_name: str, access_token: str) -> int:
    connection = info.context["connection"]
    user_data = await _get_user(access_token)
    budget_query = MssqlQuery(budget).get(budget.c.name, budget_name)
    with connection.begin():
        budget_command = BudgetInsertCommand(
            user=user_data,
            budget_insert_repo=SqlAlchemyInsertRepo(connection, budget),
            budget_details_repo=SqlAlchemyDetailsRepo(connection, budget_query),
            budget_to_user_insert_repo=SqlAlchemyInsertRepo(connection, user_to_budget),
        )
        await budget_command.create({"name": budget_name})
    return cast(int, budget_command.pk)


async def add_transaction(info: Info, input_data: TransactionInputSchema, access_token: str) -> int:
    connection = info.context["connection"]
    with connection.begin():
        command = TransactionInsertCommand(
            insert_repo=SqlAlchemyInsertRepo(connection=connection, table=transaction),
            details_repo=SqlAlchemyDetailsRepo(
                connection=connection,
                query=MssqlQuery(transaction).paginate(page=1, size=1).order_by(desc(transaction.c.id)),
            ),
        )
        await command.create(input_data.__dict__)
    return cast(int, command.pk)


async def add_category(info: Info, input_data: CategoryInputSchema, access_token: str) -> None:
    connection = info.context["connection"]
    with connection.begin():
        command = CategoryInsertCommand(
            insert_repo=SqlAlchemyInsertRepo(connection=connection, table=category),
            details_repo=SqlAlchemyDetailsRepo(
                connection=connection,
                query=MssqlQuery(category).paginate(page=1, size=1).order_by(desc(category.c.id)),
            ),
        )
        await command.create(input_data.__dict__)
    return command.pk
