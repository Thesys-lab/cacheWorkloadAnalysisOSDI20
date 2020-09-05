""" plot size distribution over time in heatmap 

"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import copy
import numpy as np
import matplotlib.ticker as ticker
from matplotlib import colors


def cal_size_dist_over_time(trace_reader, window):
  """ 
  return two lists, the first list counts the number of requests of certain size, 
  the second list counts the nubmer of objects of certain size, 
  the element of each list is a defaultdict(int), which reqpresents the size distribution of the time window 
  """
      
  metadata_name = "sizeCntOverTime_w{}_{}.pickle".format(window, trace_reader.trace_path.split("/")[-1])
  loaded = load_metadata(metadata_name)
  if loaded is not None:
    return loaded

  seen_obj = set()
  seen_obj_size = {}
  sz_cnt_req, sz_cnt_obj = defaultdict(int), defaultdict(int)
  sz_cnt_req_list, sz_cnt_obj_list = [], []
  last_record_time = -1
  for req in trace_reader:
    if last_record_time == -1: 
      last_record_time = req.real_time
    if req.logical_time % 20000000 == 0:
      logging.debug("{} req".format(req.logical_time))

    if req.req_size == 0:
      continue 

    sz_cnt_req[req.req_size] += req.cnt
    if req.obj_id not in seen_obj: 
      sz_cnt_obj[req.req_size] += 1
      seen_obj.add(req.obj_id)
      seen_obj_size[req.obj_id] = req.req_size
    # else: 
    #     if seen_obj_size[req.obj_id] != req.req_size: 
    #         raise RuntimeError("size different - old size {} - new size {} for obj {}".format(seen_obj_size[req.obj_id], req.req_size, req.obj_id))

    if req.real_time != last_record_time and req.real_time % window == 0: 
      sz_cnt_req_list.append(copy.copy(sz_cnt_req))
      sz_cnt_obj_list.append(copy.copy(sz_cnt_obj))

      last_record_time = req.real_time
      seen_obj.clear()
      sz_cnt_req, sz_cnt_obj = defaultdict(int), defaultdict(int)

  trace_reader.reset()
  save_metadata((sz_cnt_req_list, sz_cnt_obj_list), metadata_name)
  return sz_cnt_req_list, sz_cnt_obj_list


def draw_heatmap(plot_array, filename="heatmap.png", **kwargs):
  imshow_kwargs = kwargs.get("imshow_kwargs", {})
  if "cmap" not in imshow_kwargs:
    imshow_kwargs["cmap"] = plt.cm.jet
  else:
    imshow_kwargs["cmap"] = plt.get_cmap(imshow_kwargs["cmap"])
  imshow_kwargs["cmap"].set_bad(color='white', alpha=1.)

  img = plt.imshow(plot_array, interpolation='nearest', origin='lower',
           aspect='auto', **imshow_kwargs)

  cb = plt.colorbar(img)


def cal_size_dist_heatmap(trace_reader, window, log_base=1.2):
  sz_cnt_req_list, sz_cnt_obj_list = cal_size_dist_over_time(trace_reader, window)
  max_sz = max([max([int(i) for i in sz_cnt_req.keys()]) for sz_cnt_req in sz_cnt_req_list])+1


  plot_data_req, plot_data_obj = [], []
  for sz_cnt_req, sz_cnt_obj in zip(sz_cnt_req_list, sz_cnt_obj_list): 
    # print(len(sz_cnt_req), len(sz_cnt_obj))
    req_cnt, obj_cnt = [0]*(int(math.log(max_sz, log_base)+1)), [0]*(int(math.log(max_sz, log_base)+1))
    for sz in sz_cnt_req.keys():
      if int(sz) > max_sz: 
        # pass
        print("max {} current {} {}".format(max_sz, sz, trace_reader.trace_path))
      bucket = int(math.log(int(sz), log_base))
      req_cnt[bucket] += int(sz_cnt_req[sz])
      try:
        obj_cnt[bucket] += int(sz_cnt_obj[sz])
      except Exception as e:
        # print("size {} not found in obj_cnt, this might because obj size change over time".format(sz))
        pass

    req_cnt_sum, obj_cnt_sum = sum(req_cnt), sum(obj_cnt)
    req_cnt_pdf = [i/req_cnt_sum for i in req_cnt]
    obj_cnt_pdf = [i/obj_cnt_sum for i in obj_cnt]

    plot_data_req.append(req_cnt_pdf)
    plot_data_obj.append(obj_cnt_pdf)

  plot_data_req = np.array(plot_data_req).T
  plot_data_obj = np.array(plot_data_obj).T

  # filter out the row with all 0
  plot_data_req_sum = np.sum(plot_data_req, axis=1)
  plot_data_obj_sum = np.sum(plot_data_obj, axis=1)

  for i in range(plot_data_req_sum.shape[0]):
    if plot_data_req_sum[i] != 0:
      skipped_idx_req = i
      break 
  plot_data_req = plot_data_req[i:, :]

  for i in range(plot_data_obj_sum.shape[0]):
    if plot_data_obj_sum[i] != 0:
      skipped_idx_obj = i
      break 
  plot_data_obj = plot_data_obj[i:, :]

  return skipped_idx_req, skipped_idx_obj, plot_data_req, plot_data_obj


def plot_size_dist_heatmap(trace_reader, window=300, log_base=1.2):
  figname = "{}/{}_sizeDistHeatmap".format(FIG_DIR, trace_reader.trace_path.split("/")[-1])

  skipped_idx_req, skipped_idx_obj, plot_data_req, plot_data_obj = cal_size_dist_heatmap(trace_reader, window, log_base=log_base)

  # plt.update_plot_style()
  draw_heatmap(plot_data_req) #, imshow_kwargs={"norm": colors.LogNorm()})
  plt.xlabel("Time (hour)")
  plt.ylabel("Request size (byte)")
  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(x * window/3600)))
  plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(log_base ** (x+1+skipped_idx_req))))
  plt.savefig(figname+"_req", no_save_plot_data=True)
  plt.clf()

  draw_heatmap(plot_data_obj) #, imshow_kwargs={"norm": colors.LogNorm()})
  plt.xlabel("Time (hour)")
  plt.ylabel("Request size (byte)")
  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(x * window/3600)))
  plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(log_base ** (x+1+skipped_idx_req))))
  plt.savefig(figname+"_obj", no_save_plot_data=True)
  plt.clf()


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  p = ap.parse_args()

  reader = TwrShortBinTraceReader(p.trace)

  plot_size_dist_heatmap(reader)
  