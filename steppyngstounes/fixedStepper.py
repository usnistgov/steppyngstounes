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
    recorded : bool
        Whether to keep history of steps, errors, values, etc. (default False).

    """

    __doc__ += Stepper._stepper_test.format(StepperClass="FixedStepper",
                                            dt=0.15,
                                            steps=6668,
                                            attempts=6668)

    def __init__(self, start, stop, tryStep,
                 inclusive=False, recorded=False):
        super(FixedStepper, self).__init__(start=start, stop=stop, tryStep=tryStep,
                                           minStep=minStep, inclusive=inclusive,
                                           recorded=recorded)

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
