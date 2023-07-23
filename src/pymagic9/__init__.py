"""
PyMagic9 - a library that uses frames to analyze a call stack.
"""
from .pymagic9 import getframe, isfunctionincallchain, nameof

# noinspection SpellCheckingInspection
__all__ = ['getframe', 'isfunctionincallchain', 'nameof']
