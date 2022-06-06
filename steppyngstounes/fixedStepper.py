from __future__ import division
from __future__ import unicode_literals

from steppyngstounes.stepper import Stepper

__all__ = ["FixedStepper"]


class FixedStepper(Stepper):
    r"""Stepper that takes steps of constant size.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    size : float
        Desired step size.
    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).

    """

    __doc__ += Stepper._stepper_test(StepperClass="FixedStepper",
                                     stepper_args="size=3., record=True",
                                     control_error=False,
                                     steps=335,
                                     attempts=335)
