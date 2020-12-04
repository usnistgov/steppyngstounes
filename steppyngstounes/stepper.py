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
    solvefor : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.

    Attributes
    ----------
    elapsed : float
        The total time taken so far.
    time_steps : list of float
        The time steps successfully taken so far.
    elapsed_times : list of float
        The elapsed time at each successful time step.
    """

    def __init__(self, solvefor=()):
        self.solvefor = solvefor
        self.elapsed = 0.
        self.time_steps = []
        self.elapsed_times = []

    def calcError(self, var, equation, boundaryConditions, residual):
        """Calculate error of current solution.

        Parameters
        ----------
        var : ~fipy.variables.cellVariable.CellVariable
            Solution variable.
        equation : ~fipy.terms.term.Term
            Equation that solved `var`.
        boundaryConditions : tuple
            Boundary conditions applied to solution of `var`.
        residual : float
            Residual from solution of `var`.
        """
        raise NotImplementedError

    def solve(self, dt):
        """Action to take at each adapted time step attempt.

        Parameters
        ----------
        dt : float
            Adapted time step to attempt.

        Returns
        -------
        Solution error, normalized to 1.
        """
        error = 0.
        for var, eqn, bcs in self.solvefor:
            res = eqn.sweep(var=var,
                            dt=dt,
                            boundaryConditions=bcs)

            error = max(error,
                        self.calcError(var=var,
                                       equation=eqn,
                                       boundaryConditions=bcs,
                                       residual=res))

        return error

    def success(self, dt, dtPrev):
        """Function to perform after a successful adaptive solution step.

        Parameters
        ----------
        dt : float
            The time step that was requested.
        dtPrev : float
            The time step that was actually taken.

        """
        pass

    def failure(self, dt, dtPrev):
        """Function to perform when `solve()` returns an error greater than 1.

        Parameters
        ----------
        dt : float
            The time step that was requested.
        dtPrev : float
            The time step that was attempted.

        """
        pass

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

    def _shrinkStep(self, error, dt):
        """Reduce time step after failure

        Parameters
        ----------
        error : float
            Error (normalized to 1) from the last solve.
        dt : float
            Time step that failed.

        Returns
        -------
        float
            New time step
        """
        return dt

    def _calcPrev(self, error, dt, dtPrev):
        """Adjust previous time step

        Parameters
        ----------
        error : float
            Error (normalized to 1) from the last solve.
        dt : float
            Time step that failed.
        dtPrev : float
            Previous time step.

        Returns
        -------
        float
            New previous time step
        """
        return dtPrev

    def _calcNext(self, error, dt, dtPrev):
        """Calculate next time step after success

        Parameters
        ----------
        error : float
            Error (normalized to 1) from the last solve.
        dt : float
            Time step that succeeded.
        dtPrev : float
            Previous time step.

        Returns
        -------
        float
            New time step
        """
        return dt

    def _step(self, dt, dtPrev):
        """Solve at given time step and then adapt.

        Parameters
        ----------
        dt : float
            Adapted time step to attempt.
        dtPrev : float
            The last time step attempted.

        Returns
        -------
        dt : float
            The time step attempted.
        dtNext : float
            The next time step to try.
        """
        while True:
            error = self.solve(dt=dt)

            if error > 1. and dt > self.dtMin:
                # reject the timestep
                self.failure(dt=dt)

                for var, eqn, bcs in self.solvefor:
                    var.value = var.old

                dt = self._shrinkStep(error=error, dt=dt)
                dt = self._lowerBound(dt)
                dtPrev = self._calcPrev(error=error, dt=dt, dtPrev=dtPrev)
            else:
                # step succeeded
                break

        dtNext = self._calcNext(error=error, dt=dt, dtPrev=dtPrev)

        return dt, dtNext

    def step(self, dt, dtTry=None, dtMin=None, dtPrev=None):
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

        Returns
        -------
        dtPrev : float
            The adapted time step actually taken.
        dtTry : float
            The next adapted time step to attempt.
        """
        dtTry = dtTry or dtMin or dt
        dtPrev = dtPrev or dtMin
        self.dtMin = dtMin or 0.

        this_step = 0.

        while this_step < dt:
            dtMax = dt - this_step
            if dtTry > dtMax:
                dtSave = dtTry
                dtTry = dtMax
            else:
                dtSave = None

            for var, eqn, bcs in self.solvefor:
                var.updateOld()

            dtPrev, dtTry = self._step(dt=dtTry, dtPrev=dtPrev)

            this_step += dtPrev
            self.elapsed += dtPrev

            self.time_steps.append(dtPrev)
            self.elapsed_times.append(self.elapsed)

            self.success(dt=dt, dtPrev=dtPrev)

            dtTry = max(dtTry, self.dtMin)

        return dtSave or dtPrev, dtSave or dtTry
