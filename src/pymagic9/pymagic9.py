"""
Pymagic9 - a library that uses frames to analyze a call stack
"""
import sys

# noinspection SpellCheckingInspection
__all__ = ["getframe", "nameof"]


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
def nameof(o):
    """

    :param o:
    """
    pass
