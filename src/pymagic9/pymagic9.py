"""
This module provides functions for analyzing call stacks such as `nameof`, `isfunctionincallchain`, etc.
"""
import dis
import sys

if sys.version_info < (3,):
    # noinspection PyUnresolvedReferences
    from future_builtins import ascii
from opcode import haslocal, hasconst, hasname, hasjrel, hasjabs, hascompare, hasfree, cmp_op, opmap, EXTENDED_ARG, \
    HAVE_ARGUMENT
from types import CodeType, FunctionType

# noinspection SpellCheckingInspection
__all__ = ["getframe", "isfunctionincallchain", "nameof"]


# noinspection SpellCheckingInspection
def _getframe(__depth=0):
    """
    Polyfill for the built-in sys._getframe function.

    Args:
        __depth (int, optional): The depth of the call stack to traverse. A value of 0 represents the current frame,
         1 represents the caller's frame, and so on.

    Returns:
        FrameType or None: The frame object at the specified depth in the call stack, or None if the depth is out of
        range.

    Raises:
        TypeError: If the depth argument is not an integer.
        ValueError: If call stack is not deep enough.

    This function provides a polyfill for the built-in `sys._getframe` function, which is used to access the call stack
    frames. It allows you to retrieve the frame object at a specific depth in the call stack.

    The depth argument specifies the number of frames to traverse. A value of 0 or less 0 represents the current frame,
    1 represents the caller's frame, and so on. If the depth is negative, it will traverse the frames in the opposite
    direction.

    If the specified depth is out of range (i.e., greater than the number of frames in the call stack), the function
    raises ValueEror.

    Examples:
        >>> def foo():
        ...     frame = _getframe(1)
        ...     print(frame.f_code.co_name)  # Output: bar
        >>> def bar():
        ...     foo()
        >>> bar()
        bar
    """

    if not isinstance(__depth, int):
        if sys.version_info >= (3, 5):
            raise TypeError('an integer is required (got type %s)' % type(__depth))
        elif sys.version_info < (3, ):
            raise TypeError('an integer is required')

    try:
        raise TypeError
    except TypeError:
        tb = sys.exc_info()[2]

    if tb is None: return None  # noqa E702

    frame = tb.tb_frame.f_back
    del tb

    if __depth < 0: return frame  # noqa E702

    try:
        while __depth:  # while i and frame: to disable the exception
            frame = frame.f_back  # type: ignore #noqa
            __depth -= 1
    except AttributeError:
        raise ValueError('call stack is not deep enough')

    return frame


# noinspection PyUnresolvedReferences,SpellCheckingInspection,PyProtectedMember
getframe = sys._getframe if hasattr(sys, '_getframe') else _getframe


# noinspection SpellCheckingInspection
def isfunctionincallchain(o, __depth=-1):
    """
    Determines whether the given function object or code object is present in the call chain.

    Args:
        o (FunctionType or CodeType): The function object or code object to check.
        __depth (int, optional): The depth of the call chain to search. Default is -1, which means search the entire
         call chain.

    Returns:
        bool: True if the function or code object is found in the call chain, False otherwise.

    Raises:
        TypeError: If the input object is not a function or code object.

    This function checks if the given function object or code object is present in the call chain of the current
    execution. The call chain is the sequence of function calls that led to the current point of execution.

    Warning:
         Be careful when debugging in PyCharm - there may be incorrect behavior when a function that is being debugged
         (a function that has breakpoints) is passed as an argument.

    Examples:
        >>> def foo():
        ...     return isfunctionincallchain(foo)
        ...
        >>> def bar():
        ...     return isfunctionincallchain(foo)
        ...
        >>> def baz():
        ...     return foo()
        ...
        >>> print(foo())
        True
        >>> print(bar())
        False
        >>> print(baz())
        True
    """
    if not isinstance(o, (CodeType, FunctionType)):
        raise TypeError('\'o\' must be code or function')

    code = o if not hasattr(o, "__code__") else o.__code__  # type: ignore
    frame = getframe(1)
    while frame and __depth:
        if frame.f_code is code:
            return True

        __depth -= 1
        frame = frame.f_back

    return False


