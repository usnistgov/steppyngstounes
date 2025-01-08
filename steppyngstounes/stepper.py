from __future__ import unicode_literals

import numpy as np

__docformat__ = 'restructuredtext'

__all__ = ["Step", "Stepper"]


class Step(object):
    """Object describing a step to take.

    Parameters
    ----------
    begin : float
        The present value of the variable to step over.
    end : float
        The desired value of the variable to step over.
    stepper : :class:`~steppyngstounes.stepper.Stepper`
        The adaptive stepper that generated this step.
    want : float
        The step size really desired if not constrained by, e.g., end of
        range.
    """
    def __init__(self, begin, end, stepper, want):
        self.begin = begin
        self.end = end
        self.stepper = stepper
        self.want = want

    @property
    def size(self):
        return self.end - self.begin

    def succeeded(self, value=None, error=None):
        """Test if step was successful.

        Parameters
        ----------
        value : float, optional
            User-determined scalar value that characterizes the last step.
            Whether this parameter is required depends on which
            :class:`~steppyngstounes.stepper.Stepper` is being used.
            (default None).
        error : float, optional
            User-determined error (positive and normalized to 1) from the
            last step.  Whether this parameter is required depends on which
            :class:`~steppyngstounes.stepper.Stepper` is being used.
            (default None).

        Returns
        -------
        bool
            Whether step was successful.  If `error` is not required,
            returns `True`.
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
    size : float
        Suggested step size to try (default None).
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).

        .. |machineepsilon| replace::   `eps`
        .. _machineepsilon:
           https://numpy.org/doc/stable/reference/generated/numpy.finfo.html

    inclusive : bool
        Whether to include an evaluation at `start` (default False).
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).
    limiting : bool
        Whether to prevent error from exceeding 1 (default False).

    """

    def __init__(self, start, stop, size=None, minStep=None,
                 inclusive=False, record=False, limiting=False):
        self.start = start
        self.stop = stop
        self._inclusive = inclusive
        self.record = record
        self.limiting = limiting

        if minStep is None:
            minStep = (stop - start) * np.finfo(float).eps
        self.minStep = minStep

        self.current = start
        self._sizes = [size or (stop - start)]
        self._steps = [start - self._sizes[-1]]
        self._successes = [True]
        self._values = [np.nan]
        self._errors = [1.]
        self._saveStep = None
        self._isDone = False

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
        passed to :class:`~steppyngstounes.stepper.Stepper` via
        :meth:`~steppyngstounes.stepper.Step.succeeded`.
        """
        return np.asarray(self._values[self._needs:])

    @property
    def errors(self):
        """`ndarray` of the "error" at each step attempt.

        The user-determined "error" scalar value (positive and normalized
        to 1) at each step attempt is passed to
        :class:`~steppyngstounes.stepper.Stepper` via
        :meth:`~steppyngstounes.stepper.Step.succeeded`.
        """
        return np.asarray(self._errors[self._needs:])

    def __iter__(self):
        return self

    def __next__(self):
        """Return the next step.

        .. note:: Py3k interface.

        Returns
        -------
        :class:`~steppyngstounes.stepper.Step`

        Raises
        ------
        StopIteration
            If there are no further steps to take
        """
        return self.next()

    def next(self):
        """Return the next step.

        .. note:: Legacy Python 2.7 support.

        Returns
        -------
        :class:`~steppyngstounes.stepper.Step`

        Raises
        ------
        StopIteration
            If there are no further steps to take
        """
        if self._isDone or self._done():
            # "Once an iterator's __next__() method raises StopIteration,
            # it must continue to do so on subsequent calls.
            # Implementations that do not obey this property are deemed
            # broken."
            # -- https://docs.python.org/3/library/stdtypes.html#iterator-types
            self._isDone = True
            raise StopIteration()

        if self._saveStep is not None:
            nextStep = self._saveStep
        elif self._successes[-1]:
            nextStep = self._adaptStep()
        else:
            nextStep = self._shrinkStep()

        want = nextStep
        nextStep = self._lowerBound(step=nextStep)
        nextStep = self._upperBound(step=nextStep)

        if self._inclusive:
            self.current -= nextStep

        if not self.record:
            self._purge()

        return Step(begin=self.current,
                    end=self.current + nextStep,
                    stepper=self,
                    want=want)

    def _succeeded(self, error):
        """Test if last step was successful.

        Returns
        -------
        success : bool
            Whether step was successful.
        error : float
            Error to record.
        """
        if self.limiting:
            success = (error <= 1.)
        else:
            success = True

        if error is None:
            error = 0.

        return success, error

    def _purge(self):
        """Discard any steps no longer needed.

        Failed steps and any successful steps no longer needed by the
        stepping algorithm are removed from the step records.
        """
        def extract(lst, keep):
            return list(np.asarray(lst)[keep])

        keep = np.nonzero(self._successes)[0]
        keep = keep[-self._needs:]

        self._steps = extract(self._steps, keep)
        self._sizes = extract(self._sizes, keep)
        self._values = extract(self._values, keep)
        self._successes = extract(self._successes, keep)
        self._errors = extract(self._errors, keep)

    def succeeded(self, step, value=None, error=None):
        """Test if step was successful.

        Stores data about the last step.

        Parameters
        ----------
        step : :class:`~steppyngstounes.stepper.Step`
            The step to test.
        value : float, optional
            User-determined scalar value that characterizes the last step.
            Whether this parameter is required depends on which
            :class:`~steppyngstounes.stepper.Stepper` is being used.
            (default None).
        error : float, optional
            User-determined error (positive and normalized to 1) from the
            last step.  Whether this parameter is required depends on which
            :class:`~steppyngstounes.stepper.Stepper` is being used.
            (default None).

        Returns
        -------
        bool
            Whether step was successful.
        """
        success, error = self._succeeded(error=error)
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

    @staticmethod
    def _stepper_test(StepperClass, steps, attempts,
                      stepper_args="record=True",
                      control_error=True):
        """Generate doctest for this Stepper

        Parameters
        ----------
        StepperClass : :class:`~steppyngstounes.stepper.Stepper`
            Class to test.
        steps : int
            Number of successful steps required.
        attempts : int
            Total number of steps required.
        stepper_args : str
            Arguments to pass to initialize class (default "record=True").
        control_error : bool
            Whether `StepperClass` uses error to control step size.
        """

        instantiation = "stepper = {StepperClass}".format(**locals())
        indent = " " * len(instantiation)

        test = r"""

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

       >>> totaltime = 1000.
       >>> width = 0.01

       The scaled "error" will be a measure of how much the solution has
       changed since the last step, \| `new` - `old` \| / `errorscale`).

       >>> errorscale = 1e-2

       Iterate over the stepper from `start` to `stop` (inclusive of
       calculating a value at `start`).

       """

        if control_error:
            test += r"""
       >>> old = -1."""

        test += r"""
       >>> {instantiation}(start=0., stop=totaltime, inclusive=True,
       ... {indent} {stepper_args})
       >>> for step in stepper:
       ...     new = np.tanh((step.end / totaltime - 0.5) / (2 * width))
       ..."""

        if control_error:
            test += r"""
       ...     error = abs(new - old) / errorscale
       ...
       ...     if step.succeeded(value=new, error=error):
       ...         old = new"""
        else:
            test += r"""
       ...     _ = step.succeeded(value=new)"""

        test += r"""

       >>> s = "{{}} succesful steps in {{}} attempts"
       >>> print(s.format(stepper.successes.sum(),
       ...                len(stepper.steps)))
       {steps} succesful steps in {attempts} attempts

       >>> steps = stepper.steps[stepper.successes]
       >>> ix = steps.argsort()
       >>> values = stepper.values[stepper.successes][ix]
       >>> errors = abs(values[1:] - values[:-1]) / errorscale"""

        if control_error:
            test += r"""

       Check that the post hoc error satisfies the desired tolerance.

       >>> print(max(errors) < 1.)
       True"""
        else:
            test += r"""

       As this stepper doesn't use the error, we don't expect the post
       hoc error to satisfy the tolerance."""

        if control_error:
            max_error = 1.1
        else:
            max_error = None

        test += r"""

    .. plot::
       :context:
       :alt: Plot of successful steps and trajectory of attempts.

       >>> def plotSteps():
       ...     from matplotlib import pyplot as plt
       ...
       ...     plt.rcParams['lines.linestyle'] = ""
       ...     plt.rcParams['lines.marker'] = "."
       ...     plt.rcParams['lines.markersize'] = 3
       ...     fig, axes = plt.subplots(2, 2, sharex=True)
       ...
       ...     fig.suptitle(r"{steps} successful $\mathtt{{{StepperClass}}}$ "
       ...                  r"steps and trajectory of {attempts} attempts")
       ...
       ...     axes[0, 0].plot(stepper.steps, stepper.values, color="gray",
       ...                     linestyle="-", linewidth=0.5, marker="")
       ...     axes[0, 0].plot(stepper.steps[stepper.successes],
       ...                     stepper.values[stepper.successes])
       ...     axes[0, 0].set_ylabel("value")
       ...
       ...     # plot post-hoc step size and error
       ...     # reorder, as steps may not be monotonic
       ...
       ...     steps = stepper.steps[stepper.successes]
       ...     ix = steps.argsort()
       ...     values = stepper.values[stepper.successes][ix]
       ...     errors = abs(values[1:] - values[:-1]) / errorscale
       ...
       ...     axes[1, 0].semilogy(steps[1:], steps[1:] - steps[:-1])
       ...     axes[1, 0].set_ylabel(r"$\Delta t$")
       ...     axes[1, 0].set_xlabel(r"$t$")
       ...
       ...     axes[0, 1].plot(steps[1:], errors)
       ...     axes[0, 1].axhline(y=1., color="red",
       ...                        linestyle="-", linewidth=0.5, marker="")
       ...     axes[0, 1].set_ylabel("error")
       ...     axes[0, 1].set_ylim(ymin=1e-17, ymax={max_error})
       ...
       ...     axes[1, 1].semilogy(steps[1:], errors)
       ...     axes[1, 1].axhline(y=1., color="red",
       ...                        linestyle="-", linewidth=0.5, marker="")
       ...     axes[1, 1].set_ylabel("error")
       ...     axes[1, 1].set_xlabel(r"$t$")
       ...     axes[1, 1].set_ylim(ymin=1e-17, ymax={max_error})
       ...
       ...     plt.tight_layout(rect=[0, 0, 1, 0.95])
       ...     plt.show()

       >>> plotSteps() # doctest: +SKIP"""

        return test.format(**locals())

    _stepper_test_args = "record=True"
