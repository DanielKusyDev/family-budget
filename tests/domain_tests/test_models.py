from datetime import datetime, date

from faker import Faker

from app.domain.models import AbstractModel


class TestEncoders(AbstractModel):
    dttm: datetime
    dt: date


def test_model_decoders(faker: Faker) -> None:
    report = TestEncoders(
        dttm=datetime(year=1999, month=12, day=10, hour=8, minute=12, second=1), dt=date(year=2002, month=1, day=1)
    )
    assert report.dict() == {"dttm": "1999-12-10T08:12:01", "dt": "2002-01-01"}


def test_model_encoders() -> None:
    report = TestEncoders(dttm="1999-12-10T08:12:01", dt="2002-01-01")
    assert report == TestEncoders(
        dttm=datetime(year=1999, month=12, day=10, hour=8, minute=12, second=1),
        dt=date(year=2002, month=1, day=1),
    )
