from sqlalchemy.future import create_engine

from app.config import settings

engine = create_engine(settings.DB_CONNECTION_STRING, echo=settings.DEBUG)


def get_connection():
    with engine.connect() as conn:
        yield conn
