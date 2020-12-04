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
        }

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
        factor = min(1. / error, 0.8)
        return factor * dt

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
        return dt**2 / dtPrev

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
        self.error[2] = error

        dtNext = dtPrev * ((self.error[1] / self.error[2])**self.proportional
                           * (1. / self.error[2])**self.integral
                           * (self.error[1]**2 / (self.error[2] * self.error[0]))**self.derivative)

        self.error[0] = self.error[1]
        self.error[1] = self.error[2]

        return dtNext
