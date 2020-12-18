from __future__ import division
from __future__ import unicode_literals

import numpy as np
from scipy.interpolate import interp1d

from steppyngstounes.stepper import Stepper

__all__ = ["ParsimoniousStepper"]

class ParsimoniousStepper(Stepper):
    r"""Non-monotonic stepper that attempts to find something "interesting".

    Compute the function where the curvature is highest and where not many
    points have been computed.
    
    Based on an email::

        From: David Huard <david.huard@gmail.com>
        Date: April 1, 2009 4:23:14 PM EDT
        To: "Guyer, Jonathan E. Dr." <jonathan.guyer@nist.gov>
        Subject: Re: [SciPy-user] "smooth" plots

        Jonathan,

        Here are bits of code I've extracted from a project of mine.
        You'll have to do some imports from numpy to get it to work.  It's
        not pretty, but it was enough for my use case.  I'd be interested
        to look at papers that discuss this problem if you have references
        nearby.  Note that I also have a version that calls func on
        multiple processes (using ipython).  With 2 quad cores, this sped
        up considerably my application.

        HTH,

        David

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
        super(ParsimoniousStepper, self).__init__(start=start, stop=stop,
                                                  minStep=minStep, inclusive=inclusive,
                                                  record=True)
        self.numsteps = N
        assert scale in ["dl", "dy"]
        self.scale = scale
        self.candidates = list(np.linspace(self.start, self.stop,
                                           min(max([minsteps, N//3]),
                                               maxinitial)))
        self.candidates.pop(0)

    def _sortxy(self):
        """Sort x and y so that x is in accending order.
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
        x, y = self._sortxy()

        dx = np.diff(x)
        dy = np.diff(y)
        dn2 = np.diff(y,2)
        dn2 = np.concatenate([[dn2[0]/2,], dn2, [dn2[-1]/2]])
        der2 = interp1d(x,dn2)
        dl = np.sqrt(dx**2 + dy**2)
        centerx = x[:-1]+dx/2
        d2 = der2(centerx)
        if self.scale == 'dl':
            cons = dl*np.sqrt(abs(d2))
        elif self.scale == 'dy':
            cons = abs(dy)*abs(d2)
        i = np.argmax(cons)

        #newx = x[max(0,i-1):i+1]+dx[max(0,i-1):i+1]/2.
        newx = centerx[i].tolist()
#         if len(newx) == 0:
#             raise 'No candidate found.'

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

    def _succeeded(self, error):
        """Determine if most recent attempt failed.

        .. note:: Parsimonious steps always succeed.

        Returns
        -------
        True
            Parsimonious steps always succeed.
        error : float
            Error to record. If `error` was None, returns 0.
        """
        if error is None:
            error = 0.
        return True, error

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
