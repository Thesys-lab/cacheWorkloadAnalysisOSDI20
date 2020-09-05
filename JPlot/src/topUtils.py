

import copy
from src.const.globalSettings import GLOBAL_SETTING_DICT
from src.const.color import COLORS, SINGLE_COLORS, BW_COLORS, DEFAULT_COLOR
from src.const.const import DEFAULT_HATCH, DEFAULT_LINESTYLE, DEFAULT_MARKER

global GLOBAL_SETTING_DICT


def set_plot_style(style):
    GLOBAL_SETTING_DICT["plot_style"] = style
    GLOBAL_SETTING_DICT["update_plot_style"] = True


def set_auto_open(auto_open=True):
    GLOBAL_SETTING_DICT["auto_open"] = auto_open
    GLOBAL_SETTING_DICT["update_plot_style"] = True


def set_output_format(format):
    GLOBAL_SETTING_DICT["output_format"] = format
    GLOBAL_SETTING_DICT["update_plot_style"] = True


def get_default_hatch():
    return copy.deepcopy(DEFAULT_HATCH)


def get_default_marker():
    return copy.deepcopy(DEFAULT_MARKER)


def get_default_linestyle():
    return copy.deepcopy(DEFAULT_LINESTYLE)


def get_default_color():
    return copy.deepcopy(DEFAULT_COLOR)


def get_color(n):
    if n in COLORS:
        return copy.deepcopy(COLORS[n])
    else:
        return copy.deepcopy(DEFAULT_COLOR)


def get_single_color(n):
    if n in SINGLE_COLORS:
        return copy.deepcopy(SINGLE_COLORS[n])
    else:
        raise RuntimeError("unsupported number of colors {}".format(n))


def get_bw_color(n):
    if n in BW_COLORS:
        return copy.deepcopy(BW_COLORS[n])
    else:
        raise RuntimeError("unsupported number of colors {}".format(n))

# def reset():
#     pass
