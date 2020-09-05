""" plot request rate

"""


import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import numpy as np 
from scipy import stats
from scipy.optimize import minimize 
from scipy.optimize import curve_fit
from scipy import stats 


def cal_popularity(trace_reader):
  """ calculate popularity related """ 

  metadata_name = "popularity/objCnt_{}.pickle".format(trace_reader.trace_path.split("/")[-1])
  loaded = load_metadata(metadata_name)
  if loaded is not None:
    return loaded 

  obj_cnt_dict = defaultdict(int)
  for req in trace_reader:
    if req.logical_time % 20000000 == 0:
      logging.debug("{} req".format(req.logical_time))
    obj_cnt_dict[req.obj_id] += 1

  obj_cnt_sorted_list = list(sorted(obj_cnt_dict.values(), reverse=True))
  max_obj_cnt = max(obj_cnt_dict.values())
  obj_cnt_cnt_dict = defaultdict(int)
  for cnt in obj_cnt_dict.values():
    obj_cnt_cnt_dict[cnt] += 1

  trace_reader.reset()
  save_metadata((obj_cnt_sorted_list, obj_cnt_cnt_dict), metadata_name)

  return obj_cnt_sorted_list, obj_cnt_cnt_dict


def plot_popularity_rank(trace_reader):
  obj_cnt_sorted_list, _ = cal_popularity(trace_reader)
  n_pts = len(obj_cnt_sorted_list)

  plt.plot(obj_cnt_sorted_list, nomarker=True)
  plt.xlabel("Object rank")
  plt.ylabel("Frequency")
  plt.grid(linestyle="--")
  plt.xscale("log")
  plt.yscale("log")
  plt.savefig("{}/{}_popularity_rank".format(FIG_DIR, trace_reader.trace_path.split("/")[-1]), no_save_plot_data=True)
  plt.clf()

  x = np.log(np.arange(1, 1+n_pts))
  y = np.log(np.array(obj_cnt_sorted_list))
  slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)

  if obj_cnt_sorted_list[0] < 100:
    s = "{:48} {:12} obj alpha {:.4f}, r^2 {:.4f} (the most popular object has access cnt less than 100)".format(
      trace_reader.trace_path.split("/")[-1], n_pts, 0, 0, 0, )
  else:
    s = "{:48} {:12} obj alpha {:.4f}, r^2 {:.4f}".format(trace_reader.trace_path.split("/")[-1], n_pts, -slope, r_value*r_value)

  print(s)
  with open("alpha", "a") as ofile:
    ofile.write(s+"\n")

  return s


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="file path to trace")
  p = ap.parse_args()

  reader = TwrShortBinTraceReader(p.trace)

  plot_popularity_rank(reader)





