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

    __doc__ += Stepper._stepper_test.format(stepperclass="FixedStepper",
                                            dt=0.15,
                                            steps=8089,
                                            attempts=8089)

    def _failed(self, triedStep, error, attempts):
        """Determine if most recent attempt failed.

        .. note:: Fixed steps always succeed.

        Returns
        -------
        bool
        """
        return False

def _test():
    import fipy.tests.doctestPlus
    return fipy.tests.doctestPlus.testmod()

if __name__ == "__main__":
    _test()
