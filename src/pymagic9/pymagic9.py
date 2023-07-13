"""
PyMagic9 - a library that uses frames to analyze a call stack
"""
import dis
import sys

from opcode import haslocal, hasconst, hasname, hasjrel, hascompare, hasfree, cmp_op, opmap
from types import CodeType, FunctionType

# noinspection SpellCheckingInspection
__all__ = ["getframe", "isfunctionincallchain", "nameof"]


# noinspection SpellCheckingInspection
def _getframe(__depth=0):
    """Polyfill for built-in sys._getframe.

    :param __depth: deep of stack
    :return: Frame or None when __depth's frame in the top of stack.
    """

    if not isinstance(__depth, int):
        raise TypeError('an integer is required (got type %s)' % type(__depth))

    try:
        raise TypeError
    except TypeError:
        tb = sys.exc_info()[2]

    frame = tb.tb_frame.f_back
    del tb

    if __depth < 0:
        return frame

    try:
        while __depth:  # while i and frame: to disable the exception
            frame = frame.f_back
            __depth -= 1
    except AttributeError:
        raise ValueError('call stack is not deep enough')

    return frame


# noinspection PyUnresolvedReferences,SpellCheckingInspection,PyProtectedMember
getframe = sys._getframe if hasattr(sys, '_getframe') else _getframe


# noinspection SpellCheckingInspection
def isfunctionincallchain(o, __depth=-1):
    """A function that determines whether the given function object
    or code object is in the call chain.

    :param o: code object of function object
    :param __depth: search of deep
    :return: True or False
    """
    if not isinstance(o, (CodeType, FunctionType)):
        raise TypeError('\'obj\' must be code or function')

    code = o if not hasattr(o, "__code__") else o.__code__
    frame = getframe(1)
    while frame and __depth:
        if frame.f_code is code:
            return True

        __depth -= 1
        frame = frame.f_back

    return False


# noinspection SpellCheckingInspection,PyUnusedLocal
def nameof(obj):
    """A function that correctly determines the name of an object,
    without being tied to the object itself, for example:

    >>> var1 = [1,2]
    >>> var2 = var1
    >>> print(nameof(var1))
        var1
    >>> print(nameof(var2))
        var2
    :param obj: any object
    :return: name of object
    """
    frame = getframe(1)
    f_code, f_lineno = frame.f_code, frame.f_lineno

    for line in dis.findlinestarts(f_code):
        if f_lineno == line[1]:
            return _get_last_name(f_code.co_code[line[0]:frame.f_lasti], f_code)


# noinspection SpellCheckingInspection
def _get_argval(offset, op, arg, varnames=None, names=None, constants=None, cells=None):
    """Based on dis._get_instructions_bytes function.

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
        elif op in hasjrel:
            argval = offset + 2 + arg
        elif op in hascompare:
            argval = cmp_op[arg]
        elif op in hasfree:
            argval = cells[arg]
        elif op == opmap['FORMAT_VALUE']:
            argval = ((None, str, repr, ascii)[arg & 0x3], bool(arg & 0x4))

    return argval


def _get_last_name(code, f_code):
    arg, offset, op = None, None, None
    # noinspection PyProtectedMember
    for offset, op, arg in dis._unpack_opargs(code):
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
