# noinspection SpellCheckingInspection
"""
Tests for pymagic9.py module
"""
import dis
import pymagic9.pymagic9 as pm
# noinspection PyPackageRequirements
import pytest
import sys


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("__depth",
                         [
                             -1,
                             0,
                             1,
                         ]
                         )
def test__getframe_valid(__depth):
    """
    Correct cases of `_getframe`
    """
    try:
        raise TypeError
    except TypeError:
        expected = (sys.exc_info()[2]).tb_frame

    # noinspection PyUnresolvedReferences
    result = pm._getframe(__depth)

    while __depth > 0:
        __depth = __depth - 1
        expected = expected.f_back

    assert result is expected


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("__depth",
                         [
                             (),
                             1000000000,
                         ]
                         )
def test__getframe_invalid(__depth):
    # noinspection SpellCheckingInspection,SpellCheckingInspection
    """
    Incorrect cases of `_getframe`
    """
    if isinstance(__depth, int):
        with pytest.raises(ValueError, match=r"call stack is not deep enough"):
            pm.getframe(__depth)
    else:
        match = ""

        if sys.version_info >= (3, 5):
            match = r"(an integer is required \(got type (.*))"
        elif sys.version_info == (2, 7):
            match = "an integer is required"

        with pytest.raises(TypeError, match=match):
            # noinspection PyTypeChecker
            pm.getframe(__depth)


# noinspection SpellCheckingInspection
def test_isfunctionincallchain_valid():
    # noinspection PyMissingOrEmptyDocstring
    def f(o):
        return pm.isfunctionincallchain(o)

    # noinspection PyMissingOrEmptyDocstring
    def g(o):
        return f(o)

    assert g(g) and g(g.__code__) is True and f(g) is False


# noinspection SpellCheckingInspection,PyTypeChecker
def test_isfunctionincallchain_invalid():
    with pytest.raises(TypeError, match=r"\'o\' must be code or function"):
        pm.isfunctionincallchain(None)


# noinspection SpellCheckingInspection
@pytest.mark.parametrize("name",
                         [
                             "first_name",
                             "_SecondName",
                             "__name3",
                         ]
                         )
def test_nameof(name):
    locals().setdefault(name, None)
    pm_ = pm
    exec ("result = pm_.nameof(%s) if hasattr(pm_, 'nameof') else None" % name, locals())
    del pm_

    assert locals()['result'] == name


# noinspection SpellCheckingInspection,PyUnresolvedReferences
def test__get_argval():
    max_count = 3
    for _, o in globals().items():
        if not max_count:
            break

        if hasattr(o, "__code__"):
            max_count -= 1
            co = o.__code__
            code = co.co_code
            # noinspection SpellCheckingInspection
            varnames = co.co_varnames
            names = co.co_names
            constants = co.co_consts
            cells = co.co_cellvars + co.co_freevars

            if hasattr(dis, '_get_instructions_bytes'):
                for i in dis._get_instructions_bytes(code, varnames, names, constants, cells):
                    # noinspection PyUnresolvedReferences
                    result = pm._get_argval(i.offset, i.opcode, i.arg,
                                            varnames, names, constants, cells)
                    assert result == i.argval
            else:
                _ = bytearray(code)
                del _[::-3]
                for offset, op, arg in pm._unpack_opargs(_):
                    pm._get_argval(offset, op, arg,
                                   varnames, names, constants, cells)
                    assert True


# noinspection PyUnresolvedReferences
def test__get_last_name():
    frame = pm.getframe(0)
    f_code = frame.f_code

    if sys.version_info >= (3,):
        result = pm._get_last_name(f_code.co_code[:frame.f_lasti], f_code)
    else:
        _ = bytearray(f_code.co_code)[:frame.f_lasti]
        del _[::-3]
        result = pm._get_last_name(_, f_code)

    del f_code, frame

    assert result == 'frame'
