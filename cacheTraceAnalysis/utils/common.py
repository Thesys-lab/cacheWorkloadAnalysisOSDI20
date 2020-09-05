

import os
import sys
import math
import time
from pprint import pprint, pformat
from collections import defaultdict, deque
import json
import pickle
import logging

sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")

from traceReader.twrBinTraceReader import TwrShortBinTraceReader


#################################### logging related #####################################
logging.basicConfig(format='%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s]: \t%(message)s',
                    level=logging.INFO, datefmt='%H:%M:%S')


LOG_NAME = "cacheTraceAnalysis"
LOG_FMT = '%(asctime)s: %(levelname)s [%(filename)s:%(lineno)s]: \t%(message)s'
LOG_DATEFMT ='%H:%M:%S'

from .const import *


try:
  import JPlot
  from JPlot import pyplot as plt
  from JPlot import plotTools as plotTools

  JPlot.set_auto_open(False)
  JPlot.set_plot_style("presentation-onecol")
  from matplotlib.ticker import MaxNLocator
except Exception as e:
  print(e)





####################################### output related ############################################
FIG_DIR = "fig"
METADATA_DIR = "metadata"

if not os.path.exists(METADATA_DIR):
  os.makedirs(METADATA_DIR)
if not os.path.exists(FIG_DIR):
  os.makedirs(FIG_DIR)


def save_metadata(metadata, metadata_name):
  metadata_path = f"{METADATA_DIR}/{metadata_name}"
  if not os.path.exists(os.path.dirname(metadata_path)):
    os.makedirs(os.path.dirname(metadata_path))
  if metadata_name.endswith("pickle"):
    with open(metadata_path, "wb") as ofile:
      pickle.dump(metadata, ofile)
  elif metadata_name.endswith("json"):
    with open(metadata_path, "w") as ofile:
      json.dump(metadata, ofile)
  else:
    raise RuntimeError("unknown suffix in metadata name {}".format(metadata_name))
  return True

def load_metadata(metadata_name):
  metadata_path = f"{METADATA_DIR}/{metadata_name}"
  if not os.path.exists(metadata_path):
    return None
  logging.info("use pre-calculated data at {}".format(metadata_path))
  if metadata_name.endswith("pickle"):
    with open(metadata_path, "rb") as ifile:
      return pickle.load(ifile)
  elif metadata_name.endswith("json"):
    with open(metadata_path, "r") as ifile:
      return json.load(ifile)
  else:
    raise RuntimeError("unknown suffix in metadata name {}".format(metadata_name))














