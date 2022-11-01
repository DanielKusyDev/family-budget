from typing import Sequence

from app import Map


def repo_result_contain_keys(
    dicts: Sequence[Map], always_required_keys: Sequence[str], optional_keys: dict[str, Sequence[str]] | None = None
) -> bool:
    """
    Check if all items in the list include given keys.

    There are two types of keys: always required and optional. The list is always checked for the presence of the first
    set of keys. The second is a dictionary `key:list<values>` where the 'key' is a field that must be present in a
    checked dictionary to start validating assigned to that key list.
    """
    if not all([set(always_required_keys).issubset(set(data_keys)) for data_keys in dicts]):
        return False
    if not optional_keys:
        return True
    for base_key, keys in optional_keys.items():
        for item in dicts:
            if base_key in item and not set(keys).issubset(set(item)):
                return False
    return True
