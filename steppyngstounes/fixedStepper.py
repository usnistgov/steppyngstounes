from __future__ import division
from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["FixedStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class FixedStepper(Stepper):
    r"""Stepper that takes steps of fixed size.

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

    """

    __doc__ += Stepper._stepper_test.format(stepperclass="FixedStepper", maxerror="None")

    def _step(self, tryStep):
        """Solve at given step.

        This method never "fails" and the step is never changed.

        Parameters
        ----------
        tryStep : float
            Step to attempt.

        Returns
        -------
        triedStep : float
            The step actually taken.
        nextStep : float
            The next step to try.

        """
        # step always "succeeds"
        error = self.solve(tryStep=tryStep)

        nextStep = self.success(triedStep=tryStep, error=error)

        return tryStep, nextStep
