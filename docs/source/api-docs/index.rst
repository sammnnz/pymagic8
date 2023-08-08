PyMagic9 lib
============

.. automodule:: pymagic9
   :members:
   :exclude-members: getframe

   .. function:: getframe(__depth=0)

      The `sys._getframe <https://docs.python.org/3/library/sys.html?highlight=_getframe#sys._getframe>`_ function is
      used here if it exists in the version of python being used. Otherwise, the :ref:`_getframe <private-getframe>`
      polyfill is used.

.. toctree::
   :maxdepth: 2

   pymagic9.rst