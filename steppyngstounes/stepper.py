from __future__ import unicode_literals
from builtins import object
__docformat__ = 'restructuredtext'

__all__ = ["Stepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class Stepper(object):
    """Adaptive stepper base class.

    Parameters
    ----------
    vardata : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.
    """

    def __init__(self, vardata=()):
        self.vardata = vardata

    def sweepFn(vardata, dt, *args, **kwargs):
        """Function to apply at each adapted time step.

        Parameters
        ----------
        vardata : tuple of tuple
            Each tuple holds a `CellVariable` to solve for, the equation to
            solve, and the old-style boundary conditions to apply.
        dt : float
            Adapted time step to attempt.
        *args, **kwargs
            Extra arguments passed to `self.step()`.  The same `*args` and
            `**kwargs` are passed to `successFn()` and `failFn()`.

        Returns
        -------
        Solution error, normalized to 1.
        """
        residual = 0
        for var, eqn, bcs in vardata:
            residual = max(residual, eqn.sweep(var=var, dt=dt, boundaryConditions=bcs))

        return residual
    sweepFn = staticmethod(sweepFn)

    def successFn(vardata, dt, dtPrev, elapsed, *args, **kwargs):
        """Function to perform after a successful adaptive solution step.

        Parameters
        ----------
        vardata : tuple of tuple
            Each tuple holds a `CellVariable` to solve for, the equation to
            solve, and the old-style boundary conditions to apply.
        dt : float
            The time step that was requested.
        dtPrev : float
            The time step that was actually taken.
        elapsed : float
            How much time is elapsed *for this time step*.
        *args, **kwargs
            Extra arguments passed to `self.step()`.  The same `*args` and
            `**kwargs` are passed to `sweepFn()` and `failFn()`.

        """
        pass
    successFn = staticmethod(successFn)

    def failFn(vardata, dt, *args, **kwargs):
        """Function to perform when `sweepFn()` returns an error greater than 1.

        Parameters
        ----------
        vardata : tuple of tuple
            Each tuple holds a `CellVariable` to solve for, the equation to
            solve, and the old-style boundary conditions to apply.
        dt : float
            The time step that was requested.
        *args, **kwargs
            Extra arguments passed to `self.step()`.  The same `*args` and
            `**kwargs` are passed to `sweepFn()` and `successFn()`.

        """
        pass
    failFn = staticmethod(failFn)

    def _lowerBound(self, dt):
        """Determine minimum time step.

        Parameters
        ----------
        dt : float
            Desired time step.

        Returns
        -------
        float
            Maximum of `dt` and `self.dtMin`.

        Raises
        ------
        FloatingPointError
            If the resulting time step would underflow.

        """
        dt = max(dt, self.dtMin)
        if self.elapsed + dt == self.elapsed:
            raise FloatingPointError("step size underflow: %g + %g == %g" % (self.elapsed, dt, self.elapsed))

        return dt

    def _step(self, dt, dtPrev, sweepFn, failFn, *args, **kwargs):
        """Sweep at given time step and then adapt.

        Parameters
        ----------
        dt : float
            Adapted time step to attempt.
        dtPrev : float
            The last time step attempted.
        sweepFn : callable
            Function to apply at each adapted time step.
        failFn : callable
            Function to perform when `sweepFn()` returns an error greater than 1.
        *args, **kwargs
            Extra arguments to pass on to `sweepFn()` and `failFn()`.

        Returns
        -------
        dt : float
            The time step attempted.
        dtNext : float
            The next time step to try.
        """
        sweepFn(vardata=self.vardata, dt=dt, *args, **kwargs)
        return dt, dt

    def step(self, dt, dtTry=None, dtMin=None, dtPrev=None,
             sweepFn=None, successFn=None, failFn=None, *args, **kwargs):
        """Perform an adaptive solution step.

        Parameters
        ----------
        dt : float
            The desired time step.
        dtTry : float
            The time step to try first.
        dtMin : float
            The smallest time step to allow.
        dtPrev : float
            The last time step attempted.
        sweepFn : callable
            Function to override `self.sweepFn` (default None).
        successFn : callable
            Function to override `self.successFn` (default None).
        failFn : callable
            Function to override `self.failFn` (default None).
        *args, **kwargs
            Extra arguments to pass on to `sweepFn()`, `successFn()`, and
            `failFn()`.

        Returns
        -------
        dtPrev : float
            The adapted time step actually taken.
        dtTry : float
            The next adapted time step to attempt.
        """
        sweepFn = sweepFn or self.sweepFn
        successFn = successFn or self.successFn
        failFn = failFn or self.failFn

        dtTry = dtTry or dtMin or dt
        dtPrev = dtPrev or dtMin
        self.dtMin = dtMin or 0.

        self.elapsed = 0.

        while self.elapsed < dt:
            dtMax = dt - self.elapsed
            if dtTry > dtMax:
                dtSave = dtTry
                dtTry = dtMax
            else:
                dtSave = None

            for var, eqn, bcs in self.vardata:
                var.updateOld()

            dtPrev, dtTry = self._step(dt=dtTry, dtPrev=dtPrev,
                                       sweepFn=sweepFn, failFn=failFn,
                                       *args, **kwargs)

            self.elapsed += dtPrev

            successFn(vardata=self.vardata,
                      dtPrev=dtPrev, elapsed=self.elapsed, dt=dt, *args, **kwargs)

            dtTry = max(dtTry, self.dtMin)

        return dtSave or dtPrev, dtSave or dtTry
