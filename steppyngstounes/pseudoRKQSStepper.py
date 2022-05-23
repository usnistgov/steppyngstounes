from __future__ import division
from __future__ import unicode_literals

from steppyngstounes.stepper import Stepper

__all__ = ["PseudoRKQSStepper"]


class PseudoRKQSStepper(Stepper):
    r"""Pseudo-Runge-Kutta adaptive stepper.

    Based on the ``rkqs`` (Runge-Kutta "quality-controlled" stepper)
    algorithm of Numerical Recipes in C: 2nd Edition, Section 16.2.

    Not really appropriate, since we're not doing the `rkck` Runge-Kutta
    steps in the first place, but works OK.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = \mathrm{min}\left[S \left(e_n\right)^{P_\text{grow}},
                                        f_\text{max} \right] \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`e_n` is the error at step :math:`n`.  :math:`S` is the safety
    factor, :math:`P_\text{grow}` is the growth exponent, and
    :math:`f_\text{max}` is the maximum factor to grow the step size.

    On failure, retries with

    .. math::

       \Delta_{n} = \mathrm{max}\left[S \left(e_n\right)^{P_\text{shrink}},
                                      f_\text{min} \right] \Delta_n

    where :math:`P_\text{shrink}` is the shrinkage exponent and
    :math:`f_\text{min}` is the minimum factor to shrink the stepsize.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    size : float
        Suggested step size to try (default None).
    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).
    limiting : bool
        Whether to prevent error from exceeding 1 (default True).
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).

        .. |machineepsilon| replace::   `eps`
        .. _machineepsilon:
           https://numpy.org/doc/stable/reference/generated/numpy.finfo.html

    safety : float
        RKQS control safety factor :math:`S` (default 0.9).
    pgrow : float
        RKQS control growth exponent :math:`P_\text{grow}` (default -0.2).
    pshrink : float
        RKQS control shrinkage exponent :math:`P_\text{shrink}` (default
        -0.25).
    maxgrow : float
        RKQS control maximum factor to grow step size :math:`f_\text{max}`
        (default 5).
    minshrink : float
        RKQS control minimum factor to shrink step size
        :math:`f_\text{min}` (default 0.1).

    """

    __doc__ += Stepper._stepper_test(StepperClass="PseudoRKQSStepper",
                                     steps=346,
                                     attempts=361)

    def __init__(self, start, stop, size=None, minStep=None,
                 inclusive=False, record=False, limiting=True,
                 safety=0.9, pgrow=-0.2, pshrink=-0.25,
                 maxgrow=5, minshrink=0.1):
        super(PseudoRKQSStepper, self).__init__(start=start,
                                                stop=stop,
                                                size=size,
                                                minStep=minStep,
                                                inclusive=inclusive,
                                                record=record,
                                                limiting=limiting)
        self.safety = safety
        self.pgrow = pgrow
        self.pshrink = pshrink
        self.maxgrow = maxgrow
        self.minshrink = minshrink
        self.errcon = (maxgrow/safety)**(1./pgrow)

    def _shrinkStep(self):
        """Reduce step after failure

        Returns
        -------
        float
            New step.

        """
        factor = max(self.safety * self._errors[-1]**self.pshrink,
                     self.minshrink)
        return factor * self._sizes[-1]

    def _adaptStep(self):
        """Calculate next step after success

        Returns
        -------
        float
            New step.

        """
        if self._errors[-1] > self.errcon:
            factor = self.safety * self._errors[-1]**self.pgrow
        else:
            factor = self.maxgrow

        return factor * self._sizes[-1]
