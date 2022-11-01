from typing import cast

from sqlalchemy import and_
from strawberry.types import Info

from app.domain.models.output_models import BudgetListElement, User
from app.domain.services.budget_services import BudgetListView, BudgetInsertCommand
from app.domain.services.user_services import SignUpCommand, SignInDbCommand, UserAuthenticationView
from app.drivers.graphql.schemas import BudgetListElementSchema, Page, FilterSchema, SignInForm, UserToken
from app.infra.database.repos import SqlAlchemyListRepo, MssqlQuery, SqlAlchemyInsertRepo, SqlAlchemyDetailsRepo
from app.infra.database.tables import budget, user, user_to_budget


async def _get_user(access_token: str) -> User:
    user_view = UserAuthenticationView(access_token)
    return await user_view.authenticate()


async def budgets_list(
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


async def create_budget(info: Info, budget_name: str, access_token: str) -> None:
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
