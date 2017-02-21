import dependently
import pytest
import ipdb
import inspect


@dependently.dependently()
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


@dependently.dependently()
def with_keywords(a: int, b: int=0, c=1):
    """
    Requires:
        a >= 0
        b >= 0

    Ensures:
        ret >= a
        ret >= b

    """
    ipdb.set_trace()
    return a + b


@dependently.dependently()
def with_all(a, b, *args, c=0, d=1, **kwargs):
    """

    Args:
        a:
        b:
        *args:
        c:
        d:
        **kwargs:

    Returns:

    Requires:

    Ensures:

    """
    return a + b


def test_in_check():
    assert in_range_check(0, 6, 0) == 6

    with pytest.raises(AssertionError):
        in_range_check(-1, 6, 0)


def test_keyword_args():
    with_keywords(1, c=2)


def test_with_all():
    with_all(1, 2, 3, 4, c=1, e=5)


def test_closures():
    asdf = 7

    @dependently.dependently()
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


def test_create_locals():

    def just_args(a, b):
        return a + b

    context = dependently.create_locals(inspect.getfullargspec(just_args), (1, 2), {})
    assert context == {'a': 1, 'b': 2}

    def just_kwargs(a=1, b=1):
        return a + b

    context = dependently.create_locals(inspect.getfullargspec(just_kwargs), (), {})
    assert context == {'a': 1, 'b': 1}

    context = dependently.create_locals(inspect.getfullargspec(just_kwargs), (), {'a': 2})
    assert context == {'a': 2, 'b': 1}

    def args_and_kwargs(a, b, c=1):
        return a + b + c

    def with_var_kwargs(a, b, c=1, **kwargs):
        return a + b + c
    context = dependently.create_locals(inspect.getfullargspec(with_var_kwargs), (1, 2), {'d': 2})
    assert context == {'a': 1, 'b': 2, 'c': 1, 'kwargs': {'d': 2}}

# test_keyword_args()
# test_with_all()
test_create_locals()
# with_var_kwargs(1, 2, d=3)