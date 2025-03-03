import itertools
from collections.abc import Callable
from contextlib import nullcontext as no_exception
from typing import Optional

import pytest

from cli.__types import PositiveNumberParamType, SemanticVersionParamType, SHA1ParamType


@pytest.mark.parametrize(
    "value,expectException,expectMessage",
    [
        ("1", no_exception(), None),
        ("blah", pytest.raises(Exception), "Must be a number, got 'blah'."),
        ("0", pytest.raises(Exception), "Must be a positive non-zero number, got 0."),
        ("-1", pytest.raises(Exception), "Must be a positive non-zero number, got -1."),
    ],
)
def test_PositiveNumberParamType_convert(value: str, expectException: Callable, expectMessage: Optional[str]):
    _type = PositiveNumberParamType()

    with expectException as e:
        _type.convert(value, None, None)

    assert expectMessage is None or expectMessage in str(e)


@pytest.mark.parametrize(
    "value,expectException,expectMessage",
    [
        ("0.1.0", no_exception(), None),
        ("blah", pytest.raises(Exception), "Must be a valid semantic version, got 'blah'."),
    ],
)
def test_SemanticVersionParamType_convert(value: str, expectException: Callable, expectMessage: Optional[str]):
    _type = SemanticVersionParamType()

    with expectException as e:
        _type.convert(value, None, None)

    assert expectMessage is None or expectMessage in str(e)


def generate_sha1(n: int) -> str:
    return "".join(itertools.islice(itertools.cycle("0123456789abcdef"), n))


@pytest.mark.parametrize(
    "value,expectException,expectMessage",
    [
        (generate_sha1(5), no_exception(), None),
        (generate_sha1(40), no_exception(), None),
        (generate_sha1(4), pytest.raises(Exception), f"Must be a valid SHA1, got {generate_sha1(4)!r}."),
        (generate_sha1(41), pytest.raises(Exception), f"Must be a valid SHA1, got {generate_sha1(41)!r}."),
    ],
)
def test_SHA1ParamType_convert(value: str, expectException: Callable, expectMessage: Optional[str]):
    _type = SHA1ParamType()

    with expectException as e:
        _type.convert(value, None, None)

    assert expectMessage is None or expectMessage in str(e)
