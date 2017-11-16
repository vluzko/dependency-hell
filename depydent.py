import re
from typing import Tuple, List, Mapping, Callable, Dict
import inspect

RETURN_PATTERN = re.compile(r'$return as (\w+)$')


def depydent(style="google", type_checks=False):
    """

    Args:
        style: The documentation style.
        type_checks: Whether or not to also run type checks (using the function's annotations).
            Defaults to False, because it's assumed that mypy is in use.

    Returns:

    """
    def dependent(f):
        """

        Args:
            f: Function to wrap. Should have at least one of "Requires:" or "Ensures:" in its docstring.

        Returns:

        """
        annotation_requirements = extract_annotations(f.__annotations__)
        compiled_annotations = {k: [compile(x, '<string>', 'eval') for x in v] for k, v in annotation_requirements.items()}

        if f.__doc__:
            style_reader = style_mapping[style]

            require_strings, ensure_strings = style_reader(f.__doc__)
            match = re.match(RETURN_PATTERN, ensure_strings[0] if len(ensure_strings) > 0 else "")
            if match:
                return_string = match.groups()[0]
            else:
                return_string = "ret"
            requires = [compile(x, '<string>', 'eval') for x in require_strings]
            ensures = [compile(x, '<string>', 'eval') for x in ensure_strings]
        else:
            requires = []
            ensures = []
            require_strings = []
            ensure_strings = []
            return_string = "ret"

        def wrapped(*args, **kwargs):
            closure = inspect.getclosurevars(f)

            # Create locals
            local_context = inspect.getcallargs(f, *args, **kwargs)

            # Create globals
            global_context = closure.globals
            global_context.update(closure.builtins)
            global_context.update(closure.nonlocals)

            # Run function Requires
            for requirement, string in zip(requires, require_strings):
                assert eval(requirement, global_context, local_context), "Requirement failed: {}. Arguments: {}".format(string, args)

            # Run argument Requires
            for argument in local_context:
                # Optional, in case you want to use mypy.
                if type_checks:
                    expected_type = f.__annotations__.get(argument)
                    if expected_type:
                        try:
                            error_message = "{arg} ({val}) is not an instance of {typ} and it should be.".format(arg=argument, val=local_context[argument], typ=expected_type)
                            assert isinstance(local_context[argument], expected_type), error_message
                        except TypeError:
                            # Because of the way the `typing` library works, it's not really feasible to check that the argument has the correct *type*.
                            # isinstance(val, Type) (where Type is defined by the `typing` library) will generate a TypeError.
                            # This is deeply unfortunate but unavoidable.
                            pass

                requirements = annotation_requirements.get(argument, ())
                compiled = compiled_annotations.get(argument, ())
                for requirement, string in zip(compiled, requirements):
                    assert eval(requirement, global_context, local_context), "Annotation requirement failed: {}. Arguments: {}".format(string, args)

            # Run Ensures
            return_value = f(*args, **kwargs)
            local_context[return_string] = return_value
            for guarantee, string in zip(ensures, ensure_strings):
                assert eval(guarantee, global_context, local_context), "Guarantee failed: {}. Return value: {}".format(string, return_value)

            return return_value
        return wrapped
    return dependent


def extract_annotations(annotations: Dict[str, type]) -> Dict[str, Tuple[str]]:
    """Pulls requirements out of type annotations.
    Takes the annotations from an inspect.FullArgSpec object.
    Checks each annotation for docstrings, then checks each docstring for requirements.

    Args:
        annotations: A dictionary mapping argument names to their annotated types.

    Returns:
        A dictionary mapping arguments to their requirements.
    """
    requirements = {}

    for argument, expected_type in annotations.items():
        requires = ()
        if expected_type.__doc__:
            requires = tuple(string.replace('self', argument) for string in read_google_style(expected_type.__doc__)[0])

        # Check if any superclasses have requirements.
        for superclass in expected_type.__bases__:
            additional_requirements = extract_annotations({argument: superclass})
            if additional_requirements:
                requires = requires + additional_requirements.get(argument, ())
        if requires:
            requirements[argument] = requires
    return requirements


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
        title_pattern = re.compile('^([ \t]*)' + section_title + ':[ \t]*\n', re.MULTILINE)
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
