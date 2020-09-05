

import JPlot.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import os
import sys
sys.path.append("../")


def test_plot1():
    for i in range(8):
        plt.plot(range(20), [j+i*8 for j in range(20)])
    plt.savefig("test.png", save_tex=True)
    plt.clf()


def test_replot():
    plt.replot_using_saved_data("test.png.plotData.json")


def test_subplots():
    fig, axes = plt.subplots(1, 2, figsize=(10, 4),
                             gridspec_kw={"wspace": 0, "hspace": 0},
                             subplot_kw={"sharey": True, "frame_on": True}
                             )

    d = np.arange(0, 20)
    axes[0].plot(d, d, )
    axes[0].fill_between(y1=d, x=d, alpha=0.2)

    d2 = np.arange(20, 0, -1)
    axes[1].plot(d2, d2, )
    axes[1].fill_between(y1=d2, x=d2, alpha=0.2)
    axes[1].set_yticks([])

    legend_elements = [Line2D([0], [0], color='red', lw=2, ls='-', label='la'),
                       Line2D([0], [0], color='green',
                              lw=2.5, ls='--', label='lb'),
                       Patch(facecolor='black', edgecolor='gray', label='pa', alpha=0.3)]

    plt.legend(handles=legend_elements, frameon=True, facecolor="white", edgecolor="black", framealpha=1,
               labelspacing=0.2, columnspacing=0.6, bbox_to_anchor=(0.2, 1), ncol=2)
    fig.tight_layout()
    plt.savefig("test", pad_inches=0, bbox_inches='tight')


if __name__ == "__main__":
    test_plot1()
    # test_replot()
    # test_subplots()
