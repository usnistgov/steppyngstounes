import numpy as np
from steppyngstounes import CheckpointStepper
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
stepper = CheckpointStepper(start=0., stop=totaltime, inclusive=True,
                            stops=10.**np.arange(-5, 5), record=True)
for step in stepper:
    new = np.tanh((step.end / totaltime - 0.5) / (2 * width))

    _ = step.succeeded(value=new)
#
s = "{} succesful steps in {} attempts"
print(s.format(stepper.successes.sum(),
               len(stepper.steps)))
# Expected:
## 10 succesful steps in 10 attempts
#
steps = stepper.steps[stepper.successes]
ix = steps.argsort()
values = stepper.values[stepper.successes][ix]
errors = abs(values[1:] - values[:-1]) / errorscale
#
# As this stepper doesn't use the error, we don't expect the post
