"""
This module provides functions for analyzing call stacks such as `nameof`, `isfunctionincallchain`, etc.
"""
import dis
import sys

if sys.version_info < (3,):  # pragma: no cover
    # noinspection PyUnresolvedReferences
    from future_builtins import ascii
from opcode import haslocal, hasconst, hasname, hasjrel, hasjabs, hascompare, hasfree, cmp_op, opmap, EXTENDED_ARG, \
    HAVE_ARGUMENT, opname
from types import CodeType, FunctionType

# noinspection SpellCheckingInspection
__all__ = ["getframe", "isemptyfunction", "isfunctionincallchain", "nameof"]


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
        elif sys.version_info < (3, ):  # pragma: no cover
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
            return _get_last_name(f_code.co_code[line[0]:frame.f_lasti], f_code)


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
def _unpack_opargs_py2(code):  # pragma: no cover
    """
    _unpack_opargs function for python2

    """
    extended_arg, i = 0, 0
    while i < len(code):
        op = ord(code[i])
        i += 1
        if op >= HAVE_ARGUMENT:
            arg = ord(code[i]) | ord(code[i + 1]) * 256 | extended_arg  # type: int | None
            extended_arg, i = 0, i + 2
            if op == EXTENDED_ARG:
                exec("extended_arg = arg * 65536L")  # py3 support
        else:
            arg = None

        yield i, op, arg


# noinspection SpellCheckingInspection
def _unpack_opargs_py3(code):
    """
    _unpack_opargs function for python3

    This function is a clone of the `dis._unpack_opargs` function from the Python 3.9.6 standard library's `dis`
    module.
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


# noinspection SpellCheckingInspection
_unpack_opargs = _unpack_opargs_py2 if sys.version_info < (3,) else _unpack_opargs_py3
_unpack_opargs.__doc__ = """
Unpacks the opcodes and their arguments from the given bytecode. Works in Python 2.7 and Python 3.

Args:
    code (bytes or bytearray): The bytecode to unpack.

Yields:
    tuple: A tuple containing the offset, opcode, and argument of each opcode.

It takes a bytecode object as input and yields a sequence of tuples containing the offset, opcode, and argument of each
opcode in the bytecode.
"""
del _unpack_opargs_py2, _unpack_opargs_py3


# noinspection SpellCheckingInspection
def isemptyfunction(func):
    """
    Checks if a function is empty or not.

    Args:
        func (function): The function to check.

    Returns:
        bool: True if the function is empty, False otherwise.

    Raises:
        TypeError: If the input object is not a function.

    This function determines whether the given function is empty or not. An empty function is defined here as a
    function that:
    - may contain operators pass, return;
    - may only return None;
    - may contain a documentation string (classic documentation string in triple quotes, in double/single quotes as
    `str` type, and also in `bytes` type) and comments;
    - may contain any unreachable code (see `odd_function` in Examples);
    - may contain statements (of immutable types) to have no effect (see `odd_function` in Examples).
    If something else is present in the function, then it is considered not empty. It can be useful in scenarios where
    you need to check if a function has any implementation or if it is just a placeholder.

    The definition above may seem strange, but an empty function is defined this way for the sake of compatibility with
    the versions of Python supported by this project (since the interpreter behaves differently on different versions
    of Python, a simpler implementation of this function would return different values).

    Examples:
        >>> def empty_function():
        ...     pass
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     return
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     return None
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():  # doctest:+SKIP
        ...     # only in Python3
        ...     ...
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     \""" docstring \"""
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     "doc"
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     b'Hello World!'
        ...     return
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     # comments
        ...     return
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> def empty_function():
        ...     \""" docstring \"""
        ...     return
        ...
        >>> print(isemptyfunction(empty_function))
        True
        >>> empty_lambda = lambda x: None
        >>> print(isemptyfunction(empty_lambda))
        True
        >>> def non_empty_function():
        ...     print("Hello, world!")
        ...
        >>> print(isemptyfunction(non_empty_function))
        False
        >>> def non_empty_function():
        ...     return 0
        ...
        >>> print(isemptyfunction(non_empty_function))
        False
        >>> def non_empty_function():  # statement (mutable) to have no effect
        ...     []
        ...     return
        ...
        >>> print(isemptyfunction(non_empty_function))
        False
        >>> not_empty_lambda = lambda: 0
        >>> print(isemptyfunction(not_empty_lambda))
        False

        All odd_functions is empty!
        >>> def odd_function():  # statement (immutable) to have no effect
        ...     None
        ...     100
        ...     True
        ...     ()
        ...     "string"
        ...     b'd\x01'
        ...     return
        ...
        >>> print(isemptyfunction(odd_function))
        True
        >>> def odd_function(): \""" docstring \"""; return; None;  # oneline function and unreachable code
        >>> print(isemptyfunction(odd_function))
        True
        >>> def odd_function():  # unreachable code
        ...     return
        ...     a = 2
        >>> print(isemptyfunction(odd_function))
        True
    """
    if not isinstance(func, FunctionType):
        raise TypeError("'func' argument must be a function")

    code = func.__code__
    gen_opargs = _unpack_opargs(code.co_code)
    op, loadop, loadarg = 0, 0, 0
    for _, op, arg in gen_opargs:
        if op == 9:  # skip if NOP; py310+
            continue

        if op == 1 and loadop:  # skip when POP_TOP next for LOAD_*  # pragma: no cover
            loadop = 0
            continue

        # TODO: isemptyfunction: explicitly specify opcodes
        if opname[op].startswith("LOAD"):
            if not loadop:  # skip when first LOAD_* opcode
                loadop, loadarg = op, arg
                continue

            return False  # two LOAD_* opcodes in a row

        break

    if loadop != 100:  # first opcode must be LOAD_CONST
        return False

    if code.co_consts[loadarg] is not None:  # check for docstring
        return False

    return op == 83  # second opcode must be RETURN_VALUE
