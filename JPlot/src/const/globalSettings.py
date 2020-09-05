

import copy
from src.const.color import DEFAULT_COLOR
from src.const.const import *

GLOBAL_SETTING_DICT = {
    "plot_style": "presentation",
    "auto_open": False,
    "output_format": "png",
    "update_plot_style": True,
    "color": copy.deepcopy(DEFAULT_COLOR), 
    "marker": copy.deepcopy(DEFAULT_MARKER),
    "linestyle": copy.deepcopy(DEFAULT_LINESTYLE),
    "hatch": copy.deepcopy(DEFAULT_HATCH), 
    "plot_data": [],
}



