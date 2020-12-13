from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["PseudoRKQSStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PseudoRKQSStepper(Stepper):
    r"""Pseudo-Runge-Kutta adaptive stepper.

    Based on the ``rkqs`` (Runge-Kutta "quality-controlled" stepper)
    algorithm of Numerical Recipes in C: 2nd Edition, Section 16.2.

    Not really appropriate, since we're not doing the `rkck` Runge-Kutta
    steps in the first place, but works OK.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = \mathrm{min}\left[S \left(e_n\right)^{P_\text{grow}}, f_\text{max} \right] \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`e_n` is the error at step :math:`n`.  :math:`S` is the safety
    factor, :math:`P_\text{grow}` is the growth exponent, and
    :math:`f_\text{max}` is the maximum factor to grow the step size.

    On failure, retries with

    .. math::

       \Delta_{n} = \mathrm{max}\left[S \left(e_n\right)^{P_\text{shrink}}, f_\text{min} \right] \Delta_n

    where :math:`P_\text{shrink}` is the shrinkage exponent and :math:`f_\text{min}`
    is the minimum factor to shrink the stepsize.

    .. note::

        The user must override
        :meth:`~fipy.steppers.stepper.Stepper.calcError` and may override
        :meth:`~fipy.steppers.stepper.Stepper.solve`,
        :meth:`~fipy.steppers.stepper.Stepper.success`, and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

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
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).
    safety : float
        RKQS control safety factor :math:`S` (default 0.9).
    pgrow : float
        RKQS control growth exponent :math:`P_\text{grow}` (default -0.2).
    pshrink : float
        RKQS control shrinkage exponent :math:`P_\text{shrink}` (default -0.25).
    maxgrow : float
        RKQS control maximum factor to grow step size :math:`f_\text{max}` (default 5).
    minshrink : float
        RKQS control minimum factor to shrink step size :math:`f_\text{min}` (default 0.1).

    """

    __doc__ += Stepper._stepper_test.format(StepperClass="PseudoRKQSStepper",
                                            dt=50.,
                                            steps=369,
                                            attempts=392)

    def __init__(self, start, stop, tryStep=None, inclusive=False, minStep=None,
                 safety=0.9, pgrow=-0.2, pshrink=-0.25,
                 maxgrow=5, minshrink=0.1):
        super(PseudoRKQSStepper, self).__init__(start=start, stop=stop, tryStep=tryStep,
                                                inclusive=inclusive, minStep=minStep)
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
        factor = max(self.safety * self._errors[-1]**self.pshrink, self.minshrink)
        return factor * self._sizes[-1]

    def _calcNext(self):
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

def _test():
    import fipy.tests.doctestPlus
    return fipy.tests.doctestPlus.testmod()

if __name__ == "__main__":
    _test()
