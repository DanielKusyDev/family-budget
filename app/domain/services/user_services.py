from datetime import datetime

import bcrypt
import jwt
import pytz
from icontract import require

from app import Map
from app.config import settings
from app.domain.models.output_models import User
from app.domain.ports.api_ports import InsertCommand, SignInCommand, AuthenticationView
from app.domain.ports.spi_ports import InsertRepo, DetailsRepo


class SignInDbCommand(SignInCommand):
    def __init__(self, user_repo: DetailsRepo) -> None:
        self._user_repo = user_repo

    async def _get_user(self) -> Map | None:
        return await self._user_repo.fetch_one()

    @staticmethod
    async def _generate_token(user_data: Map) -> str:
        user_data["created_at"] = user_data["created_at"].isoformat()
        payload = {"sub": user_data, "exp": datetime.now(tz=pytz.utc) + settings.JWT_EXP}
        encoded_jwt = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALG)
        return encoded_jwt

    async def sign_in(self, password: str) -> str | None:
        user_data = await self._user_repo.fetch_one()
        if user_data:
            passwords_match = bcrypt.checkpw(password.encode("utf-8"), user_data["password"].encode("utf-8"))
            if passwords_match:
                return await self._generate_token(user_data)
        raise PermissionError


class SignUpCommand(InsertCommand):
    def __init__(self, repo: InsertRepo) -> None:
        self._repo = repo

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @require(lambda data: "email" in data, description="Username is required.")
    @require(lambda data: "password" in data, description="Password is required.")
    async def create(self, data: Map) -> None:
        password = self._hash_password(data["password"])
        await self._repo.insert({"email": data["email"], "password": password})


class UserAuthenticationView(AuthenticationView):
    def __init__(self, token: str) -> None:
        self._token = token

    async def authenticate(self) -> User | None:
        try:
            payload = jwt.decode(self._token, settings.SECRET_KEY, algorithms=[settings.JWT_ALG])
        except jwt.DecodeError:
            return None
        if datetime.fromtimestamp(payload["exp"], tz=pytz.utc) > datetime.now(tz=pytz.utc):
            return User(**payload["sub"])
        return None
