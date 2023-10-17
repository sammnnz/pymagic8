# pymagic9

[![license](https://img.shields.io/badge/License-APACHE_2.0-yellow.svg)](http://www.apache.org/licenses/)
<a><img src="https://img.shields.io/badge/python-2.7 | 3.6 | 3.7 | 3.8 | 3.9 | 3.10 -blue.svg"></a>
![Tests](https://github.com/sammnnz/pymagic9/actions/workflows/tests.yml/badge.svg)
[![codecov](https://codecov.io/gh/sammnnz/pymagic9/branch/release-v0.9.0/graph/badge.svg?token=qQAiKKnctA)](https://codecov.io/gh/sammnnz/pymagic9)

This is a Python library based on calling the stack of frames at runtime and analyzing the code object of frames (bytecode and other attributes). Basically, it implements some C# features. For example, it contains the `nameof` function and `auto-implemented properties`. See the [documentation](https://sammnnz.github.io/pymagic9/) for more information.

## Installation

You can install `pymagic9` using pip:
~~~~shell
pip install pymagic9
~~~~

## Features

**[getframe](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.getframe)**: The [sys._getframe](https://docs.python.org/3/library/sys.html?highlight=_getframe#sys._getframe) function is used here if it exists in the version of python being used. Otherwise, the [_getframe](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9._getframe) polyfill is used.

**[isemptyfunction](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.isemptyfunction)**: Checks if a function is empty or not.

**[isfunctionincallchain](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.isfunctionincallchain)**: Determines whether the given function object or code object is present in the call chain.

**[nameof](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.nameof)**: This function allows you to retrieve the name of a variable, function, class, or module as a string. This can be useful in scenarios where you need to dynamically access or manipulate names in your code.

**[PropertyMeta](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.PropertyMeta)**: This metaclass allows you to create `auto-implemented properties` (like in C#, where you can declare properties without explicitly defining a getter and setter), for which you can use an ellipsis or empty functions to indicate that the Python itself would create the auto-implemented accessor.

## Usage of `auto-implemented properties`

1. Import the PropertyMeta metaclass and assign it as a metaclass for the desired class:
~~~~python
from pymagic9 import PropertyMeta


class Person(metaclass=PropertyMeta):
    pass
~~~~
2. Create properties in this class with empty accessors (using empty function or ellipsis) to indicate that this property will be auto-implemented:
~~~~python
from pymagic9 import PropertyMeta


class Person(metaclass=PropertyMeta):
    """class Person"""
    def __init__(self, name):
        self.name = name

    name = property(fget=...,)           # readonly property
    age = property(fget=..., fset=...,)  # ordinary property
~~~~
3. Now for an `ordinary` property we can get and put values into it at any time. But for a `readonly` property, you can put a value into it only once, at the time of creating an instance of the class:
~~~~python
from pymagic9 import PropertyMeta


class Person(metaclass=PropertyMeta):
    """class Person"""
    def __init__(self, name):
        self.name = name
        # self.name = "Sam"  # raise AttributeError: 'property' is readonly (reassigning value)

    name = property(fget=...,)           # readonly property
    age = property(fget=..., fset=...,)  # ordinary property

    
if __name__ == "__main__":
    person = Person("Tom")
    person.age = 24
    print(person.name + ',', person.age)  # Tom, 24
    # person.name = "Sam"  # raise AttributeError: 'property' is readonly
~~~~
4. To delete a property value, use the `del` operator:
~~~~python
from pymagic9 import PropertyMeta


class Person(metaclass=PropertyMeta):
    """class Person"""
    def __init__(self, name):
        self.name = name

    name = property(fget=...,)           # readonly property
    age = property(fget=..., fset=...,)  # ordinary property

    
if __name__ == "__main__":
    person = Person("Tom")
    person.age = 24
    print(person.name + ',', person.age)  # Tom, 24
    del person.name
    # print(person.name)  # raise AttributeError: auto-implemented field does not exist or has already been erased
~~~~
5. If the `getter` is specified by an empty accessor (using empty function or ellipsis), and the `setter` is not an empty function, then `setter` will also be called. This can be used as a callback when assigning a value to a property:
~~~~python
from pymagic9 import nameof, PropertyMeta


def NotifyPropertyChanged(propertyname, value):
    """Notify property changed"""
    # Do something
    print(propertyname + ',', value)


class Person(metaclass=PropertyMeta):
    """class Person"""
    def __init__(self, name):
        self.name = name

    name = property(fget=...,)           # readonly property
    age = property(fget=..., fset=...,)  # ordinary property
    
    @property
    def height(self):
        """Person height in cm"""
        return
    
    @height.setter
    def height(self, value):
        NotifyPropertyChanged(nameof(self.height), value)


if __name__ == "__main__":
    person = Person("Tom")
    person.age = 24
    print(person.name + ',', person.age)  # Tom, 24
    person.height = 180  # height, 180
~~~~
6. Similar code for `Python 2.7` looks like this:
~~~~python
from pymagic9 import nameof, PropertyMeta

__metaclass__ = PropertyMeta


def NotifyPropertyChanged(propertyname, value):
    """Notify property changed"""
    # Do something
    print(propertyname + ', ' + str(value))
    
    
class Person:
    """class Person"""
    def __init__(self, name):
        self.name = name

    name = property(fget=Ellipsis,)                # readonly property
    age = property(fget=Ellipsis, fset=Ellipsis,)  # ordinary property
    
    @property
    def height(self):
        """Person height in cm"""
        return
    
    @height.setter
    def height(self, value):
        NotifyPropertyChanged(nameof(self.height), value)


if __name__ == "__main__":
    person = Person("Tom")
    person.age = 24
    print(person.name + ', ' + str(person.age))  # Tom, 24
    person.height = 180  # height, 180
~~~~
The detailed operating principle is described in the [documentation](https://sammnnz.github.io/pymagic9/latest/api-docs/pymagic9.html#pymagic9.pymagic9.PropertyMeta).

## Compatibility

`pymagic9` is compatible with the following versions of Python:

- CPython 2.7
- CPython 3.6
- CPython 3.7
- CPython 3.8
- CPython 3.9
- CPython 3.10

It is supported on Windows, Ubuntu, and MacOS platforms.

## Documentation

For more information and detailed usage examples, please refer to the [documentation](https://sammnnz.github.io/pymagic9/).

## License

This project is licensed under the Apache License 2.0. See the [LICENSE](https://github.com/sammnnz/pymagic9/blob/master/LICENSE) file for more details.
