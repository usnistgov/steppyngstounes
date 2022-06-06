from __future__ import division
from __future__ import unicode_literals

import numpy as np

from steppyngstounes.stepper import Stepper

__all__ = ["ParsimoniousStepper"]


class ParsimoniousStepper(Stepper):
    r"""Non-monotonic stepper that samples sparsely explored regions

    Computes the function where the curvature is highest and where not many
    points have been computed.

    .. note::

       By its nature, this :class:`~steppyngstounes.stepper.Stepper` must
       `record`.

    Parameters
    ----------
    start : float
        Beginning of range to step over.
    stop : float
        Finish of range to step over.
    N : int
        Number of points to sample.
    minStep : float
        Smallest step to allow (default `(stop - start) *`
        |machineepsilon|_).

        .. |machineepsilon| replace::   `eps`
        .. _machineepsilon:
           https://numpy.org/doc/stable/reference/generated/numpy.finfo.html

    inclusive : bool
        Whether to include an evaluation at `start` (default False)
    scale : str
        Parameter to indicate whether to scale by value "dy" or arc length
        "dl" (default "dl").
    minsteps : int
        Minimum number of steps to take (default 4).
    maxinitial : int
        The maximum number of even steps to take before adapting (default
        11).

    """

    __doc__ += Stepper._stepper_test(StepperClass="ParsimoniousStepper",
                                     stepper_args="N=50",
                                     control_error=False,
                                     steps=50,
                                     attempts=50)

    def __init__(self, start, stop, N, minStep=0., inclusive=False,
                 scale="dl", minsteps=4, maxinitial=11):
        super(ParsimoniousStepper, self).__init__(start=start,
                                                  stop=stop,
                                                  minStep=minStep,
                                                  inclusive=inclusive,
                                                  record=True,
                                                  limiting=False)
        self.numsteps = N
        assert scale in ["dl", "dy"]
        self.scale = scale
        self.candidates = list(np.linspace(self.start, self.stop,
                                           min(max([minsteps, N//3]),
                                               maxinitial)))
        self.candidates.pop(0)

    def _sortxy(self):
        """Sort x and y so that x is in ascending order.
        """
        sx = np.squeeze(np.asarray(self.steps))
        sy = np.squeeze(np.asarray(self.values))
        si = sx.argsort()
        sx = sx[si]
        sy = sy[si]
        return np.squeeze(sx), np.squeeze(sy)

    def _find_candidate(self):
        """Given points (x,y) on a continuous curve, select a new x_i
        where the computation of y_i will yield valuable new information
        about the curve.

        Regions of high curvature are sampled preferably, as well as
        regions scarcely sampled by x.

        """
        from scipy.interpolate import interp1d

        x, y = self._sortxy()

        dx = np.diff(x)
        dy = np.diff(y)
        dn2 = np.diff(y, 2)
        dn2 = np.concatenate([[dn2[0]/2], dn2, [dn2[-1]/2]])
        der2 = interp1d(x, dn2)
        dl = np.sqrt(dx**2 + dy**2)
        centerx = x[:-1]+dx/2
        d2 = der2(centerx)
        if self.scale == 'dl':
            cons = dl*np.sqrt(abs(d2))
        elif self.scale == 'dy':
            cons = abs(dy)*abs(d2)
        i = np.argmax(cons)

        newx = centerx[i].tolist()

        return newx

    def _upperBound(self, step):
        """Determine maximum step.

        Parameters
        ----------
        step : float
            Desired step.

        Returns
        -------
        float
            `step` is returned unchanged.

        """
        return step

    def _done(self):
        """Determine if all requested steps have been taken.

        Returns
        -------
        bool

        """
        return len(self.steps) >= self.numsteps

    def _adaptStep(self):
        """Calculate next step after success

        Returns
        -------
        float
            New step.

        """
        if not self.candidates:
            self.candidates.append(self._find_candidate())

        return self.candidates.pop(0) - self.current
