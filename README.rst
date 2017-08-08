|logo|


Limonado: Tornado API Tools
****************************

.. image:: https://img.shields.io/travis/gakhov/limonado/master.svg?style=flat-square
    :target: https://travis-ci.org/gakhov/limonado
    :alt: Travis Build Status

.. image:: https://img.shields.io/github/release/gakhov/limonado.svg?style=flat-square
    :target: https://github.com/gakhov/limonado/releases
    :alt: Current Release Version

.. image:: https://img.shields.io/pypi/v/limonado.svg?style=flat-square
    :target: https://pypi.python.org/pypi/limonado
    :alt: pypi Version

.. image:: https://readthedocs.org/projects/pip/badge/?version=latest&style=flat-square
    :target: http://limonado.readthedocs.io/en/latest/
    :alt: Documentation Version

.. image:: https://coveralls.io/repos/github/gakhov/limonado/badge.svg?branch=master
   :target: https://coveralls.io/github/gakhov/limonado?branch=master&style=flat-squar


.. contents ::


Introduction
------------


Dependencies
---------------------



Documentation
--------------

The latest documentation can be found at `<http://limonado.readthedocs.io/en/latest/>`_


License
-------

MIT License


Source code
-----------

* https://github.com/gakhov/limonado/


Authors
-------

* `Andrii Gakhov @gakhov`
* `Jean Vancoppenolle @jvcop`


Install with pip
--------------------

Installation requires a working build environment.

.. code:: bash

    $ pip3 install -U limonado

When using pip it is generally recommended to install packages in a ``virtualenv``
to avoid modifying system state:

.. code:: bash

    $ virtualenv .env -p python3 --no-site-packages
    $ source .env/bin/activate
    $ pip3 install -U limonado


Compile from source
---------------------

The other way to install Limonado is to clone its
`GitHub repository <https://github.com/gakhov/limonado>`_ and build it from
source.

.. code:: bash

    $ git clone https://github.com/gakhov/limonado.git
    $ cd limonado

    $ make build

    $ bin/pip3 install -r requirements-dev.txt
    $ make tests


.. |logo| image:: https://raw.githubusercontent.com/gakhov/limonado/master/docs/_static/logo.png
