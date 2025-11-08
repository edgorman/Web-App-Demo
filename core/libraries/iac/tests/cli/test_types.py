import itertools
from collections.abc import Callable
from contextlib import nullcontext as no_exception
from typing import Optional

import pytest

from cli.__types import PositiveNumberParamType, SemanticVersionParamType, SHA1ParamType


@pytest.mark.parametrize(
    "value,expect_exception,expect_message",
    [
        ("1", no_exception(), None),
        ("blah", pytest.raises(Exception), "Must be a number, got 'blah'."),
        ("0", pytest.raises(Exception), "Must be a positive non-zero number, got 0."),
        ("-1", pytest.raises(Exception), "Must be a positive non-zero number, got -1."),
    ],
)
def test_PositiveNumberParamType_convert(value: str, expect_exception: Callable, expect_message: Optional[str]):
    _type = PositiveNumberParamType()

    with expect_exception as e:
        _type.convert(value, None, None)

    assert expect_message is None or expect_message in str(e)


@pytest.mark.parametrize(
    "value,expect_exception,expect_message",
    [
        ("0.1.0", no_exception(), None),
        ("blah", pytest.raises(Exception), "Must be a valid semantic version, got 'blah'."),
    ],
)
def test_SemanticVersionParamType_convert(value: str, expect_exception: Callable, expect_message: Optional[str]):
    _type = SemanticVersionParamType()

    with expect_exception as e:
        _type.convert(value, None, None)

    assert expect_message is None or expect_message in str(e)


def generate_sha1(n: int) -> str:
    return "".join(itertools.islice(itertools.cycle("0123456789abcdef"), n))


@pytest.mark.parametrize(
    "value,expect_exception,expect_message",
    [
        (generate_sha1(5), no_exception(), None),
        (generate_sha1(40), no_exception(), None),
        (generate_sha1(4), pytest.raises(Exception), f"Must be a valid SHA1, got {generate_sha1(4)!r}."),
        (generate_sha1(41), pytest.raises(Exception), f"Must be a valid SHA1, got {generate_sha1(41)!r}."),
    ],
)
def test_SHA1ParamType_convert(value: str, expect_exception: Callable, expect_message: Optional[str]):
    _type = SHA1ParamType()

    with expect_exception as e:
        _type.convert(value, None, None)

    assert expect_message is None or expect_message in str(e)
