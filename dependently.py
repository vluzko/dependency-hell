import copy
from copy import deepcopy
import re
from typing import Tuple, List, Mapping, Callable


def dependently(style="google"):
    def dependent(f):
        """

        Args:
            f: Function to wrap. Should have at least one of "Requires:" or "Ensures:" in its docstring.

        Returns:

        """
        style_reader = style_mapping[style]
        arg_names = f.__code__.co_varnames
        requires, ensures = style_reader(f.__doc__)

        def wrapped(*args, **kwargs):
            for i, arg_name in enumerate(arg_names):
                loc = locals()
                glob = globals()
                if arg_name in loc or arg_name in glob:
                    raise OverwrittenVariableError("""The argument {} to the function {} is in the local or global environment of dependently.
                    Currently this causes unknown behavior, so it's disallowed. Please rename the argument or remove the dependently call.
                    """)

                exec('{} = deepcopy(args[{}])'.format(arg_name, i))

            for requirement in requires:
                assert eval(requirement), "Requirement failed: {}. Arguments: {}".format(requirement, args)
            ret = f(*args, **kwargs)

            for guarantee in ensures:
                assert eval(guarantee)

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
