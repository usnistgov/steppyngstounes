from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["PseudoRKQSStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PseudoRKQSStepper(Stepper):
    """Pseudo-Runge-Kutta adaptive stepper.

    Based on the ``rkqs`` (Runge-Kutta "quality-controlled" stepper)
    algorithm of Numerical Recipes in C: 2nd Edition, Section 16.2.

    Not really appropriate, since we're not doing Runge-Kutta steps
    in the first place, but works OK.

    .. note::

        The user must override
        :meth:`~fipy.steppers.stepper.Stepper.calcError` and may override
        :meth:`~fipy.steppers.stepper.Stepper.success` and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.
    safety, pgrow, pshrink, errcon : float
        RKQS control constants.

    """

    def __init__(self, solvefor=(), safety=0.9, pgrow=-0.2, pshrink=-0.25, errcon=1.89e-4):
        Stepper.__init__(self, solvefor=solvefor)
        self.safety = safety
        self.pgrow = pgrow
        self.pshrink = pshrink
        self.errcon = errcon

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
        factor = max(self.safety * error**self.pgrow, 0.1)
        return factor * triedStep

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
        if error > self.errcon:
            factor = self.safety * error**self.pshrink
        else:
            factor = 5

        return factor * triedStep
