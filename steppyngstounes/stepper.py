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
    begin : float
        The present value of the variable to step over.
    end : float
        The desired value of the variable to step over.
    stepper : ~steppyngstounes.stepper.Stepper
        The adaptive stepper that generated this step.
    """
    def __init__(self, begin, end, stepper):
        self.begin = begin
        self.end = end
        self.stepper = stepper

    def succeeded(self, value, error):
        """Test if step was successful.

        Parameters
        ----------
        value : float
            User-determined scalar value that characterizes the last step.
        error : float
            User-determined error (positive and normalized to 1) from the
            last step.

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
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).

        .. |machineepsilon| replace::   `eps`
        .. _machineepsilon:             https://numpy.org/doc/stable/reference/generated/numpy.finfo.html

    inclusive : bool
        Whether to include an evaluation at `start` (default False).
    recorded : bool
        Whether to keep history of steps, errors, values, etc. (default False).

    Yields
    ------
    ~steppyngstounes.stepper.Step

    """

    def __init__(self, start, stop, tryStep=None, minStep=None,
                 inclusive=False, recorded=False):
        self.start = start
        self.stop = stop
        self._inclusive = inclusive
        self.recorded = recorded

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
        self._needs = 1

    @property
    def steps(self):
        """`ndarray` of values of the control variable attempted so far.
        """
        return np.asarray(self._steps[self._needs:])

    @property
    def sizes(self):
        """`ndarray` of the step size at each step attempt.
        """
        return np.asarray(self._sizes[self._needs:])

    @property
    def successes(self):
        """`ndarray` of whether the step was successful at each step attempt.
        """
        return np.asarray(self._successes[self._needs:])

    @property
    def values(self):
        """`ndarray` of the "value" at each step attempt.

        The user-determined scalar value at each step attempt is
        passed to :class:`~steppyngstounes.Stepper` via
        :meth:`~steppyngstounes.Step.succeeded`.
        """
        return np.asarray(self._values[self._needs:])

    @property
    def errors(self):
        """`ndarray` of the "error" at each step attempt.

        The user-determined "error" scalar value (positive and normalized
        to 1) at each step attempt is passed to
        :class:`~steppyngstounes.Stepper` via
        :meth:`~steppyngstounes.Step.succeeded`.
        """
        return np.asarray(self._errors[self._needs:])

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self._saveStep is not None:
            nextStep = self._saveStep
        elif self._successes[-1]:
            nextStep = self._adaptStep()
        else:
            nextStep = self._shrinkStep()

        nextStep = self._lowerBound(step=nextStep)
        nextStep = self._upperBound(step=nextStep)

        if self._inclusive:
            self.current -= nextStep

        if not self.recorded:
            self._purge()

        if self._done():
            raise StopIteration()

        return Step(begin=self.current, end=self.current + nextStep, stepper=self)

    def _succeeded(self, error):
        """Test if last step was successful.
        """
        return (error <= 1.)

    def _purge(self):
        """Discard any steps no longer needed.

        Failed steps and any successful steps no longer needed by the
        stepping algorithm are removed from the step records.
        """
        def extract(l, keep):
            return list(np.asarray(l)[keep])

        keep = np.nonzero(self._successes)[0]
        keep = keep[-self._needs:]

        self._steps = extract(self._steps, keep)
        self._sizes = extract(self._sizes, keep)
        self._values = extract(self._values, keep)
        self._successes = extract(self._successes, keep)
        self._errors = extract(self._errors, keep)

    def succeeded(self, step, value, error):
        """Test if step was successful.

        Stores data about the last step.

        Parameters
        ----------
        step : ~steppyngstounes.stepper.Step
            The step to test.
        value : float
            User-determined scalar value that characterizes the last step.
        error : float
            User-determined error (positive and normalized to 1) from the
            last step.

        Returns
        -------
        bool
            Whether step was successful.
        """
        success = self._succeeded(error=error)
        if self._inclusive:
            success = True
            self._inclusive = False

        self._steps.append(step.end)
        self._sizes.append(step.end - step.begin)
        self._values.append(value)
        self._successes.append(success)

        # don't let error be zero
        self._errors.append(error + np.finfo(float).eps)

        if success:
            self.current = step.end
        else:
            self._saveStep = None

        return success

    def _lowerBound(self, step):
        """Determine minimum step.

        Parameters
        ----------
        step : float
            Desired step.

        Returns
        -------
        float
            Maximum magnitude of `step` and `self.minStep`.

        Raises
        ------
        FloatingPointError
            If the resulting step would underflow.

        """
        if step < 0:
            sign = -1
        else:
            sign = 1
        step = sign * max(abs(step), abs(self.minStep))
        if self.current + step == self.current:
            raise FloatingPointError("step size underflow: %g + %g == %g"
                                     % (self.current, step, self.current))

        return step

    def _upperBound(self, step):
        """Determine maximum step.

        Parameters
        ----------
        step : float
            Desired step.

        Returns
        -------
        float
            Maximum magnitude of `step` and distance remaining to
            `self.stop`.

        """
        maxStep = self.stop - self.current

        if abs(step) > abs(maxStep):
            self._saveStep = step
            step = maxStep
        else:
            self._saveStep = None

        return step

    def _shrinkStep(self):
        """Reduce step after failure

        Most subclasses of :class:`~steppyngstounes.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that failed.
        error : float
            Error (positive and normalized to 1) from the last step.

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1]

    def _adaptStep(self):
        """Calculate next step after success

        Most subclasses of :class:`~steppyngstounes.stepper.Stepper` should
        override this method (default returns last step unchanged).

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1]

    def _done(self):
        """Determine if stepper has reached objective.

        Returns
        -------
        bool

        """
        return self.current == self.stop

    _stepper_test = r"""

    Examples
    --------

    .. plot::
       :context: reset
       :include-source:
       :nofigs:

       >>> import numpy as np
       >>> from steppyngstounes import {StepperClass}

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
       >>> stepper = {StepperClass}(start=0., stop=totaltime, tryStep=dt,
       ...                          inclusive=True, recorded=True)
       >>> for step in stepper:
       ...     new = np.tanh((step.end / totaltime - 0.5) / (2 * width))
       ...
       ...     error = abs(new - old) / errorscale
       ...
       ...     if step.succeeded(value=new, error=error):
       ...         old = new

       >>> s = "{{}} succesful steps in {{}} attempts"
       >>> print(s.format(stepper.successes.sum(),
       ...                len(stepper.steps)))
       {steps} succesful steps in {attempts} attempts

       Ensure solution tolerance is achieved.

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
