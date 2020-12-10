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
        :meth:`~fipy.steppers.stepper.Stepper.solve`,
        :meth:`~fipy.steppers.stepper.Stepper.success`, and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a
        :class:`~fipy.variables.cellVariable.CellVariable` to solve for,
        the equation to solve, and the old-style boundary conditions to
        apply (if any).
    minStep : float
        Smallest step to allow (default 0).

    Attributes
    ----------
    current : float
        The present value of the control variable.
    steps : list of float
        The steps successfully taken so far.
    values : list of float
        The value of the control variable at each successful step.
    error : list of float
        The error at each successful step.

    """

    _stepper_test = r"""

    Examples
    --------

    .. plot::
       :context: reset
       :include-source:
       :nofigs:

       >>> import fipy as fp
       >>> from fipy.tools import numerix

       Declare a trivial 1D mesh

       >>> mesh = fp.Grid1D(nx=1, dx=1.)

       Instantiate a solution variable :math:`$\phi$` on that mesh.

       >>> phi = fp.CellVariable(mesh=mesh, name=r"$\phi$", value=0., hasOld=True)

       Determine a desired time step and total runtime, as well as the
       intervals to capture results.

       >>> dt = {dt}
       >>> totaltime = 1000.
       >>> checkpoints = (fp.numerix.arange(int(totaltime / dt)) + 1) * dt

       Rather than solve any actual PDEs, we'll demonstrate using an
       artificial function that changes abruptly, but smoothly, with time.

       >>> def dummyfunc(t, width):
       ...     return numerix.tanh((t / totaltime - 0.5) / (2 * width))

       Create a stepper subclass that customizes how to update :math:`\phi`
       (using `dummyfunc`), how to determine the scaled "error" (here we
       calculate :math:`\|\phi - \phi^\mathrm{{old}}\|_1 /
       \mathtt{{errorscale}}`), and records the values of :math:`\phi` at
       successful steps.

       >>> errorscale = 1e-2

       >>> from fipy.steppers import {stepperclass}

       >>> class My{stepperclass}({stepperclass}):
       ...     def __init__(self, solvefor, *args, **kwargs):
       ...         super(My{stepperclass}, self).__init__(solvefor, *args, **kwargs)
       ...         self.var = solvefor[0][0]
       ...         # `signal` must have same length as `steps` and `values`
       ...         self.signal = [self.var.cellVolumeAverage.value] * len(self.steps)
       ...
       ...     def solve1(self, tryStep, var, eqn, bcs):
       ...         var.value = dummyfunc(t=self.current + tryStep, width=0.01)
       ...         return 0.
       ...
       ...     def calcError(self, var, equation, boundaryConditions, residual):
       ...         return numerix.L1norm(var - var.old) / errorscale
       ...
       ...     def success(self, *args, **kwargs):
       ...         self.signal.append(self.var.cellVolumeAverage.value)
       ...         return super(My{stepperclass}, self).success(*args, **kwargs)

       Finally, instantiate a stepper with the variable to solve for and the
       smallest step to allow.

       >>> stepper = My{stepperclass}(solvefor=((phi, None, ()),), minStep=dt / 1e6)

       Call :meth:`~fipy.steppers.stepper.Stepper.step` for each desired
       time step.  Pass the time to step to `until` and the time step to try
       first `tryStep`.

       >>> tryStep = dt
       >>> for until in checkpoints:
       ...     prevStep, tryStep = stepper.step(until=until, tryStep=tryStep)

       >>> print(len(stepper.steps))
       12345

    .. plot::
       :context:
       :include-source:

       >>> plt.rcParams['lines.linestyle'] = ""
       >>> plt.rcParams['lines.marker'] = "."
       >>> fix, axes = plt.subplots(2, 2, sharex=True)

       >>> axes[0, 0].plot(stepper.values, stepper.signal)
       >>> axes[0, 0].set_ylabel(r"$\phi$")

       >>> axes[1, 0].semilogy(stepper.values, stepper.steps)
       >>> axes[1, 0].set_ylabel(r"$\Delta t$")
       >>> axes[1, 0].set_xlabel(r"$t$")

       >>> axes[0, 1].plot(stepper.values, stepper.error)
       >>> axes[0, 1].set_ylabel(r"error")
       >>> axes[0, 1].set_ylim(ymin=0, ymax=1.1)

       >>> axes[1, 1].semilogy(stepper.values, stepper.error)
       >>> axes[1, 1].set_ylabel("error")
       >>> axes[1, 1].set_xlabel(r"$t$")
       >>> axes[1, 1].set_ylim(ymin=1e-17, ymax=1.1)

       >>> plt.tight_layout()
       >>> plt.show()

    """

    def __init__(self, solvefor=(), minStep=0.):
        self.solvefor = solvefor
        self.minStep = minStep
        self.current = 0.
        self.steps = []
        self.values = []
        self.error = []

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

    def solve1(self, tryStep, var, eqn, bcs):
        """Solve one equation at each adapted step attempt.

        The default performs one sweep and returns its residual.  Override
        this method in order to customize the sweep loop.

        Parameters
        ----------
        tryStep : float
            Adapted step to attempt.
        var : ~fipy.variables.cellVariable.CellVariable
            Solution variable.
        eqn : ~fipy.terms.term.Term
            Equation to solve for `var`.
        bcs : tuple of ~fipy.boundaryConditions.BoundaryCondition
            Boundary conditions to apply in solution.

        Returns
        -------
        float
            Solution residual, as returned from
            :meth:~fipy.terms.term.Term.sweep`.
        """
        return eqn.sweep(var=var,
                         dt=tryStep,
                         boundaryConditions=bcs)

    def solve(self, tryStep):
        """Solve equations at each adapted step attempt.

        The default solves each variable/equation/boundary-condition set in
        succession and calculates the maximum error from all of them.
        Override this method in order to customize the sweep loop.

        Parameters
        ----------
        tryStep : float
            Adapted step to attempt.

        Returns
        -------
        float
            Solution error, positive and normalized to 1.

        """
        for var, eqn, bcs in self.solvefor:
            var.updateOld()

        error = 0.
        for var, eqn, bcs in self.solvefor:
            res = self.solve1(tryStep=tryStep,
                              var=var,
                              eqn=eqn,
                              bcs=bcs)

            # don't let error be zero
            error = max(error,
                        self.calcError(var=var,
                                       equation=eqn,
                                       boundaryConditions=bcs,
                                       residual=res)
                        + numerix.finfo(float).eps)

        return error

    def success(self, triedStep, error):
        """Action to perform after a successful adaptive solution step.

        Default determines the next step to take.

        .. warning::

           If the user overrides this method they should ensure to call the
           inherited :meth:`~fipy.steppers.stepper.Stepper.failure` method.

        Parameters
        ----------
        triedStep : float
            The step that was actually taken.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        nextStep : float
            The next step to attempt.

        """
        self.error.append(error)

        nextStep = self._calcNext(triedStep=triedStep, error=error)
        nextStep = self._lowerBound(tryStep=nextStep)

        return nextStep

    def failure(self, triedStep, error):
        """Action to perform when `solve()` returns an error greater than 1.

        Default resets the variable values and shrinks the step.

        .. warning::

           If the user overrides this method they should ensure to call the
           inherited :meth:`~fipy.steppers.stepper.Stepper.failure` method.

        Parameters
        ----------
        triedStep : float
            The step that was attempted.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        nextStep : float
            The next step to attempt.

        """
        for var, eqn, bcs in self.solvefor:
            var.value = var.old

        nextStep = self._shrinkStep(triedStep=triedStep, error=error)
        nextStep = self._lowerBound(tryStep=nextStep)

        return nextStep

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
        if tryStep < 0:
            sign = -1
        else:
            sign = 1
        tryStep = sign * max(abs(tryStep), abs(self.minStep))
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

    def _calcNext(self, triedStep, error):
        """Calculate next step after success

        Most subclasses of :class:`~fipy.steppers.stepper.Stepper` should
        override this method (default returns `triedStep` unchanged).

        Parameters
        ----------
        triedStep : float
            Step that succeeded.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Returns
        -------
        float
            New step.

        """
        return triedStep

    def _step(self, tryStep):
        """Solve at given step and then adapt.

        Parameters
        ----------
        tryStep : float
            Adapted step to attempt.

        Returns
        -------
        triedStep : float
            The step actually taken.
        nextStep : float
            The next step to try.

        """
        while True:
            error = self.solve(tryStep=tryStep)

            if error <= 1. or tryStep <= self.minStep:
                # step succeeded
                break
            else:
                # reject the step
                tryStep = self.failure(triedStep=tryStep, error=error)

        nextStep = self.success(triedStep=tryStep, error=error)

        return tryStep, nextStep

    def step(self, until, tryStep=None):
        """Perform an adaptive solution step.

        Parameters
        ----------
        until : float
            The value of the control variable to step to.
        tryStep : float
            The step to try first (default None).

        Returns
        -------
        triedStep : float
            The step actually taken.
        nextStep : float
            The next step to try.

        """
        tryStep = tryStep or self.minStep or (until - self.current)

        saveStep = None
        while True:
            maxStep = until - self.current
            if maxStep == 0:
                # reached `until`
                break

            if abs(tryStep) > abs(maxStep):
                saveStep = tryStep
                tryStep = maxStep
            else:
                saveStep = None

            triedStep, tryStep = self._step(tryStep=tryStep)

            self.current += triedStep

            self.steps.append(triedStep)
            self.values.append(self.current)

        return saveStep or triedStep, saveStep or tryStep
