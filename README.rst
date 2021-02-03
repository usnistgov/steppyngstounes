**steppyngstounes** / ˈstɛp ɪŋˌstoʊnz /

  1.  *pl. n.* *[Middle English]* Stones used as steps of a stairway;
  also, stones in a stream used for crossing.  [#]_
  
      *...while at Calais in 1474 we find 40 'steppyngstounes' bought for
      the stairways of the town.* [#]_

  
  2.  *n.* *[chiefly Pythonic]* A package that provides iterators for
  advancing from `start` to `stop`, subject to algorithms that depend on
  user-defined `value` or `error`.

|CircleCI| |GitHub| |Codacy|

Computations that evolve in time or sweep a variable often boil down to a
control loop like

.. code-block:: python

   for step in range(steps):
       do_something(step)

or

.. code-block:: python

   t = 0
   while t < totaltime:
       t += dt
       do_something(dt)

which works well enough, until the size of the steps needs to change.  This
can be either to save or plot results at some fixed points, or because the
computation becomes either harder or easier to perform.  The control loop
then starts to dominate the script, obscuring the interesting parts of the
computation, particularly as different edge cases are accounted for.

Packages like `odeint`_ address many of these issues, but do so through
callback functions, which effectively turn the computation of interest
inside out, again obscuring the interesting bits.  Further, because they
are often tailored for applications like solving ordinary differential
equations, applying them to other stepping problems, even `solving partial
differential equations`_, can be rather opaque.

The steppyngstounes package is designed to retain the simplicity of the
original control loop, while allowing great flexibility in how steps are
taken and automating all of the aspects of increasing and decreasing the
step size.

A steppyngstounes control loop can be as simple as

.. code-block:: python

   from steppyngstounes import FixedStepper

   for step in FixedStepper(start=0., stop=totaltime, size=dt):
       do_something(step.size)

       _ = step.succeeded()

which replicates the :keyword:`while` construct above, but further ensures
that ``totaltime`` is not overshot if it isn't evenly divisible by ``dt``.

.. attention::

   The call to :meth:`~steppyngstounes.stepper.Step.succeeded` informs the
   :class:`~steppyngstounes.stepper.Stepper` to advance, otherwise it will
   iterate on the same step indefinitely.

Rather than manually incrementing the control variable (e.g., ``t``), the
values of the control variable before and after the step are available as
the :class:`~steppyngstounes.stepper.Step` attributes
:attr:`~steppyngstounes.stepper.Step.begin` and
:attr:`~steppyngstounes.stepper.Step.end`.  The attribute
:attr:`~steppyngstounes.stepper.Step.size` is a shorthand for
``step.end - step.begin``.

If the size of the steps should be adjusted by some characteristic of the
calculation, such as the change in the value since the last solution, the
error (normalized to 1) can be passed to
:meth:`~steppyngstounes.stepper.Step.succeeded`, causing the
:class:`~steppyngstounes.stepper.Stepper` to advance (possibly adjusting
the next step size) or to retry the step with a smaller step size.

.. code-block:: python

   from steppyngstounes import SomeStepper

   old = initial_condition
   for step in SomeStepper(start=0., stop=totaltime, size=dt):
       new = do_something_else(step.begin, step.end, step.size)

       err = (new - old) / scale

       if step.succeeded(error=err):
           old = new
           # do happy things
       else:
           # do sad things


A hierarchy of :class:`~steppyngstounes.stepper.Stepper` iterations enables
saving or plotting results at fixed, possibly irregular, points, while
allowing an adaptive :class:`~steppyngstounes.stepper.Stepper` to find the
most efficient path between those checkpoints.

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

A variety of stepping algorithms are described and demonstrated in the
documentation of the individual :mod:`steppyngstounes` classes.

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

.. _odeint: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.odeint.html
.. _solving partial differential equations: https://www.ctcms.nist.gov/fipy

.. |CircleCI|      image:: https://circleci.com/gh/guyer/steppyngstounes.svg?style=svg
    :target: https://circleci.com/gh/guyer/steppyngstounes
.. |Codacy|        image:: https://app.codacy.com/project/badge/Grade/442966c7b8a24ca4af23a31fe4ac2df8
    :target: https://www.codacy.com/gh/guyer/steppyngstounes/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=guyer/steppyngstounes&amp;utm_campaign=Badge_Grade
.. |GitHub|        image:: https://img.shields.io/github/contributors/guyer/steppyngstounes.svg
    :target: https://github.com/guyer/steppyngstounes
