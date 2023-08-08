pymagic9
=========================

.. automodule:: pymagic9.pymagic9
   :members:
   :exclude-members: getframe

   .. function:: getframe(__depth=0)

      The `sys._getframe <https://docs.python.org/3/library/sys.html?highlight=_getframe#sys._getframe>`_ function is
      used here if it exists in the version of python being used. Otherwise, the :ref:`_getframe <private-getframe>`
      polyfill is used.

   .. _private-getframe:

   .. autofunction:: pymagic9.pymagic9._getframe

   .. autofunction:: pymagic9.pymagic9._get_argval
   .. autofunction:: pymagic9.pymagic9._get_last_name
   .. autofunction:: pymagic9.pymagic9._unpack_opargs
