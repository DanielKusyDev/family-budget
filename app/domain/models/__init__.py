from abc import ABC
from datetime import datetime, date
from typing import Any

from pydantic.main import BaseModel


class AbstractModel(BaseModel, ABC):
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
        json_decoders = {datetime: lambda v: datetime.fromisoformat(v)}

    def dict(self, *args: Any, **kwargs: Any) -> Any:
        data = super().dict(*args, **kwargs)
        for k, v in data.items():
            if isinstance(v, date):
                data[k] = v.isoformat()
        return data


class Model(AbstractModel):
    id: int
    created_at: datetime
