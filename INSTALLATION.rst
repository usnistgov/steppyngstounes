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

  $ make -C docs html

If the figures do not update

::

  $ touch docs/_autosummary/*.rst

and repeat.

Documentation can be found in :file:`{STEPPYNGSTOUNES}/docs/_build/html/`.
