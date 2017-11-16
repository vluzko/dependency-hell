import typing
import depydent
import pytest


PositiveInteger = typing.NewType("PositiveInteger", int)
PositiveInteger.__doc__ = """
Requires:
    self > 0
"""


@depydent.depydent()
def check_positive(a: PositiveInteger):
    return a


def test_check_positive():
    assert check_positive(PositiveInteger(5))

    with pytest.raises(AssertionError):
        assert check_positive(PositiveInteger(-1))
