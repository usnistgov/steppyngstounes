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

    """

    __doc__ += Stepper._stepper_test.format(stepperclass="PIDStepper")

    def __init__(self, solvefor=(), minStep=0.,
                 proportional=0.075, integral=0.175, derivative=0.01):
        super(PIDStepper, self).__init__(solvefor=solvefor, minStep=minStep)

        self.proportional = proportional
        self.integral = integral
        self.derivative = derivative

        # pre-seed the error list as this algorithm needs historical errors
        self.error += [1., 1.]
        self.steps += [self.minStep, self.minStep]
        if self.values:
            current = self.values[-1]
        else:
            current = 0.
        self.values += [current + self.steps[-2],
                        current + self.steps[-2] + self.steps[-1]]

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
