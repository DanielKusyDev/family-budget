from collections import defaultdict

import pytest

from app.domain.adapters import IMDB


@pytest.fixture
def in_memory_db() -> IMDB:
    return defaultdict(list)
