def plotSteps():
    from matplotlib import pyplot as plt

    plt.rcParams['lines.linestyle'] = ""
    plt.rcParams['lines.marker'] = "."
    plt.rcParams['lines.markersize'] = 3
    fig, axes = plt.subplots(2, 2, sharex=True)

    fig.suptitle(r"10 successful $\mathtt{CheckpointStepper}$ "
                 r"steps and trajectory of 10 attempts")

    axes[0, 0].plot(stepper.steps, stepper.values, color="gray",
                    linestyle="-", linewidth=0.5, marker="")
    axes[0, 0].plot(stepper.steps[stepper.successes],
                    stepper.values[stepper.successes])
    axes[0, 0].set_ylabel("value")

    # plot post-hoc step size and error
    # reorder, as steps may not be monotonic

    steps = stepper.steps[stepper.successes]
    ix = steps.argsort()
    values = stepper.values[stepper.successes][ix]
    errors = abs(values[1:] - values[:-1]) / errorscale

    axes[1, 0].semilogy(steps[1:], steps[1:] - steps[:-1])
    axes[1, 0].set_ylabel(r"$\Delta t$")
    axes[1, 0].set_xlabel(r"$t$")

    axes[0, 1].plot(steps[1:], errors)
    axes[0, 1].axhline(y=1., color="red",
                       linestyle="-", linewidth=0.5, marker="")
    axes[0, 1].set_ylabel("error")
    axes[0, 1].set_ylim(ymin=1e-17, ymax=None)

    axes[1, 1].semilogy(steps[1:], errors)
    axes[1, 1].axhline(y=1., color="red",
                       linestyle="-", linewidth=0.5, marker="")
    axes[1, 1].set_ylabel("error")
    axes[1, 1].set_xlabel(r"$t$")
    axes[1, 1].set_ylim(ymin=1e-17, ymax=None)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.show()
#
plotSteps() # doctest: +SKIP
