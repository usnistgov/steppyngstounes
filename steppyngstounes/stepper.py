from __future__ import unicode_literals
from builtins import object

import numpy as np

__docformat__ = 'restructuredtext'

__all__ = ["Step", "Stepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class Step(object):
    """Object describing a step to take.

    Parameters
    ----------
    current : float
        The present value of the variable to step over.
    size : float
        The amount to change the value of the variable to step over.
    stepper : ~fipy.steppers.stepper.Stepper
        The adaptive stepper that generated this step.
    """
    def __init__(self, current, size, stepper):
        self.current = current
        self.size = size
        self.stepper = stepper

    def succeeded(self, value, error):
        """Test if step was successful.

        Parameters
        ----------
        value : float
            User-determined scalar value that characterizes the last solve.
        error : float
            User-determined error (positive and normalized to 1) from the
            last solve.

        Returns
        -------
        bool
            Whether step was successful.
        """
        return self.stepper.succeeded(step=self, value=value, error=error)

class Stepper(object):
    r"""Adaptive stepper base class.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    tryStep : float
        Suggested step size to try (default None).
    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    minStep : ~fipy.steppers.stepper.Step
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).

        .. |machineepsilon| replace::   `eps`
        .. _machineepsilon:             https://numpy.org/doc/stable/reference/generated/numpy.finfo.html

    Yields
    ------
    ~fipy.steppers.stepper.Step

    """

    _stepper_test = r"""

    Examples
    --------

    .. plot::
       :context: reset
       :include-source:
       :nofigs:

       >>> import numpy as np
       >>> from fipy.steppers import {StepperClass}

       We'll demonstrate using an artificial function that changes
       abruptly, but smoothly, with time,

       .. math::

          \tanh\frac{{\frac{{t}}{{t_\mathrm{{max}}}} - \frac{{1}}{{2}}}}
                      {{2 w}}

       where :math:`t` is the elapsed time, :math:`t_\mathrm{{max}}` is
       total time desired, and :math:`w` is a measure of the step width.

       >>> dt = {dt}
       >>> totaltime = 1000.
       >>> width = 0.01

       The scaled "error" will be a measure of how much the solution has
       changed since the last step :math:`\|\mathtt{{new}} -
       \mathtt{{old}}\|_1 / \mathtt{{errorscale}}`).

       >>> errorscale = 1e-2

       Iterate over the stepper from `start` to `stop` (inclusive of
       calculating a value at `start`), using a suggested initial step size
       of `tryStep`.

       >>> old = -1.
       >>> stepper = {StepperClass}(start=0., stop=totaltime, tryStep=dt, inclusive=True)
       >>> for step in stepper:
       ...     t = step.current + step.size
       ...     new = np.tanh((t / totaltime - 0.5) / (2 * width))
       ...
       ...     error = abs(new - old) / errorscale
       ...
       ...     if step.succeeded(value=new, error=error):
       ...         old = new

       >>> s = "{{}} succesful steps in {{}} attempts"
       >>> print(s.format(len(stepper.steps[stepper.successes]),
       ...                len(stepper.steps)))
       {steps} succesful steps in {attempts} attempts

       Ensure solution tolerance is achieved (aside from a few "starter"
       steps).

       >>> print(max(stepper.errors[stepper.successes]) < 1.)
       True

    .. plot::
       :context:
       :alt: Plot of successful steps and trajectory of attempts.

       >>> def plotSteps():
       ...     from matplotlib import pyplot as plt
       ...
       ...     plt.rcParams['lines.linestyle'] = ""
       ...     plt.rcParams['lines.marker'] = "."
       ...     plt.rcParams['lines.markersize'] = 3
       ...     fix, axes = plt.subplots(2, 2, sharex=True)
       ...
       ...     axes[0, 0].plot(stepper.steps, stepper.values, color="gray",
       ...                     linestyle="-", linewidth=0.5, marker="")
       ...     axes[0, 0].plot(stepper.steps[stepper.successes],
       ...                     stepper.values[stepper.successes])
       ...     axes[0, 0].set_ylabel(r"$\phi$")
       ...
       ...     axes[1, 0].semilogy(stepper.steps[stepper.successes],
       ...                         stepper.sizes[stepper.successes])
       ...     axes[1, 0].set_ylabel(r"$\Delta t$")
       ...     axes[1, 0].set_xlabel(r"$t$")
       ...
       ...     axes[0, 1].plot(stepper.steps[stepper.successes],
       ...                     stepper.errors[stepper.successes])
       ...     axes[0, 1].set_ylabel("error")
       ...     axes[0, 1].set_ylim(ymin=1e-17, ymax=1.1)
       ...
       ...     axes[1, 1].semilogy(stepper.steps[stepper.successes],
       ...                         stepper.errors[stepper.successes])
       ...     axes[1, 1].set_ylabel("error")
       ...     axes[1, 1].set_xlabel(r"$t$")
       ...     axes[1, 1].set_ylim(ymin=1e-17, ymax=1.1)
       ...
       ...     plt.tight_layout()
       ...     plt.show()

       >>> plotSteps() # doctest: +SKIP

    """

    def __init__(self, start, stop, tryStep=None, inclusive=False, minStep=None):
        self.start = start
        self.stop = stop
        self.inclusive = inclusive

        if minStep is None:
            minStep = (stop - start) * np.finfo(float).eps
        self.minStep = minStep

        self.current = start
        self._sizes = [tryStep or (stop - start)]
        self._steps = [start - self._sizes[-1]]
        self._successes = [True]
        self._values = [np.NaN]
        self._errors = [1.]
        self._saveStep = None

        # number of artificial steps needed by the algorithm
        self._bogus = 1

    @property
    def steps(self):
        """`ndarray` of values of the control variable attempted so far.
        """
        return np.asarray(self._steps[self._bogus:])

    @property
    def sizes(self):
        """`ndarray` of the step size at each step attempt.
        """
        return np.asarray(self._sizes[self._bogus:])

    @property
    def successes(self):
        """`ndarray` of whether the step was successful at each step attempt.
        """
        return np.asarray(self._successes[self._bogus:])

    @property
    def values(self):
        """`ndarray` of the "value" at each step attempt.

        The user-determined scalar value at each step attempt is
        passed to :class:`~fipy.steppers.Stepper` via
        :meth:`~fipy.steppers.Step.succeeded`.
        """
        return np.asarray(self._values[self._bogus:])

    @property
    def errors(self):
        """`ndarray` of the "error" at each step attempt.

        The user-determined "error" scalar value (positive and normalized
        to 1) at each step attempt is passed to
        :class:`~fipy.steppers.Stepper` via
        :meth:`~fipy.steppers.Step.succeeded`.
        """
        return np.asarray(self._errors[self._bogus:])

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._saveStep is not None:
            nextStep = self._saveStep
        elif self._successes[-1]:
            nextStep = self._calcNext()
        else:
            nextStep = self._shrinkStep()

        nextStep = self._lowerBound(tryStep=nextStep)

        maxStep = self.stop - self.current
        if self._done(maxStep=maxStep):
            raise StopIteration()

        if abs(nextStep) > abs(maxStep):
            self._saveStep = nextStep
            nextStep = maxStep
        else:
            self._saveStep = None

        return Step(current=self.current, size=nextStep, stepper=self)

    def _succeeded(self, error):
        return error <= 1.

    def succeeded(self, step, value, error):
        self._steps.append(step.current + step.size)
        self._sizes.append(step.size)

        # don't let error be zero
        self._errors.append(error + np.finfo(float).eps)

        self._values.append(value)

        success = self._succeeded(error=error)
        self._successes.append(success)

        if success:
            self.current = self._steps[-1]
        else:
            self._saveStep = None

        return success

    def _lowerBound(self, tryStep):
        """Determine minimum step.

        Parameters
        ----------
        tryStep : float
            Desired step.

        Returns
        -------
        float
            Maximum magnitude of `tryStep` and `self.minStep`.

        Raises
        ------
        FloatingPointError
            If the resulting step would underflow.

        """
        if tryStep < 0:
            sign = -1
        else:
            sign = 1
        tryStep = sign * max(abs(tryStep), abs(self.minStep))
        if self.current + tryStep == self.current:
            raise FloatingPointError("step size underflow: %g + %g == %g" % (self.current, tryStep, self.current))

        return tryStep

    def _shrinkStep(self):
        """Reduce step after failure

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that failed.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1]

    def _calcNext(self):
        """Calculate next step after success

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that succeeded.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1]

    def _failed(self, triedStep, error, attempts):
        """Determine if most recent attempt failed

        Parameters
        ----------
        triedStep : float
            Step that was attempted.
        error : float
            Error (positive and normalized to 1) from the last solve.
        attempts : int
            Number of failed attempts so far.

        Returns
        -------
        bool
        """
        return ((error > 1. or attempts > (self.maxattempts + 1))
                and triedStep > self.minStep)

    def _done(self, maxStep):
        """Determine if stepper has reached objective.

        Parameters
        ----------
        maxStep : float
            Maximum step size to attempt.

        Returns
        -------
        bool

        """
        return maxStep == 0
