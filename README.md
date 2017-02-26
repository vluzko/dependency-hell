# Depydent

"Dependent types" in Python.

More accurately: dependently is a (simple) library for creating "contracts" for your functions. You write requirements and guarantees in the docstring of a function, wrap the function in the @dependently wrapper, and it will ensure those requirements and guarantees are met.

## Usage
In the docstring of a function, insert a "Requires:" section or a "Ensures:" section.
Then wrap the function in the dependently.dependently decorator.

The section title must be followed by a newline.

Within each section, write any number of indented lines, where each line is a python expression.
It is encouraged but not mandatory that each line be a *boolean* expression, but this isn't
enforced.

Every time your function runs, the dependently decorator will assert each expression
in the "Requires" section before the function is called, and each expression in the
"Ensures" section after it returns.

The arguments to the function will be available to expressions in "Requires", by name.

The return value of the function will be available to expressions in "Ensures", under the name "ret"

## Example
````
@depydent.depydent()
def simple_sum(a: int, b: float, c: int):
    """

        Args:
            a:
            b:
            c:

        Returns:
            The sum of a, b, and c

        Requires:
            a in range(0, 1)
            b in range(6, 7)
            0 < c < 10

        Ensures:
            ret in range(6, 18)
            ret > a
            ret >= b
            ret > c
    """
    return a + b + c
````


## Caveats
*Be careful*. There's a fair amount of magic going on here, debugging it won't be fun.
* DO NOT write unpure conditions. The arguments are not copied, if your condition mutates one of them it will remain mutated.
* Don't wrap performance critical functions.
* Don't do anything tricky. If you're messing with python internals or doing anything hacky, don't use this library.
