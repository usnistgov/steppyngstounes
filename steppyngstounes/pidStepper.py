from __future__ import division
from __future__ import unicode_literals
from fipy.steppers.stepper import Stepper

__all__ = ["PIDStepper"]
from future.utils import text_to_native_str
__all__ = [text_to_native_str(n) for n in __all__]

class PIDStepper(Stepper):
    """Adaptive stepper using a PID controller.

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
        :meth:`~fipy.steppers.stepper.Stepper.success` and
        :meth:`~fipy.steppers.stepper.Stepper.failure`.

    Parameters
    ----------
    solvefor : tuple of tuple
        Each tuple holds a `CellVariable` to solve for, the equation to
        solve, and the old-style boundary conditions to apply.
    proportional, integral, derivative : float
        PID control constants.

    """

    def __init__(self, solvefor=(), proportional=0.075, integral=0.175, derivative=0.01):
        Stepper.__init__(self, solvefor=solvefor)

        self.proportional = proportional
        self.integral = integral
        self.derivative = derivative

        self.error = [1., 1., 1.]

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

    def _calcPrev(self, triedStep, prevStep, error):
        """Adjust previous step

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
        return triedStep**2 / prevStep

    def _calcNext(self, triedStep, prevStep, error):
        """Calculate next step after success

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
        self.error.append(error)

        factor = ((self.error[-2] / self.error[-1])**self.proportional
                  * (1. / self.error[-1])**self.integral
                  * (self.error[-2]**2
                     / (self.error[-1] * self.error[-3]))**self.derivative)

        # could optionally omit and keep whole error history
        _ = self.error.pop(0)

        return factor * prevStep
