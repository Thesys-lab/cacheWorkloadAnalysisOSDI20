

import os, sys 
import libMC 
import numpy as np 
import matplotlib 
import matplotlib.pyplot as plt 
import matplotlib.ticker as ticker



def draw_heatmap(plot_array, xlabel, ylabel, filename="heatmap.png", **kwargs):
  imshow_kwargs = kwargs.get("imshow_kwargs", {})
  if "cmap" not in imshow_kwargs:
    imshow_kwargs["cmap"] = plt.cm.jet
  else:
    imshow_kwargs["cmap"] = plt.get_cmap(imshow_kwargs["cmap"])
  imshow_kwargs["cmap"].set_bad(color='white', alpha=1.)

  img = plt.imshow(plot_array, interpolation='nearest', origin='lower',
           aspect='auto', **imshow_kwargs)

  cb = plt.colorbar(img)
  plt.xlabel(xlabel)
  plt.ylabel(ylabel)


def f1():
  log_base = 1.08
  # reader_params = {"trace_path": "trace.vscsi", "trace_type": "v", "obj_id_type": "l", }
  # reader_params = {"trace_path": "/home/jason/control_tower_probe_cache.sbin", "trace_type": "t", "obj_id_type": "l", }
  reader_params = {"trace_path": os.path.expanduser("~/b.sbin"), "trace_type": "t", "obj_id_type": "l", }
  filename=reader_params["trace_path"].split("/")[-1]+"_rt.png"

  # plot_data = libMC.get_stack_dist_heatmap(reader_params, 300, log_base)
  # plot_data = libMC.get_last_access_dist_heatmap(reader_params, 300, log_base)
  plot_data = libMC.get_reuse_time_heatmap(reader_params, 300, log_base)
  print(plot_data[plot_data>1])
  plot_data[plot_data<1e-8] = np.nan
  draw_heatmap(plot_data, xlabel="Time (hour)", ylabel="Stack distance")
  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(x * 300/3600)))
  # plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(x)))
  plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: '{:.0f}'.format(log_base ** (x+0)-1)))
  plt.savefig(filename)
  plt.clf()


if __name__ == "__main__":
  f1()


