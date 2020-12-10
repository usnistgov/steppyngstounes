from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["PseudoRKQSStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PseudoRKQSStepper(Stepper):
    r"""Pseudo-Runge-Kutta adaptive stepper.

    Based on the ``rkqs`` (Runge-Kutta "quality-controlled" stepper)
    algorithm of Numerical Recipes in C: 2nd Edition, Section 16.2.

    Not really appropriate, since we're not doing the `rkck` Runge-Kutta
    steps in the first place, but works OK.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = \mathrm{min}\left[S \left(e_n\right)^{P_\text{grow}}, f_\text{max} \right] \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`e_n` is the error at step :math:`n`.  :math:`S` is the safety
    factor, :math:`P_\text{grow}` is the growth exponent, and
    :math:`f_\text{max}` is the maximum factor to grow the step size.

    On failure, retries with

    .. math::

       \Delta_{n} = \mathrm{max}\left[S \left(e_n\right)^{P_\text{shrink}}, f_\text{min} \right] \Delta_n

    where :math:`P_\text{shrink}` is the shrinkage exponent and :math:`f_\text{min}`
    is the minimum factor to shrink the stepsize.

    .. note::

        The user must override
        :meth:`~fipy.steppers.stepper.Stepper.calcError` and may override
        :meth:`~fipy.steppers.stepper.Stepper.solve`,
        :meth:`~fipy.steppers.stepper.Stepper.success`, and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.
    minStep : float
        Smallest step to allow (default 0).
    safety : float
        RKQS control safety factor :math:`S` (default 0.9).
    pgrow : float
        RKQS control growth exponent :math:`P_\text{grow}` (default -0.2).
    pshrink : float
        RKQS control shrinkage exponent :math:`P_\text{shrink}` (default -0.25).
    maxgrow : float
        RKQS control maximum factor to grow step size :math:`f_\text{max}` (default 5).
    minshrink : float
        RKQS control minimum factor to shrink step size :math:`f_\text{min}` (default 0.1).

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

       >>> dt = 50.
       >>> totaltime = 1000.
       >>> checkpoints = (fp.numerix.arange(int(totaltime / dt)) + 1) * dt

       Rather than solve any actual PDEs, we'll demonstrate using an
       artificial function that changes abruptly, but smoothly, with time.

       >>> def dummyfunc(t, width):
       ...     return numerix.tanh((t / totaltime - 0.5) / (2 * width))

       Create a subclass of :class:`~fipy.steppers.pidStepper.PIDStepper`

       >>> errorscale = 1e-3

       >>> from fipy.steppers import PseudoRKQSStepper

       >>> class MyRKQSStepper(PseudoRKQSStepper):
       ...
       ...     def solve1(self, tryStep, var, eqn, bcs):
       ...         var.value = dummyfunc(t=self.current + tryStep, width=0.01)
       ...         return 0.
       ...
       ...     def calcError(self, var, equation, boundaryConditions, residual):
       ...         return numerix.L1norm(var - var.old) / errorscale + 1e-16

       Finally, instantiate a stepper with the variable to solve for and the
       smallest step to allow.

       >>> stepper = MyRKQSStepper(solvefor=((phi, None, ()),), minStep=dt / 1e6)

       Call :meth:`~fipy.steppers.pseudoRKQSStepper.PseudoRKQSStepper.step` for each desired
       time step.  Pass the time to step to `until` and the time step to try
       first `tryStep`.

       >>> tryStep = dt
       >>> for until in checkpoints:
       ...     prevStep, tryStep = stepper.step(until=until, tryStep=tryStep)

       >>> print(len(stepper.steps))
       123456

    .. plot::
       :context:

       >>> fix, axes = plt.subplots(2, 2, sharex=True)

       >>> axes[0, 0].plot(stepper.values, dummyfunc(numerix.array(stepper.values), width=0.01), linestyle="", marker=".")
       >>> axes[0, 0].set_ylabel(r"$\phi$")
       >>> # axes[0, 0].set_xlabel(r"$t$")

       >>> axes[1, 0].semilogy(stepper.values, stepper.steps, linestyle="", marker=".")
       >>> axes[1, 0].set_ylabel(r"$\Delta t$")
       >>> axes[1, 0].set_xlabel(r"$t$")

       >>> axes[0, 1].plot(stepper.values, stepper.error, linestyle="", marker=".")
       >>> axes[0, 1].set_ylabel(r"error")
       >>> axes[0, 1].set_ylim(ymin=0, ymax=1.1)

       >>> axes[1, 1].semilogy(stepper.values, stepper.error, linestyle="", marker=".")
       >>> axes[1, 1].set_ylabel("error")
       >>> axes[1, 1].set_xlabel(r"$t$")

       >>> plt.tight_layout()
       >>> plt.show()

    """

    def __init__(self, solvefor=(), minStep=0.,
                 safety=0.9, pgrow=-0.2, pshrink=-0.25,
                 maxgrow=5, minshrink=0.1):
        super(PseudoRKQSStepper, self).__init__(solvefor=solvefor, minStep=minStep)
        self.safety = safety
        self.pgrow = pgrow
        self.pshrink = pshrink
        self.maxgrow = maxgrow
        self.minshrink = minshrink
        self.errcon = (maxgrow/safety)**(1./pgrow)

    def _shrinkStep(self, triedStep, error):
        """Reduce step after failure

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
        factor = max(self.safety * error**self.pshrink, self.minshrink)
        return factor * triedStep

    def _calcNext(self, triedStep, error):
        """Calculate next step after success

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
        if error > self.errcon:
            factor = self.safety * error**self.pgrow
        else:
            factor = self.maxgrow

        return factor * triedStep
