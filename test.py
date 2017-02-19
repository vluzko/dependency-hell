import dependently
import pytest


@dependently.dependently()
def in_check(a: int, b: float, c: str):
    """

    Args:
        a:
        b:
        c:

    Returns:
        y: The sum of the inputs

    Requires:
        a in range(0, 1)
        b in range(6, 7)
        len(c) < 10

    Ensures:
        ret in range(6, 8)
        ret > a
        ret >= b
    """
    return a + b


def test_in_check():
    assert in_check(0, 6, "as") == 6

    with pytest.raises(AssertionError):
        in_check(-1, 6, "as")
