from __future__ import division
from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["FixedStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class FixedStepper(Stepper):
    r"""Stepper that takes steps of fixed size.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    tryStep : float
        Desired step size.
    inclusive : bool
        Whether to include an evaluation at `start` (default False)

    """

    __doc__ += Stepper._stepper_test.format(StepperClass="FixedStepper",
                                            dt=0.15,
                                            steps=6668,
                                            attempts=6668)

    def _succeeded(self, error):
        """Determine if most recent attempt failed.

        .. note:: Fixed steps always succeed.

        Returns
        -------
        bool
        """
        return True

def _test():
    import fipy.tests.doctestPlus
    return fipy.tests.doctestPlus.testmod()

if __name__ == "__main__":
    _test()
