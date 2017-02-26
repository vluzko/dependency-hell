import typing
import depydent
import pytest
import ipdb
import inspect


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


def test_in_check():
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


def test_create_locals():

    # Only positional arguments
    def just_args(a, b):
        return a + b

    # All provided.
    context = depydent.create_locals(inspect.getfullargspec(just_args), (1, 2), {})
    assert context == {'a': 1, 'b': 2}

    # Only keyword arguments
    def just_kwargs(a=1, b=1):
        return a + b

    # Just defaults.
    context = depydent.create_locals(inspect.getfullargspec(just_kwargs), (), {})
    assert context == {'a': 1, 'b': 1}

    # Partially supplied.
    context = depydent.create_locals(inspect.getfullargspec(just_kwargs), (), {'a': 2})
    assert context == {'a': 2, 'b': 1}

    def args_and_kwargs(a, b, c=1, d=2):
        return a + b + c + d

    # With default kwargs
    context = depydent.create_locals(inspect.getfullargspec(args_and_kwargs), (1, 2), {})
    assert context == {'a': 1, 'b': 2, 'c': 1, 'd': 2}

    # With normal kwargs
    context = depydent.create_locals(inspect.getfullargspec(args_and_kwargs), (1, 2), {'c': 3})
    assert context == {'a': 1, 'b': 2, 'c': 3, 'd': 2}

    # With positional kwargs
    context = depydent.create_locals(inspect.getfullargspec(args_and_kwargs), (1, 2, 3), {})
    assert context == {'a': 1, 'b': 2, 'c': 3, 'd': 2}

    def with_var_kwargs(a, b, c=1, **kwargs):
        return a + b + c

    context = depydent.create_locals(inspect.getfullargspec(with_var_kwargs), (1, 2), {'d': 2})
    assert context == {'a': 1, 'b': 2, 'c': 1, 'kwargs': {'d': 2}}

    def with_all(a, b, *args, c=1, d=2, **kwargs):
        return a + b + sum(args) + c + d + sum(kwargs.values())

    context = depydent.create_locals(inspect.getfullargspec(with_all), (1, 2, 3, 4, 5), {'e': 5, 'f': 6})
    assert context == {'a': 1, 'b': 2, 'args': (3, 4, 5), 'c': 1, 'd': 2, 'kwargs': {'e': 5, 'f': 6}}

