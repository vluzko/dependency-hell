from depydent import depydent
import pytest


def test_in_check():

    @depydent.depydent()
    def in_range_check(a: int, b: float, c: float):
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

        Ensures:
            ret in range(6, 8)
            ret > a
            ret >= b
        """
        return a + b + c

    assert in_range_check(0, 6, 0) == 6

    with pytest.raises(AssertionError):
        in_range_check(-1, 6, 0)


def test_closures():
    asdf = 7

    @depydent.depydent()
    def enclosed(a: int, b: float, c: float):
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
            asdf in range(7, 8)

        Ensures:
            ret in range(13, 16)
            ret > a
            ret >= b
        """
        return a + b + c + asdf
    assert enclosed(0, 6, 0) == 13


def test_basic_type_checking():

    @depydent.depydent(type_checks=True)
    def to_fail(a: int):
        return a

    with pytest.raises(AssertionError):
        to_fail(5.0)


def test_sub_types():
    class Base:
        """Base class.

        Requires:
            self.a > 1
        """

        def __init__(self, a):
            self.a = a

    class Derived(Base):
        pass

    x = Derived(5)

    y = Derived(-1)

    @depydent.depydent()
    def take_derived(der: Derived):
        return der

    take_derived(x)

    with pytest.raises(AssertionError):
        take_derived(y)
