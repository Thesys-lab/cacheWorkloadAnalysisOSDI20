""" a tool to run all analysis on given traces 

"""


import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from utils.common import *
from core.traceStat import TraceStat 


def gen_trace_stat(trace_path, ofilename): 
  if ofilename is None: 
    ofilename = "traceStat." + trace_path.split("/")[-1]
  if os.path.exists(ofilename):
    logging.info("{} exists".format(ofilename))
  else:
    print("need to calculate stat {}".format(ofilename))
  if not os.path.exists(os.path.dirname(ofilename)):
    os.makedirs(os.path.dirname(ofilename))
  reader = TwrShortBinTraceReader(trace_path)
  stat = TraceStat(reader)
  ofile = open(ofilename, "w")
  ofile.write("{}\n".format(stat))
  ofile.write("##"*48+"\n")
  ofile.close() 


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  ap.add_argument("--type", type=str, help="compute type")
  ap.add_argument("--output", type=str, default=None, help="output path")
  # ap.add_argument("--window", type=int, default=60, help="the size of window in sec")
  p = ap.parse_args()

  if p.type == "trace_stat":
    gen_trace_stat(p.trace, p.output)







