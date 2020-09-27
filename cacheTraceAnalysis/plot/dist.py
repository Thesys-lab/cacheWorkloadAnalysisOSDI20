

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import numpy as np
import subprocess
import libMC


def plot_dist(trace_path, dist_type="dist"):
  if not os.path.exists(trace_path):
    logging.error("trace {} not exists".format(trace_path))
    return 

  cache_name = trace_path.split("/")[-1]
  figname = "{}_{}".format(dist_type, cache_name)
  metadata_file = "metadata/{}_{}.npz".format(dist_type, cache_name)
  reader_params = {"trace_path": trace_path, "trace_type": "t", "obj_id_type": "l", }

  if os.path.exists(metadata_file):
    logging.info("use precomputed data {}".format(metadata_file))
    dist = np.load(metadata_file)["dist"]
  else:
    dist = libMC.get_last_access_dist(reader_params)
    np.savez_compressed(metadata_file, dist=dist)


  plotTools.plot_cdf(dist)
  plt.xscale("log")
  # plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.2f}'.format(log_base**x)))
  plt.xlabel("# request since last access")
  plt.ylabel("Fraction of request (CDF)")
  plt.grid(linestyle="--")
  plt.savefig("{}/{}".format(FIG_DIR, figname))
  plt.clf()


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--plot_type", type=str, required=True, choices=("stack_dist", "dist", "inter_arrival"), help="plot_type")
  ap.add_argument("--trace_path", type=str, required=True, help="trace path")
  p = ap.parse_args()

  if p.plot_type == "stack_dist": 
    plot_dist(p.trace_path, "stack_dist")
  elif p.plot_type == "inter_arrival" or p.plot_type == "dist": 
    plot_dist(p.trace_path, "dist")
  else: 
    raise RuntimeError("unknown plot type {}".format(p.plot_type))
