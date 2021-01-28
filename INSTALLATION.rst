Installation
============

Dependencies
------------

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

Installing
----------

::

  $ python setup.py install

Testing
-------

::

  $ pytest

Building the Documentation
--------------------------

::

  $ python setup.py build_sphinx

If the figures do not update

::

  $ touch docs/_autosummary/*.rst

and repeat.

If the documentation seems not to build correctly in other respects::

  $ python setup.py build_sphinx --all-files --fresh-env

Documentation can be found in :file:`{STEPPYNGSTOUNES}/build/sphinx/html`.
