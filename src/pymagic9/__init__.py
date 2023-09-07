"""
PyMagic9 - a library for analyzing call stacks using frames.
"""
from .pymagic9 import getframe, isfunctionincallchain, nameof

__author__ = 'Sam Nazarov'  # Duplicate in setup.cfg
__version__ = '0.9.0a'

# noinspection SpellCheckingInspection
__all__ = ['getframe', 'isfunctionincallchain', 'nameof']
