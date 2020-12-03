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

    def _step(self, dt, dtPrev, *args, **kwargs):
        """Sweep at given time step and then adapt.

        Parameters
        ----------
        dt : float
            Adapted time step to attempt.
        dtPrev : float
            The last time step attempted.
        *args, **kwargs
            Extra arguments to pass on to `sweepFn()` and `failFn()`.

        Returns
        -------
        dt : float
            The time step attempted.
        dtNext : float
            The next time step to try.
        """
        while True:
            error = self.sweepFn(dt=dt, *args, **kwargs)

            if error > 1.:
                # step failed
                self.failFn(dt=dt, *args, **kwargs)

                # revert
                for var, eqn, bcs in self.solvefor:
                    var.setValue(var.old)

                    dt = max(self.safety * dt * error**self.pgrow, 0.1 * dt)

                dt = self._lowerBound(dt)
            else:
                # step succeeded
                break

        if error > self.errcon:
            dtNext = dt * self.safety * error**self.pshrink
        else:
            dtNext = 5 * dt

        return dt, dtNext
