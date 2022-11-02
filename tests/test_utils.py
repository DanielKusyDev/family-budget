import pytest

from app import Map
from app.utils import repo_result_contain_keys


@pytest.mark.parametrize(
    "dicts, always_required_keys, optional_keys, expected_result",
    [
        pytest.param([{"a": 1}], ["b"], [], False, id="Always required keys missing."),
        pytest.param([{"a": 1}], ["a"], [], True, id="Always required keys present, no optional keys specified."),
        pytest.param(
            [{"a": 1}],
            ["a"],
            {"a": ["b"]},
            False,
            id="Always required keys present, optional keys guard present, no actual key in the dicts.",
        ),
        pytest.param(
            [{"a": 1, "b": 2}],
            ["a"],
            {"a": ["b", "c"]},
            False,
            id="Always required keys present, optional keys guard present, not all actual keys in the dicts.",
        ),
        pytest.param(
            [{"a": 1, "b": 2, "c": 3}],
            ["a"],
            {"a": ["b", "c"]},
            True,
            id="Always required keys present, optional keys guard present, all actual keys present.",
        ),
    ],
)
def test_repo_result_contain_keys_helper_method(
    dicts: list[Map],
    always_required_keys: list[str],
    optional_keys: dict[str, list[str]] | None,
    expected_result: bool,
) -> None:
    assert repo_result_contain_keys(dicts, always_required_keys, optional_keys) == expected_result
