import builtins
import re
from typing import Any

import fastapi
import icontract
import strawberry
from graphql import GraphQLError
from graphql.error.graphql_error import GraphQLFormattedError
from sqlalchemy.future import Connection
from starlette.requests import Request
from strawberry import BasePermission
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult, Info

from app import Map
from app.domain.services.user_services import UserAuthenticationView
from app.drivers.graphql import resolvers
from app.drivers.graphql.schemas import Page, BudgetListElementSchema, UserToken, BudgetDetailsSchema
from app.infra.database import get_connection


class MyGraphQLRouter(GraphQLRouter):
    @staticmethod
    def _process_error(error: GraphQLError) -> GraphQLFormattedError:
        match type(error.original_error):
            case icontract.ViolationError:
                pattern = r"(File .* line \d* in \w*:)(\s*.*)(: )"
                match = re.match(pattern, error.message)
                message = match.groups()[1].strip("\n").strip()
                error.message = f"Contract violation: {message}"
            case fastapi.HTTPException:
                error.message = error.original_error.detail
                error.locations = None
                error.path = None
            case builtins.PermissionError:
                error.message = "Forbidden."
                error.locations = None
                error.path = None
        return error.formatted

    async def process_result(self, request: Request, result: ExecutionResult) -> GraphQLHTTPResponse:
        data: GraphQLHTTPResponse = {"data": result.data}

        if result.errors:
            data["errors"] = [self._process_error(err) for err in result.errors]
        if result.extensions:
            data["extensions"] = result.extensions
        return data


async def get_context(connection: Connection = fastapi.Depends(get_connection)) -> Map:
    return {"connection": connection}


class IsAuthenticated(BasePermission):
    message = "Forbidden."

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        if not (token := kwargs.get("accessToken")):
            return False
        view = UserAuthenticationView(token)
        user = await view.authenticate()
        return user is not None


@strawberry.type
class Query:
    budgets: Page[list[BudgetListElementSchema]] = strawberry.field(
        resolver=resolvers.get_budgets_list,
        permission_classes=[IsAuthenticated]
    )
    budget: BudgetDetailsSchema = strawberry.field(
        resolver=resolvers.get_budget_details,
        permission_classes=[IsAuthenticated]
    )


@strawberry.type
class Mutation:
    sign_up: UserToken = strawberry.mutation(resolver=resolvers.sign_up)
    sign_in: UserToken = strawberry.mutation(resolver=resolvers.sign_in)
    create_budget: int = strawberry.mutation(resolver=resolvers.create_budget)
    add_transaction: int = strawberry.mutation(resolver=resolvers.add_transaction)
    add_category: int = strawberry.mutation(resolver=resolvers.add_category)
    import_budget: int = strawberry.mutation(resolver=resolvers.import_budget)


app = fastapi.FastAPI()
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = MyGraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")
