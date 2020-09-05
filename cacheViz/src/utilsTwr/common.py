

import os
import sys
import math
import time
from pprint import pprint, pformat
from collections import defaultdict, deque, namedtuple
import json
import glob
import logging
import importlib  
from concurrent.futures import ProcessPoolExecutor, as_completed


#################################### logging related #####################################
FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

# logging.basicConfig(format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s - %(funcName)20s() ]: \t%(message)s',


LOG_NAME = "toolsTwr"
LOG_FMT = '%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s]: \t%(message)s'
LOG_DATEFMT ='%H:%M:%S'

# logging.basicConfig(filename=LOG_NAME, format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s]: \t%(message)s',
#                     level=logging.DEBUG, datefmt='%H:%M:%S')
logging.basicConfig(format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s]: \t%(message)s',
                    level=logging.INFO, datefmt='%H:%M:%S')

# def util_get_logger(name):
#   logger = logging.getLogger(name)
#   logger.setLevel(logging.DEBUG)
#   formatter = logging.Formatter(LOG_FMT)

#   # fh = logging.FileHandler(LOG_NAME + '.log')
#   # fh.setFormatter(formatter)
#   # fh.setLevel(logging.DEBUG)

#   ch = logging.StreamHandler()
#   ch.setFormatter(formatter)
#   ch.setLevel(logging.INFO)

#   # logger.addHandler(fh) 
#   logger.addHandler(ch)
#   # logger.propagate = False 
#   return logger

# logger = util_get_logger(LOG_NAME)





# sys.path.append(os.path.expanduser("~/cacheTraceAnalysis/tools/"))
# sys.path.append(os.path.expanduser("~/JPlot/"))
sys.path.append(os.path.expanduser("~/"))
# sys.path.append(os.path.expanduser("~/myworkspace/cacheTraceAnalysis/tools/"))
# sys.path.prepend(os.path.expanduser("~/myworkspace/JPlot/"))
sys.path.append(os.path.expanduser("~/myworkspace/"))

# from data import *
# from cacheTraceAnalysis.tools.traceReader.twrBinTraceReader import TwrBinTraceReader, TwrShortBinTraceReader, TwrShortBinTraceReaderOld
# from cacheTraceAnalysis.tools.traceReader.twrBinTraceReaderHDFS import TwrBinTraceReaderHDFS, TwrShortBinTraceReaderHDFS
# from cacheTraceAnalysis.tools.traceReader.twrTraceReader import TwrTraceReader


try:
  import JPlot
  from JPlot import pyplot as plt
  from JPlot import plotTools as plotTools
  JPlot.set_auto_open(False)
  JPlot.set_plot_style("presentation-onecol")
except Exception as e:
  logging.warning("fail to import JPlot {}".format(e))






####################################### const ############################################


KiB = 1024
MiB = 1024*1024 
GiB = 1024*1024*1024
TiB = 1024*1024*1024*1024

KB = 1000
MB = 1000*1000 
GB = 1000*1000*1000
TB = 1000*1000*1000*1000



##################################### OUTPUT related ##################################### 

FIG_DIR = "fig"
METADATA_DIR = "metadata"

if not os.path.exists(METADATA_DIR):
  os.makedirs(METADATA_DIR)
if not os.path.exists(FIG_DIR):
  os.makedirs(FIG_DIR)




