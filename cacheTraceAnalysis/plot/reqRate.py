""" plot request rate

"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *

def _cal_req_rate(trace_reader, window):

  metadata_name = "reqRateList_w{}_{}.pickle".format(window, trace_reader.trace_path.split("/")[-1])
  loaded = load_metadata(metadata_name)
  if loaded is not None:
    return loaded

  start_ts = -1
  req_cnt_list, obj_cnt_list, req_Gbps_list, obj_Gbps_list = [], [], [], []
  req_cnt, obj_cnt, req_byte, obj_byte = 0, 0, 0, 0

  seen_obj = set()
  for req in trace_reader:
    if start_ts == -1:
      start_ts = req.real_time

    req_cnt += req.cnt
    req_byte += req.req_size
    if req.obj_id not in seen_obj:
      obj_cnt += 1
      obj_byte += req.req_size 
      seen_obj.add(req.obj_id)

    if (req.real_time - start_ts)//window > len(req_cnt_list):
      req_cnt_list.append(req_cnt/window)
      obj_cnt_list.append(obj_cnt/window)
      req_Gbps_list.append(req_byte/GB/window*8)
      obj_Gbps_list.append(obj_byte/GB/window*8)
      req_cnt, obj_cnt, req_byte, obj_byte = 0, 0, 0, 0
      seen_obj.clear()

  trace_reader.reset()
  save_metadata((req_cnt_list, obj_cnt_list, req_Gbps_list, obj_Gbps_list), metadata_name)

  return req_cnt_list, obj_cnt_list, req_Gbps_list, obj_Gbps_list


def plot_req_rate(trace_reader, window, plot_type=("cnt", "byte")):
  COLOR = JPlot.get_color(2)
  req_cnt_list, obj_cnt_list, req_Gbps_list, obj_Gbps_list = _cal_req_rate(trace_reader, window)
  ret_dict = {
        "mean_req_cnt": sum(req_cnt_list)/len(req_cnt_list), 
        "mean_obj_cnt": sum(obj_cnt_list)/len(obj_cnt_list), 
        "mean_req_Gbps": sum(req_Gbps_list)/len(req_Gbps_list), 
        "mean_obj_Gbps": sum(obj_Gbps_list)/len(obj_Gbps_list), 
  }

  if "cnt" in plot_type or plot_type == "cnt":
    plt.plot([i*window/3600 for i in range(len(req_cnt_list))], [i/1000 for i in req_cnt_list], nomarker=True, label="request", color=next(COLOR), linewidth=1)
    plt.plot([i*window/3600 for i in range(len(obj_cnt_list))], [i/1000 for i in obj_cnt_list], nomarker=True, label="object", color=next(COLOR), linewidth=1)
    plt.xlabel("Time (Hour)")
    plt.ylabel("Request rate (K QPS)")
    plt.legend()
    plt.savefig("{}/{}_reqRateCnt_w{}.png".format(FIG_DIR, trace_reader.trace_path.split("/")[-1], window), no_save_plot_data=True)
    plt.clf()

  COLOR = JPlot.get_color(2)
  if "byte" in plot_type or plot_type == "byte":
    y1, y2, ylabel = req_Gbps_list, obj_Gbps_list, "Request rate (Gbps)"
    if sum(req_Gbps_list)/len(req_Gbps_list) < 1:
      y1 = [i*1024 for i in req_Gbps_list]
      y2 = [i*1024 for i in obj_Gbps_list]
      ylabel = "Request rate (Mbps)"

    plt.plot([i*window/3600 for i in range(len(req_Gbps_list))], y1, nomarker=True, color=next(COLOR), label="request", linewidth=1)
    plt.plot([i*window/3600 for i in range(len(obj_Gbps_list))], y2, nomarker=True, color=next(COLOR), label="object", linewidth=1)
    plt.xlabel("Time (Hour)")
    plt.ylabel(ylabel)
    plt.legend()
    plt.savefig("{}/{}_reqRateTraffic_w{}.png".format(FIG_DIR, trace_reader.trace_path.split("/")[-1], window), no_save_plot_data=True)
    plt.clf()
  return ret_dict


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  ap.add_argument("--type", type=str, default="cnt", help="plot type")
  ap.add_argument("--window", type=int, default=60, help="the size of window in sec")
  p = ap.parse_args()

  plot_req_rate(TwrShortBinTraceReader(p.trace), p.window, plot_type=(p.type, ))