# noinspection SpellCheckingInspection,PyUnusedLocal
def nameof(o):
    """
    Returns the name of an object.

    Args:
        o (object): The object for which to retrieve the name.

    Returns:
        str: The name of the object.

    This function correctly determines the 'name' of an object, without being tied to the object itself.
    It can be used to retrieve the name of variables, functions, classes, modules, and more.

    Examples:
        >>> var1 = [1, 2]
        >>> var2 = var1
        >>> print(nameof(var1))
        var1
        >>> print(nameof(var2))
        var2
    """
    frame = getframe(1)
    f_code, f_lineno = frame.f_code, frame.f_lineno

    for line in dis.findlinestarts(f_code):
        if f_lineno == line[1]:
            if sys.version_info >= (3,):
                return _get_last_name(f_code.co_code[line[0]:frame.f_lasti], f_code)

            bytea = bytearray(f_code.co_code)[line[0]:frame.f_lasti]; del bytea[::-3]  # type: ignore # noqa E702
            return _get_last_name(bytea, f_code)


# noinspection SpellCheckingInspection
# TODO: _get_argval: Write exact types of arguments and return values
def _get_argval(offset, op, arg, varnames=None, names=None, constants=None, cells=None):
    """
    Returns the argument value based on the opcode and argument. Based on *dis._get_instructions_bytes* function (see
    `dis.get_instructions <https://docs.python.org/3.9/library/dis.html#dis.get_instructions>`_).

    This function is used internally by the `pymagic9` module to retrieve the value of an argument based on the opcode
    and argument index. It takes the offset, opcode, and argument as input and returns the corresponding value.

    The `varnames`, `names`, `constants`, and `cells` arguments are optional and provide additional context for
    resolving the argument value.
    """
    # noinspection SpellCheckingInspection
    argval = None
    if arg is not None:
        argval = arg
        if op in haslocal:
            argval = varnames[arg]
        elif op in hasconst:
            argval = constants[arg]
        elif op in hasname:
            argval = names[arg]
        elif op in hasjabs:
            if sys.version_info >= (3, 10):
                argval = arg * 2
        elif op in hasjrel:
            argval = offset + 2 + arg if sys.version_info < (3, 10) else offset + 2 + arg*2
        elif op in hascompare:
            argval = cmp_op[arg]
        elif op in hasfree:
            argval = cells[arg]
        elif op == opmap.get('FORMAT_VALUE'):
            argval = ((None, str, repr, ascii)[arg & 0x3], bool(arg & 0x4))

    return argval


def _get_last_name(code, f_code):
    """
    Returns the name that matches the last argument in the given bytecode.

    Args:
        code (bytes): The bytecode of the code object.
        f_code (CodeType): The code object.

    Returns:
        str or None: The name that matches the last argument, or None if no match is found.

    This function is used internally by the `pymagic9` module to retrieve the name that corresponds to the last
    argument in a given code object. It takes the bytecode and the code object.
    """
    arg, offset, op = None, None, None
    # noinspection PyProtectedMember
    for offset, op, arg in _unpack_opargs(code):
        pass

    if arg is None:
        return

    if op not in hasname:
        return _get_argval(offset, op, arg,
                           f_code.co_varnames,
                           f_code.co_names,
                           f_code.co_consts,
                           f_code.co_cellvars + f_code.co_freevars)

    return f_code.co_names[arg]


# noinspection SpellCheckingInspection
def _unpack_opargs(code):
    """
    Unpacks the opcodes and their arguments from the given bytecode.

    Args:
        code (bytes or bytearray): The bytecode to unpack.

    Yields:
        tuple: A tuple containing the offset, opcode, and argument of each opcode.

    This function is a clone of the `dis._unpack_opargs` function from the Python 3.9.6 standard library's `dis`
    module. This is done to support early versions of python. It takes a bytecode object as input and yields a sequence
    of tuples containing the offset, opcode, and argument of each opcode in the bytecode.
    """
    extended_arg = 0
    for i in range(0, len(code), 2):
        op = code[i]
        if op >= HAVE_ARGUMENT:
            arg = code[i + 1] | extended_arg
            extended_arg = (arg << 8) if op == EXTENDED_ARG else 0
        else:
            arg = None
        yield i, op, arg
