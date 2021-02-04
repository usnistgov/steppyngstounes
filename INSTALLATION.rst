Installation
============

Dependencies
------------

The prerequisites for steppyngstounes can be installed using `pip`__ or
`conda`__.

__ https://pip.pypa.io/
__ https://docs.conda.io/

Using
^^^^^

- `numpy`__
- `scipy`__

__ https://numpy.org/
__ https://scipy.org/

Testing
^^^^^^^

- `pytest`__

__ https://pytest.org/

Documenting
^^^^^^^^^^^

- `sphinx`__ >= 3.1
- `matplotlib`__

__ https://www.sphinx-doc.org/
__ https://matplotlib.org/

Alternative
^^^^^^^^^^^

The steppyngstounes package uses tox__ for configuration and testing.  You
may choose to install only this package and allow it to obtain any
additional packages and create virtual environments for the tasks below.

__ https://tox.readthedocs.io/

Installing
----------

Obtain the source code from GitHub__. Within the source directory::

  $ pip install -e .

__ https://github.com/guyer/steppyngstounes

Testing
-------

Within the source directory::

  $ pytest

Alternatively::

  $ tox

Building the Documentation
--------------------------

::

  $ python setup.py build_sphinx

Alternatively::

  $ tox -e docs

Documentation can be found in :file:`{STEPPYNGSTOUNES}/build/sphinx/html`.

If the figures do not update

::

  $ touch docs/_autosummary/*.rst

and repeat.

If the documentation seems not to build correctly in other respects::

  $ python setup.py build_sphinx --all-files --fresh-env
