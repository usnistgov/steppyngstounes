import numpy as np
from steppyngstounes import ScaledStepper
#
# We'll demonstrate using an artificial function that changes
# abruptly, but smoothly, with time,
#
# .. math::
#
#    \tanh\frac{\frac{t}{t_\mathrm{max}} - \frac{1}{2}}
#                {2 w}
#
# where :math:`t` is the elapsed time, :math:`t_\mathrm{max}` is
# total time desired, and :math:`w` is a measure of the step width.
#
totaltime = 1000.
width = 0.01
#
# The scaled "error" will be a measure of how much the solution has
# changed since the last step, \| `new` - `old` \| / `errorscale`).
#
errorscale = 1e-2
#
# Iterate over the stepper from `start` to `stop` (inclusive of
# calculating a value at `start`).
#
old = -1.
stepper = ScaledStepper(start=0., stop=totaltime, inclusive=True,
                        record=True)
for step in stepper:
    new = np.tanh((step.end / totaltime - 0.5) / (2 * width))

    error = abs(new - old) / errorscale

    if step.succeeded(value=new, error=error):
        old = new
#
s = "{} succesful steps in {} attempts"
print(s.format(stepper.successes.sum(),
               len(stepper.steps)))
# Expected:
## 296 succesful steps in 377 attempts
#
steps = stepper.steps[stepper.successes]
ix = steps.argsort()
values = stepper.values[stepper.successes][ix]
errors = abs(values[1:] - values[:-1]) / errorscale
#
# Check that the post hoc error satisfies the desired tolerance.
#
print(max(errors) < 1.)
# Expected:
## True
