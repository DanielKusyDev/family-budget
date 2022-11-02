from abc import ABC, abstractmethod

from app import Map
from app.domain.models import Model
from app.domain.models.output_models import User


class DetailsView(ABC):
    @abstractmethod
    async def get_one(self) -> Model | None:
        raise NotImplementedError


class ListView(ABC):
    @abstractmethod
    async def get_many(self) -> list[Model]:
        raise NotImplementedError


class AuthenticationView(ABC):
    @abstractmethod
    async def authenticate(self) -> User | None:
        raise NotImplementedError


class InsertCommand(ABC):
    @abstractmethod
    async def create(self, data: Map) -> None:
        raise NotImplementedError


class SignInCommand(ABC):
    @abstractmethod
    async def sign_in(self, password: str) -> str | None:
        raise NotImplementedError
