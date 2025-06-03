**steppyngstounes** / ˈstɛp ɪŋˌstoʊnz /

  1.  *pl. n.* *[Middle English]* Stones used as steps of a stairway;
  also, stones in a stream used for crossing.  [#]_
  
      *...while at Calais in 1474 we find 40 'steppyngstounes' bought for
      the stairways of the town.* [#]_

  
  2.  *n.* *[chiefly Pythonic]* A package that provides iterators for
  advancing from `start` to `stop`, subject to algorithms that depend on
  user-defined `value` or `error`.

|Testing| |Documentation| |Linting| |GitHub| |Codacy|

* **Documentation:** https://pages.nist.gov/steppyngstounes/en/latest
* **Discussion:** https://github.com/usnistgov/steppyngstounes/discussions
* **Source code:** https://github.com/usnistgov/steppyngstounes
* **Bug reports:** https://github.com/usnistgov/steppyngstounes/issues

A steppyngstounes control loop replaces an iteration loop like

.. code-block:: python

   for step in range(steps):
       do_something(step)

It can be as simple as

.. code-block:: python

   from steppyngstounes import FixedStepper

   for step in FixedStepper(start=0., stop=totaltime, size=dt):
       do_something(step.size)

       _ = step.succeeded()

or a more elaborate combination of checkpoints and adaptive steps

.. code-block:: python

   from steppyngstounes import CheckpointStepper, SomeStepper

   old = initial_condition
   for checkpoint in CheckpointStepper(start=0.,
                                       stops=[1e-3, 1, 1e3, 1e6]):

       for step in SomeStepper(start=checkpoint.begin,
                               stop=checkpoint.end,
                               size=checkpoint.size):

           new = do_something_else(step.begin, step.end, step.size)

           err = (new - old) / scale

           if step.succeeded(error=err):
               old = new
               # do happy things
           else:
               # do sad things

       save_or_plot()

       _ = checkpoint.succeeded()

Steppyngstounes requires `numpy`, `scipy`, and `pytest`.
Tests can be run with

.. code-block:: shell

   pytest

----

.. [#] *Middle English Dictionary*,
    Ed.  Robert E. Lewis, *et al.*,
    Ann Arbor: University of Michigan Press, 1952-2001.
    Online edition in *Middle English Compendium*,
    Ed.  Frances McSparran, *et al.*,
    Ann Arbor: University of Michigan Library, 2000-2018.
    <https://quod.lib.umich.edu/m/middle-english-dictionary/dictionary/MED42815>.
    Accessed 16 December 2020.

.. [#] *Building in England, Down to 1540: A Documentary History*,
    L. F. Salzman, Clarenden Press, Oxford, 1952.
    <https://books.google.com/books?id=WtZPAAAAMAAJ&focus=searchwithinvolume&q=steppyngstounes>.
    Accessed 16 December 2020.

.. |Testing|       image:: https://github.com/usnistgov/steppyngstounes/actions/workflows/testing-and-coverage.yml/badge.svg
    :target: https://github.com/usnistgov/steppyngstounes/actions/workflows/testing-and-coverage.yml
.. |Documentation| image:: https://github.com/usnistgov/steppyngstounes/actions/workflows/Docs4NIST.yml/badge.svg
    :target: https://github.com/usnistgov/steppyngstounes/actions/workflows/Docs4NIST.yml
.. |Linting|       image:: https://github.com/usnistgov/steppyngstounes/actions/workflows/linting-and-spelling.yml/badge.svg
    :target: https://github.com/usnistgov/steppyngstounes/actions/workflows/linting-and-spelling.yml
.. |Codacy|        image:: https://app.codacy.com/project/badge/Grade/442966c7b8a24ca4af23a31fe4ac2df8
    :target: https://www.codacy.com/gh/guyer/steppyngstounes/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=guyer/steppyngstounes&amp;utm_campaign=Badge_Grade
.. |GitHub|        image:: https://img.shields.io/github/contributors/guyer/steppyngstounes.svg
    :target: https://github.com/guyer/steppyngstounes
