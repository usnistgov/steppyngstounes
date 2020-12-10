from __future__ import division
from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["PIDStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PIDStepper(Stepper):
    r"""Adaptive stepper using a PID controller.

    Calculates a new step as

    .. math::

       \Delta_{n+1} = \left(\frac{e_{n-1}}{e_n}\right)^{k_P}
                      \left(\frac{1}{e_n}\right)^{k_I}
                      \left(\frac{e_{n-1}^2}{e_n e_{n-2}}\right)^{k_D}
                      \Delta_n

    where :math:`\Delta_n` is the step size for step :math:`n` and
    :math:`e_n` is the error at step :math:`n`.  :math:`k_P` is the
    proportional coefficient, :math:`k_I` is the integral coefficient, and
    :math:`k_D` is the derivative coefficient.

    On failure, retries with

    .. math::

       \Delta_n = \mathrm{min}\left(\frac{1}{e_n}, 0.8\right) \Delta_n

    Based on::

        @article{PIDpaper,
           author =  {A. M. P. Valli and G. F. Carey and A. L. G. A. Coutinho},
           title =   {Control strategies for timestep selection in finite element
                      simulation of incompressible flows and coupled
                      reaction-convection-diffusion processes},
           journal = {Int. J. Numer. Meth. Fluids},
           volume =  47,
           year =    2005,
           pages =   {201-231},
           doi =     {10.1002/fld.805},
        }

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
    proportional : float
        PID control :math:`k_P` coefficient (default 0.075).
    integral : float
        PID control :math:`k_I` coefficient (default 0.175).
    derivative : float
        PID control :math:`k_D` coefficient (default 0.01).

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

       >>> from fipy.steppers import PIDStepper

       >>> class MyPIDStepper(PIDStepper):
       ...
       ...     def solve1(self, tryStep, var, eqn, bcs):
       ...         var.value = dummyfunc(t=self.current + tryStep, width=0.01)
       ...         return 0.
       ...
       ...     def calcError(self, var, equation, boundaryConditions, residual):
       ...         return numerix.L1norm(var - var.old) / errorscale + 1e-16

       Finally, instantiate a stepper with the variable to solve for and the
       smallest step to allow.

       >>> stepper = MyPIDStepper(solvefor=((phi, None, ()),), minStep=dt / 1e6)

       Call :meth:`~fipy.steppers.pidStepper.PIDStepper.step` for each desired
       time step.  Pass the time to step to `until` and the time step to try
       first `tryStep`.

       >>> tryStep = dt
       >>> for until in checkpoints:
       ...     prevStep, tryStep = stepper.step(until=until, tryStep=tryStep)

       >>> print(len(stepper.steps))
       12345

    .. plot::
       :context:

       >>> fix, axes = plt.subplots(2, 2, sharex=True)

       >>> axes[0, 0].plot(stepper.values, dummyfunc(numerix.array(stepper.values), width=0.01), linestyle="", marker=".")
       >>> axes[0, 0].set_ylabel(r"$\phi$")

       >>> axes[1, 0].semilogy(stepper.values, stepper.steps, linestyle="", marker=".")
       >>> axes[1, 0].set_ylabel(r"$\Delta t$")
       >>> axes[1, 0].set_xlabel(r"$t$")

       >>> axes[0, 1].plot(stepper.values, stepper.error[2:], linestyle="", marker=".")
       >>> axes[0, 1].set_ylabel(r"error")
       >>> axes[0, 1].set_ylim(ymin=0, ymax=1.1)

       >>> axes[1, 1].semilogy(stepper.values, stepper.error[2:], linestyle="", marker=".")
       >>> axes[1, 1].set_ylabel("error")
       >>> axes[1, 1].set_xlabel(r"$t$")

       >>> plt.tight_layout()
       >>> plt.show()

    """

    def __init__(self, solvefor=(), minStep=0.,
                 proportional=0.075, integral=0.175, derivative=0.01):
        super(PIDStepper, self).__init__(solvefor=solvefor, minStep=minStep)

        self.proportional = proportional
        self.integral = integral
        self.derivative = derivative

        # pre-seed the error list as this algorithm needs historical errors
        self.error += [1., 1.]

        self.prevStep = self.minStep

    def failure(self, triedStep, error):
        """Action to perform when `solve()` returns an error greater than 1.

        Resets the variable values, shrinks the step, and adjusts the
        "`prevStep`" used by the algorithm.

        .. warning::

           If the user overrides this method they should ensure to call the
           inherited :meth:`~fipy.steppers.stepper.PIDStepper.failure` method.

        Parameters
        ----------
        triedStep : float
            The step that was attempted.
        error : float
            Error (positive and normalized to 1) from the last solve.

        Return
        ------
        nextStep : float
            The next step to attempt.

        """
        nextStep = super(PIDStepper, self).failure(triedStep=triedStep, error=error)

        self.prevStep = triedStep**2 / (self.prevStep or self.minStep)

        return nextStep

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
        factor = min(1. / error, 0.8)
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
        factor = ((self.error[-2] / self.error[-1])**self.proportional
                  * (1. / self.error[-1])**self.integral
                  * (self.error[-2]**2
                     / (self.error[-1] * self.error[-3]))**self.derivative)

        # could optionally drop the oldest error
        # _ = self.error.pop(0)

        tryStep = factor * (self.prevStep or triedStep)

        self.prevStep = tryStep

        return tryStep
