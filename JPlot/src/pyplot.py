# -*- coding: utf-8 -*-
import json
import subprocess

from src.const.color import COLORS, SINGLE_COLORS, BW_COLORS
from src.const.const import DEFAULT_HATCH, DEFAULT_LINESTYLE, DEFAULT_MARKER
from src.const.globalSettings import *

from src.pyplotAux import update_plot_style, general_processing
from src.pyplotAux import _extract_arg, _postprocess_plot, _default_process
from src.ax import AX
from src.topUtils import *
import matplotlib.pyplot as plt
from matplotlib.pyplot import *



def plot(*args, **kwargs):
    general_processing(plt, *args, **kwargs)
    _default_process()


def semilogx(*args, **kwargs):
    general_processing(plt, *args, **kwargs)
    _default_process()


def bar(*args, **kwargs):
    if "hatch" not in kwargs:
        kwargs["hatch"] = next(GLOBAL_SETTING_DICT["hatch"])
    general_processing(plt, *args, **kwargs)


def box(*args, **kwargs):
    general_processing(plt, *args, **kwargs)


def errorbar(*args, **kwargs):
    general_processing(plt, *args, **kwargs)


def boxplot(*args, **kwargs):
    # update_plot_style(**kwargs)
    # e_args = _extract_arg(kwargs)
    # e_args["has_legend"] = False  # labels is diffent here
    # plt.boxplot(*args, **kwargs)
    general_processing(plt, *args, **kwargs)
    # _postprocess_plot(**e_args)


def scatter(*args, **kwargs):
    general_processing(plt, *args, **kwargs)
    _default_process()


def hist(*args, **kwargs):
    general_processing(plt, *args, **kwargs)


def fill_between(*args, **kwargs):
    general_processing(plt, *args, **kwargs)


def savefig(*args, **kwargs):
    update_plot_style()
    if "fname" in kwargs:
        figname = kwargs["fname"]
    else:
        figname = args[0]
        args = args[1:]

    if figname.split(".")[-1] not in set(("eps", "jpeg", "jpg", "pdf", "pgf", "png", "ps", "raw", "rgba", "svg", "svgz", "tif", "tiff")):
        figname += "." + GLOBAL_SETTING_DICT["output_format"]
    kwargs["fname"] = figname

    if "bbox_inches" not in kwargs:
        kwargs["bbox_inches"] = 'tight'

    # if not kwargs.pop("no_save_plot_data", False):
    kwargs.pop("no_save_plot_data", False)
    if kwargs.pop("save_plot_data", False):
        with open(f"{figname}"+".plotData.json", "w") as ofile:
            json.dump(GLOBAL_SETTING_DICT["plot_data"], ofile)
    GLOBAL_SETTING_DICT["plot_data"] = []

    if kwargs.pop("save_tex", False):
        try:
            import tikzplotlib
            filename = figname.replace(".png", ".tex").replace(".pdf", ".tex")
            tikzplotlib.save(filename)
        except Exception as e:
            print(e)

    plt.savefig(*args, **kwargs)
    if GLOBAL_SETTING_DICT["auto_open"]:
        subprocess.run(["open", figname], shell=False)
    GLOBAL_SETTING_DICT["update_plot_style"] = True


def cla():
    reset()
    plt.cla()


def clf():
    reset()
    plt.clf()


def close():
    reset()
    plt.close()

def reset():
    global GLOBAL_SETTING_DICT
    GLOBAL_SETTING_DICT["color"] = get_default_color()
    GLOBAL_SETTING_DICT["marker"] = get_default_marker()
    GLOBAL_SETTING_DICT["linestyle"] = get_default_linestyle()
    GLOBAL_SETTING_DICT["hatch"] = get_default_hatch()
    GLOBAL_SETTING_DICT["update_plot_style"] = True


def replot(plot_data_file):
    replot_using_saved_data(plot_data_file)


def replot_using_saved_data(plot_data_file):
    with open(plot_data_file, "r") as ifile:
        plot_data = json.load(ifile)
    for p in plot_data:
        args = eval(p[1])
        kwargs = eval(p[2])
        # print(args, type(args))
        print(kwargs, type(kwargs))
        globals()[p[0]](*args, **kwargs)
    savefig(plot_data_file.replace(".plotData.json", ""))


def xticks(*args, **kwargs):
    plt.xticks(*args, **kwargs)


def yticks(*args, **kwargs):
    plt.yticks(*args, **kwargs)


def set_n_colors(n):
    global GLOBAL_SETTING_DICT
    GLOBAL_SETTING_DICT["color"] = get_color(n)
    return GLOBAL_SETTING_DICT["color"]


def set_single_colors(n):
    global GLOBAL_SETTING_DICT
    GLOBAL_SETTING_DICT["color"] = get_single_color(n)
    return GLOBAL_SETTING_DICT["color"]


def set_bw_colors(n):
    global GLOBAL_SETTING_DICT
    GLOBAL_SETTING_DICT["color"] = get_bw_color(n)
    return GLOBAL_SETTING_DICT["color"]


def subplot(*args, **kwargs):
    update_plot_style(**kwargs)
    return getattr(plt, "subplot")(*args, **kwargs)


def subplots(*args, **kwargs):
    update_plot_style(**kwargs)
    fig, axes = getattr(plt, "subplots")(*args, **kwargs)
    new_axes = [AX(i) for i in axes]
    return fig, new_axes

