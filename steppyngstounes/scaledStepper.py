from __future__ import division
from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["ScaledStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class ScaledStepper(Stepper):
    r"""Adaptive stepper adjust the step by fixed factors.

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
    
    .. note::

        The user must override
        :meth:`~fipy.steppers.stepper.Stepper.calcError` and may override
        :meth:`~fipy.steppers.stepper.Stepper.solve`,
        :meth:`~fipy.steppers.stepper.Stepper.success`, and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.
    minStep : float
        Smallest step to allow (default 0).
    growFactor : float
        Growth factor :math:`f_\text{grow}` (default 1.2).
    shrinkFactor : float
        Shrinkage factor :math:`f_\text{shrink}` (default 0.5).

    """

    __doc__ += Stepper._stepper_test.format(StepperClass="ScaledStepper",
                                            dt=50.,
                                            steps=383,
                                            attempts=478)

    def __init__(self, solvefor=(), minStep=0.,
                 growFactor=1.2, shrinkFactor=0.5):
        super(ScaledStepper, self).__init__(solvefor=solvefor, minStep=minStep)
        self.growFactor = growFactor
        self.shrinkFactor = shrinkFactor

    def _shrinkStep(self, triedStep, error):
        """Reduce step after failure

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
        return triedStep * self.shrinkFactor

    def _calcNext(self, triedStep, error):
        """Calculate next step after success

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
        return triedStep * self.growFactor

def _test():
    import fipy.tests.doctestPlus
    return fipy.tests.doctestPlus.testmod()

if __name__ == "__main__":
    _test()
        