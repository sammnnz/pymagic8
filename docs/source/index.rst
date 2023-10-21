.. pymagic9 documentation master file, created by
   sphinx-quickstart on Mon Jul 31 00:54:25 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to pymagic9's documentation!
====================================

This is a Python library based on calling the stack of frames at runtime and analyzing the code object of frames.
Basically, it implements some C# features. For example, it contains the :ref:`nameof <nameof>` function and
:ref:`auto-implemented properties <PropertyMeta>`.

Installation
------------

You can install `pymagic9` using pip:

.. code-block:: shell

   pip install pymagic9


.. toctree::
   :maxdepth: 2
   :caption: Contents

   api-docs/index.rst
   api-docs/pymagic9.rst

Compatibility
-------------

`pymagic9` is compatible with the following versions of Python:

* CPython 2.7
* CPython 3.6
* CPython 3.7
* CPython 3.8
* CPython 3.9
* CPython 3.10

License
-------

This project is licensed under the Apache License 2.0. See the `LICENSE <https://github.com/sammnnz/pymagic9/blob/master/LICENSE>`_ file for more details.

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
