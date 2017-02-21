import copy
from copy import deepcopy
import re
from typing import Tuple, List, Mapping, Callable
from inspect import getclosurevars, getfullargspec, FullArgSpec
import ipdb


def create_locals(spec: FullArgSpec, all_args: tuple, all_kwargs: dict) -> dict:
    """

    Args:
        spec:
        all_args:
        all_kwargs:

    Returns:

    """
    context = {arg_name: val for arg_name, val in zip(spec.args, all_args)}
    if spec.varargs:
        context.update({spec.varargs: all_args[len(context):]})
        context.update(spec.kwonlydefaults)
        # var_kwargs = {k: v for k, v in all_kwargs.items() if k not in spec.kwonlyargs}
        kwargs = {k: all_kwargs.get(k, spec.kwonlydefaults[k]) for k in spec.kwonlyargs}
        context.update(kwargs)
    elif spec.defaults:
        number_kws = len(spec.defaults)
        kwargs = {arg_name: all_kwargs.get(arg_name, val) for arg_name, val in zip(spec.args[-number_kws:], spec.defaults)}
        context.update(kwargs)
    else:
        kwargs = {}
    var_kwargs = {k: v for k, v in all_kwargs.items() if k not in kwargs}
    if var_kwargs:
        context[spec.varkw] = var_kwargs

    return context


def dependently(style="google"):
    """

    Args:
        style:

    Returns:

    """
    def dependent(f):
        """

        Args:
            f: Function to wrap. Should have at least one of "Requires:" or "Ensures:" in its docstring.

        Returns:

        """
        if not f.__doc__:
            return f

        style_reader = style_mapping[style]
        arg_names = f.__code__.co_varnames

        require_strings, ensure_strings = style_reader(f.__doc__)
        requires = [compile(x, '<string>', 'eval') for x in require_strings]
        ensures = [compile(x, '<string>', 'eval') for x in ensure_strings]

        def wrapped(*args, **kwargs):
            spec = getfullargspec(f)
            closure = getclosurevars(f)
            local_context = create_locals(spec, args, kwargs)

            global_context = closure.globals
            global_context.update(closure.builtins)
            global_context.update(closure.nonlocals)
            # local_context = {arg_name: deepcopy(arg) for arg_name, arg in zip(arg_names, args)}

            for requirement, string in zip(requires, require_strings):
                assert eval(requirement, global_context, local_context), "Requirement failed: {}. Arguments: {}".format(string, args)
            ret = f(*args, **kwargs)
            local_context['ret'] = ret
            for guarantee, string in zip(ensures, ensure_strings):
                assert eval(guarantee, global_context, local_context), "Guarantee failed: {}. Return value: {}".format(string, ret)

            return ret
        return wrapped
    return dependent


def read_google_style(docstring: str) -> Tuple[List[str], List[str]]:
    """Parses a Google style dependency docstring.

    Args:
        docstring: A docstring with Google style dependencies.

    Returns:
        requires, ensures. Both are lists of strings, where each string is a valid Python expression.
    """

    def _read_section(section_title: str) -> List[str]:
        """Reads a section. Used for requires and ensures"""
        lines = []  # type: List[str]
        title_pattern = re.compile('^([ \t]+)' + section_title + ':[ \t]*\n', re.MULTILINE)
        title_match = title_pattern.search(docstring)

        if title_match:
            prefix = r'^' + title_match.groups()[0]  # type: str
            end = title_match.end()
            try:
                first_line_pattern = prefix + r'([ \t]+)(.*)\n'
                first_line = re.compile(first_line_pattern, re.MULTILINE).search(docstring[end:])
                indent, statement = first_line.groups()
                lines.append(statement)

                full_indent = prefix + indent
                remaining = docstring[end + first_line.end():]
                other_lines_pattern = r'(' + full_indent + r'.*\n' + r')*'
                other_lines = re.compile(other_lines_pattern, re.MULTILINE).match(remaining).group()
                lines.extend([line.strip() for line in other_lines.splitlines()])
            except AttributeError:
                pass
        return lines

    requires = _read_section("Requires")
    ensures = _read_section("Ensures")
    return requires, ensures


class OverwrittenVariableError(Exception):
    pass


style_mapping = {
    "google": read_google_style
}  # type: Mapping[str, Callable[[str], Tuple[List[str], List[str]]]]
