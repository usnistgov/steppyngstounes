from __future__ import division
from __future__ import unicode_literals

from steppyngstounes.stepper import Stepper

__all__ = ["ScaledStepper"]


class ScaledStepper(Stepper):
    r"""Adaptive stepper that adjusts the step by fixed factors.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = f_\text{grow} \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`f_\text{grow}` is the factor by which to grow the step size.

    On failure, retries with

    .. math::

       \Delta_{n} = f_\text{shrink} \Delta_n

    where :math:`f_\text{shrink}` is the factor by which to shrink the step
    size.

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
        Whether to include an evaluation at `start` (default False)
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).
    growFactor : float
        Growth factor :math:`f_\text{grow}` (default 1.2).
    shrinkFactor : float
        Shrinkage factor :math:`f_\text{shrink}` (default 0.5).

    """

    __doc__ += Stepper._stepper_test(StepperClass="ScaledStepper",
                                     steps=296,
                                     attempts=377)

    def __init__(self, start, stop, size=None, minStep=None,
                 inclusive=False, record=False,
                 growFactor=1.2, shrinkFactor=0.5):
        super(ScaledStepper, self).__init__(start=start,
                                            stop=stop,
                                            size=size,
                                            minStep=minStep,
                                            inclusive=inclusive,
                                            record=record,
                                            limiting=True)
        self.growFactor = growFactor
        self.shrinkFactor = shrinkFactor

    def _shrinkStep(self):
        """Reduce step after failure

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1] * self.shrinkFactor

    def _adaptStep(self):
        """Calculate next step after success

        Returns
        -------
        float
            New step.

        """
        return self._sizes[-1] * self.growFactor
