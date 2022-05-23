from __future__ import division
from __future__ import unicode_literals

import itertools
import numpy as np

from steppyngstounes.stepper import Stepper

__all__ = ["CheckpointStepper"]


class CheckpointStepper(Stepper):
    r"""Stepper that stops at fixed points.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stops : iterable of float
        Desired checkpoints.
    stop : float, optional
        Finish of range to step over (default `np.inf`).  In the event that
        any of `stops` exceed `stop`, the stepper will terminate at `stop`.
        A step will not be taken to `stop` otherwise (clear?).
    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    record : bool
        Whether to keep history of steps, errors, values, etc. (default False).

    """

    __doc__ += Stepper._stepper_test(StepperClass="CheckpointStepper",
                                     stepper_args="stops=10.**np.arange(-5, 5)"
                                                  ", record=True",
                                     control_error=False,
                                     steps=10,
                                     attempts=10)

    def __init__(self, start, stops, stop=np.inf,
                 inclusive=False, record=False):
        self._wantstops = iter(stops)

        # peek at first value
        peek = next(self._wantstops) - start
        if inclusive:
            pushback = [start, start + peek]
        else:
            pushback = [start + peek]
        self._wantstops = itertools.chain(pushback, self._wantstops)

        super(CheckpointStepper, self).__init__(start=start,
                                                stop=stop,
                                                size=peek,
                                                inclusive=inclusive,
                                                record=record,
                                                limiting=False)

    def _adaptStep(self):
        """Calculate next step after success

        Returns next step size in sequence.

        Returns
        -------
        float
            New step.

        """
        return next(self._wantstops) - self.current
