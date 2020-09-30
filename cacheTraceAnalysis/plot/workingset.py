"""
  plots how total workseting set increase over time 

"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import bisect


SLAB_SIZES = [96, 120, 152, 192, 240, 304, 384, 480, 600, 752, 944, 1184, 1480, 1856, 2320, 2904, 3632, 4544, 5680, 7104, 8880, 
                11104, 13880, 17352, 21696, 27120, 33904, 42384, 52984, 66232, 82792, 103496, 129376, 161720, 202152, 252696, 
                315872, 394840, 524288, 655360, 819200, 1024000, 1280000, 1600000, 2000000, 2500000, 3125000, 3906250, 
                ]

def _cal_total_workingset_size(trace_reader, window=300, consider_ttl=True, slab_sizes=None): 
  """ calculate how working set size change over time 
  """
  metadata_name = "ttl_w{}_{}{}_{}.pickle".format(window, consider_ttl, "_slab" if slab_sizes is not None else "", trace_reader.trace_path.split("/")[-1])

  loaded = load_metadata(metadata_name)
  if loaded is not None:
    return loaded

  ttl_obj = defaultdict(list)       # the objects that expire at ttl 
  workingset = {}     # obj -> size 
  workingset_size = 0 
  workingset_size_list = []
  sz_to_slab_mapping = {}
  start_ts, current_ts, last_window_ts = -1, 0, 0
  for req in trace_reader: 
    current_ts = req.real_time
    if start_ts == -1:
      start_ts = req.real_time
    if req.op == "set" or req.op == "add":
      if req.obj_id not in workingset:
        sz = req.obj_size 
        # sz = 1 
        if slab_sizes is not None: 
          # find the slab this object will use
          if sz not in sz_to_slab_mapping:
            sz_slab = slab_sizes[bisect.bisect_right(slab_sizes, sz)]
            sz_to_slab_mapping[sz] = sz_slab
            sz = sz_slab
          else: 
            sz = sz_to_slab_mapping[sz]

        workingset_size += sz 
        workingset[req.obj_id] = sz
        if consider_ttl and req.ttl != 0: 
          ttl_obj[current_ts+req.ttl].append(req.obj_id)
    if consider_ttl and current_ts in ttl_obj:
      for obj in ttl_obj[current_ts]:
        workingset_size -= workingset[obj]
        del workingset[obj]
      del ttl_obj[current_ts]
    if (req.real_time - start_ts) % window == 0 and req.real_time != last_window_ts:
      workingset_size_list.append(workingset_size)
      # print("{} append {}".format(req.real_time, workingset_size))
      last_window_ts = req.real_time

  save_metadata(workingset_size_list, metadata_name)
  trace_reader.reset()
  return workingset_size_list 


def plot_total_workingset_size(trace_reader, window, consider_ttl=True, slab_sizes=None): 
  figname = "{}/{}_{}_workingset".format(FIG_DIR, trace_reader.trace_path.split("/")[-1], window)
  if consider_ttl:
    figname = "{}_ttl".format(figname)
  if slab_sizes is not None and slab_sizes is not False:
    figname = "{}_slab".format(figname)
  if slab_sizes is True:
    slab_sizes = SLAB_SIZES

  n_color = 2
  if slab_sizes:
    n_color = 4
  plt.set_n_colors(n_color)
  ret_dict = {}
  workingset_size_list = _cal_total_workingset_size(trace_reader, window, False, slab_sizes=None)
  plt.plot([i*window/3600 for i in range(len(workingset_size_list))], 
            [sz/MB for sz in workingset_size_list], nomarker=True, label="no-ttl")
  ret_dict["no-ttl"] = workingset_size_list[-1]

  if consider_ttl:
    workingset_size_list = _cal_total_workingset_size(trace_reader, window, True, slab_sizes=None)
    plt.plot([i*window/3600 for i in range(len(workingset_size_list))], 
              [sz/MB for sz in workingset_size_list], nomarker=True, label="ttl")
    ret_dict["ttl"] = workingset_size_list[-1]

  if slab_sizes:
    workingset_size_list = _cal_total_workingset_size(trace_reader, window, False, slab_sizes=slab_sizes)
    plt.plot([i*window/3600 for i in range(len(workingset_size_list))], 
              [sz/MB for sz in workingset_size_list], nomarker=True, label="no-ttl-slab")
    ret_dict["no-ttl-slab"] = workingset_size_list[-1]

    workingset_size_list = _cal_total_workingset_size(trace_reader, window, True, slab_sizes=slab_sizes)
    plt.plot([i*window/3600 for i in range(len(workingset_size_list))], 
              [sz/MB for sz in workingset_size_list], nomarker=True, label="ttl-slab")
    ret_dict["ttl-slab"] = workingset_size_list[-1]

  if "ttl" in ret_dict and ret_dict["no-ttl"]/ret_dict["ttl"] > 100:
    plt.yscale("log")

  plt.xlabel("Time (hour)")
  plt.ylabel("Working set size (MB)")
  # plt.ylabel("Working set size (# million Obj)")
  plt.legend()
  plt.grid(linestyle="--")
  plt.savefig(figname, no_save_plot_data=True)
  plt.clf()
  return ret_dict


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  ap.add_argument("--window", type=int, default=300, help="window size")
  p = ap.parse_args()

  reader = TwrShortBinTraceReader(p.trace)

  plot_total_workingset_size(reader, p.window)





