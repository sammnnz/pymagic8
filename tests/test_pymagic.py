# noinspection SpellCheckingInspection
"""
Tests for pymagic9.py module
"""
import dis
import pymagic9.pymagic9 as pm
import pytest
import sys

from six import add_metaclass


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


# noinspection SpellCheckingInspection,PyUnresolvedReferences
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
            pm._getframe(__depth)
    else:
        match = ""

        if sys.version_info >= (3, 5):
            match = r"(an integer is required \(got type (.*))"
        elif sys.version_info < (3, ):
            match = "an integer is required"

        with pytest.raises(TypeError, match=match):
            # noinspection PyTypeChecker
            pm._getframe(__depth)


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
    exec("result = pm_.nameof(%s) if hasattr(pm_, 'nameof') else None" % name, locals())
    del pm_

    assert locals()['result'] == name


# noinspection SpellCheckingInspection,PyUnresolvedReferences
def test__get_argval():
    max_count = 8
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
                for offset, op, arg in pm._unpack_opargs(code):
                    pm._get_argval(offset, op, arg,
                                   varnames, names, constants, cells)
                    assert True


# noinspection PyUnresolvedReferences
def test__get_last_name():
    frame = pm.getframe(0)
    f_code = frame.f_code
    result = pm._get_last_name(f_code.co_code[:frame.f_lasti], f_code)
    del f_code, frame

    assert result == 'frame'


def empty_function_1():
    pass


def empty_function_2():
    return


def empty_function_3():
    return None

empty_function_4 = """
def empty_function_4():
    ...
"""  # noqa 305
if sys.version_info < (3,):
    empty_function_4 = """
def empty_function_4():
    return
"""

exec(empty_function_4, globals())


def empty_function_5():  # noqa 302
    """ docstring """


def empty_function_6():
    "doc"


def empty_function_7():
    b'Hello World!'
    return


def empty_function_8():
    # comment
    return


def empty_function_9():
    """ docstring """
    return


empty_lambda_1 = lambda x: None  # noqa 731


def not_empty_function_1():
    print("Hello, world!")


def not_empty_function_2():
    return 0


not_empty_lambda_1 = lambda: 0  # noqa 731


def odd_function_1(): """docstring"""; return; None;  # noqa 702


def odd_function_2(a, c):
    return
    a = 2
    b = a * 3  # noqa 841


def odd_function_3():
    return
    100


def odd_function_4(a, *args):
    None
    True
    ()
    return


def odd_function_5():
    []
    return


def odd_function_6():
    100
    return


@pytest.mark.parametrize(("func", "name"), [
    (empty_function_1, None),
    (empty_function_2, None),
    (empty_function_3, None),
    (empty_function_4, None),
    (empty_function_5, None),
    (empty_function_6, None),
    (empty_function_7, None),
    (empty_function_8, None),
    (empty_function_9, None),
    (empty_lambda_1, pm.nameof(empty_lambda_1)),
    (not_empty_function_1, None),
    (not_empty_function_2, None),
    (not_empty_lambda_1, pm.nameof(not_empty_lambda_1)),
    (odd_function_1, None),
    (odd_function_2, None),
    (odd_function_3, None),
    (odd_function_4, None),
    (odd_function_5, None),
    (odd_function_6, None),
])
def test_isemptyfunction(func, name):
    if name is None:
        name = func.__name__

    expected = None
    if name.startswith("not_empty"):
        expected = False
    elif name.startswith(("empty", "odd")):
        expected = True

    result = pm.isemptyfunction(func)
    assert result is expected


def test_isemptyfunction_invalid_input():
    with pytest.raises(TypeError, match=r"\'func\' argument must be a function"):
        pm.isemptyfunction(None)


# noinspection PyMissingOrEmptyDocstring
@pytest.fixture(scope="class")
def create_PropertyMeta():

    @add_metaclass(pm.PropertyMeta)
    # noinspection PyMissingOrEmptyDocstring,PyCompatibility
    class _(object):
        # noinspection PyPropertyAccess
        def __init__(self):
            self.__field = 1
            self.property1 = "property1"
            self.property2 = "property2"
            self.property3 = "property3"
            self.property4 = "property4"
            self.property5 = "property5"

        # noinspection PyTypeChecker,PyPropertyDefinition
        property1 = property(Ellipsis, Ellipsis)

        # noinspection PyTypeChecker,PyPropertyDefinition
        property2 = property(
            fget=Ellipsis,
            fdel=Ellipsis
        )

        # empty accessor
        # noinspection PyPropertyDefinition, PyStatementEffect
        @property
        def property3(self):
            Ellipsis

        @property3.setter
        def property3(self, value):
            print(value)

        # empty accessor
        # noinspection PyPropertyDefinition
        @property
        def property4(self):
            pass

        @property4.deleter
        def property4(self):
            print('delete')

        # empty accessor
        @property4.setter
        def property4(self, value):
            return

        # empty accessor
        @property
        def property5(self):
            return None

    return _


# noinspection PyMissingOrEmptyDocstring
class TestPropertyMeta:
    @staticmethod
    def test___init__():
        Meta = pm.PropertyMeta("Meta", (), {"i": 1})
        assert isinstance(Meta, pm.PropertyMeta)

    @staticmethod
    def test_property1_get(create_PropertyMeta):
        TestClass = create_PropertyMeta()
        assert TestClass.property1 == "property1"

    @staticmethod
    def test_property1_del(create_PropertyMeta):
        TestClass = create_PropertyMeta()
        del TestClass.property1
        for attr, _ in TestClass.__dict__.items():
            if attr.startswith("__") and attr.endswith("property1"):
                assert TestClass.property1 is None

    @staticmethod
    def test_property2_set(create_PropertyMeta):
        TestClass = create_PropertyMeta()
        with pytest.raises(AttributeError, match=r"'property' object has private setter"):
            TestClass.property2 = None

    @staticmethod
    def test_property3_set(create_PropertyMeta):
        TestClass = create_PropertyMeta()
        TestClass.property3 = None
        assert TestClass.property3 is None

    @staticmethod
    def test_property4_del(create_PropertyMeta):
        TestClass = create_PropertyMeta()
        del TestClass.property4
        for attr, _ in TestClass.__dict__.items():
            if attr.startswith("__") and attr.endswith("property4"):
                assert TestClass.property4 is None


@pytest.mark.parametrize("func", [
    empty_function_1,
    not_empty_function_1,
    None,
    Ellipsis
])
def test__is_auto_implemented_accessor(func):
    expected = None
    if func is None:
        expected = False
    elif func is Ellipsis:
        expected = True
    elif func.__name__.startswith("empty"):
        expected = True
    elif func.__name__.startswith("not"):
        expected = False

    # noinspection PyUnresolvedReferences
    assert expected is pm._is_autoimplemented_accessor(func)
