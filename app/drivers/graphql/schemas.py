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
