from __future__ import unicode_literals
from builtins import object

from fipy.tools import numerix

__docformat__ = 'restructuredtext'

__all__ = ["Stepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class Stepper(object):
    """Adaptive stepper base class.

    .. note::

        The user must override
        :meth:`~fipy.steppers.stepper.Stepper.calcError` and may override
        :meth:`~fipy.steppers.stepper.Stepper.success` and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a
        :class:`~fipy.variables.cellVariable.CellVariable` to solve for,
        the equation to solve, and the old-style boundary conditions to
        apply (if any).

    Attributes
    ----------
    current : float
        The present value of the control variable.
    steps : list of float
        The steps successfully taken so far.
    values : list of float
        The value of the control variable at each successful step.

    """

    def __init__(self, solvefor=()):
        self.solvefor = solvefor
        self.current = 0.
        self.steps = []
        self.values = []

    def calcError(self, var, equation, boundaryConditions, residual):
        """Calculate error of current solution.

        Users must subclass the desired class of
        :class:`~fipy.steppers.stepper.Stepper` and override this method to
        calculate a value normalized to 1.

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

        Returns
        -------
        float
            Solution error, positive and normalized to 1.  Returning a
            value greater than 1 will cause the next step to shrink,
            otherwise it will grow.

        """
        raise NotImplementedError

    def solve(self, tryStep):
        """Action to take at each adapted step attempt.

        Parameters
        ----------
        tryStep : float
            Adapted step to attempt.

        Returns
        -------
        float
            Solution error, positive and normalized to 1.

        """
        error = 0.
        for var, eqn, bcs in self.solvefor:
            res = eqn.sweep(var=var,
                            dt=tryStep,
                            boundaryConditions=bcs)

            error = max(error,
                        self.calcError(var=var,
                                       equation=eqn,
                                       boundaryConditions=bcs,
                                       residual=res))

        return error

    def success(self, triedStep):
        """Action to perform after a successful adaptive solution step.

        Default does nothing.  Users can override this method to perform
        any desired actions.

        Parameters
        ----------
        triedStep : float
            The step that was actually taken.

        """
        pass

    def failure(self, triedStep):
        """Action to perform when `solve()` returns an error greater than 1.

        Default does nothing.  Users can override this method to perform
        any desired actions.

        Parameters
        ----------
        triedStep : float
            The step that was attempted.

        """
        pass

    def _lowerBound(self, tryStep):
        """Determine minimum step.

        Parameters
        ----------
        tryStep : float
            Desired step.

        Returns
        -------
        float
            Maximum magnitude of `tryStep` and `self.minStep`.

        Raises
        ------
        FloatingPointError
            If the resulting step would underflow.

        """
        tryStep = numerix.sign(tryStep) * max(abs(tryStep), abs(self.minStep))
        if self.current + tryStep == self.current:
            raise FloatingPointError("step size underflow: %g + %g == %g" % (self.current, tryStep, self.current))

        return tryStep

    def _shrinkStep(self, triedStep, error):
        """Reduce step after failure

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that failed.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New step.

        """
        return triedStep

    def _calcPrev(self, triedStep, prevStep, error):
        """Adjust previous step

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        not need to override this method (default returns `prevStep`
        unchanged).

        Parameters
        ----------
        triedStep : float
            Step that failed.
        prevStep : float
            Previous step.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New previous step.

        """
        return prevStep

    def _calcNext(self, triedStep, prevStep, error):
        """Calculate next step after success

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that succeeded.
        prevStep : float
            Previous step.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New step.

        """
        return triedStep

    def _step(self, tryStep, prevStep):
        """Solve at given step and then adapt.

        Parameters
        ----------
        tryStep : float
            Adapted step to attempt.
        prevStep : float
            The last step attempted.

        Returns
        -------
        tryStep : float
            The step attempted.
        nextStep : float
            The next step to try.

        """
        while True:
            error = self.solve(tryStep=tryStep)

            if error > 1. and abs(tryStep) > abs(self.minStep):
                # reject the step
                self.failure(triedStep=tryStep)

                for var, eqn, bcs in self.solvefor:
                    var.value = var.old

                tryStep = self._shrinkStep(triedStep=tryStep, error=error)
                tryStep = self._lowerBound(tryStep=tryStep)
                prevStep = self._calcPrev(error=error, tryStep=tryStep, prevStep=prevStep)
            else:
                # step succeeded
                break

        nextStep = self._calcNext(triedStep=tryStep, prevStep=prevStep, error=error)
        nextStep = self._lowerBound(tryStep=nextStep)

        return tryStep, nextStep

    def step(self, until, tryStep=None, minStep=None, prevStep=None):
        """Perform an adaptive solution step.

        Parameters
        ----------
        until : float
            The value of the control variable to step to.
        tryStep : float
            The step to try first.
        minStep : float
            The smallest step to allow.
        prevStep : float
            The last step attempted.

        Returns
        -------
        prevStep : float
            The adapted step actually taken.
        tryStep : float
            The next adapted step to attempt.

        """
        tryStep = tryStep or minStep or (until - self.current)
        prevStep = prevStep or minStep
        self.minStep = minStep or 0.

        saveStep = None
        while True:
            maxStep = until - self.current
            if maxStep == 0:
                # reached until
                break

            if abs(tryStep) > abs(maxStep):
                saveStep = tryStep
                tryStep = maxStep
            else:
                saveStep = None

            for var, eqn, bcs in self.solvefor:
                var.updateOld()

            prevStep, tryStep = self._step(tryStep=tryStep, prevStep=prevStep)

            self.current += prevStep

            self.steps.append(prevStep)
            self.values.append(self.current)

            self.success(triedStep=prevStep)

        return saveStep or prevStep, saveStep or tryStep
