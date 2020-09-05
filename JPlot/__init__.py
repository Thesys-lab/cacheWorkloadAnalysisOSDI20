

"""
    __init__


    author: Jason <peter.waynechina@gmail.com>

"""

__version__ = "0.0.13"


import os, sys
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)), )
# sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "src/"))


import matplotlib
matplotlib.use("Agg")


# import src as JPlot
from src import pyplot
# from src import pyplot as pyplot2
from src import plotTools


# import JPlot as JPlot
# import pyplot as pyplot
# import plotTools as plotTools
# from const.color import COLORS, SINGLE_COLORS, BW_COLORS, DEFAULT_COLOR  
# from const.const import DEFAULT_HATCH, DEFAULT_MARKER, DEFAULT_LINESTYLE


from src.topUtils import *








# pyplot.set_n_colors(2)
