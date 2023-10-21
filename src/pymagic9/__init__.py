"""
PyMagic9 - a library based on calling the stack of frames at runtime and analyzing the code object of frames.
Basically, it implements some C# features. For example, it contains the `nameof` function and `auto-implemented
properties`. See the documentation for more information.
"""
from .pymagic9 import getframe, isemptyfunction, isfunctionincallchain, nameof, PropertyMeta

__author__ = 'Sam Nazarov'  # Duplicate in setup.cfg
__version__ = '0.9.0a'

# noinspection SpellCheckingInspection
__all__ = ['getframe', 'isemptyfunction', 'isfunctionincallchain', 'nameof', 'PropertyMeta']
