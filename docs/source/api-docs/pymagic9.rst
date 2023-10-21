pymagic9.py
=========================

.. automodule:: pymagic9.pymagic9
   :members:
   :exclude-members: getframe, isemptyfunction, isfunctionincallchain, nameof, PropertyMeta

   .. _PropertyMeta:

   .. autoclass:: pymagic9.pymagic9.PropertyMeta

   .. function:: getframe(__depth=0)

      The `sys._getframe <https://docs.python.org/3/library/sys.html?highlight=_getframe#sys._getframe>`_ function is
      used here if it exists in the version of python being used. Otherwise, the :ref:`_getframe <private-getframe>`
      polyfill is used.

   .. autofunction:: pymagic9.pymagic9.isemptyfunction
   .. autofunction:: pymagic9.pymagic9.isfunctionincallchain

   .. _nameof:

   .. autofunction:: pymagic9.pymagic9.nameof

   .. _private-getframe:

   .. autofunction:: pymagic9.pymagic9._getframe

   .. autofunction:: pymagic9.pymagic9._unpack_opargs
