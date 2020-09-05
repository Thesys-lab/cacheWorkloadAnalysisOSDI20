

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import numpy as np
import subprocess

try:
  import libMC
except Exception as e:
  print(e) 


def dist_plot(trace_path):
  reader_params = {"trace_path": trace_path, "trace_type": "t", "obj_id_type": "l", }
  plot_dist_cdf(reader_params, "last_access_dist", )




def eviction_algo(trace_name, trace_name, max_mem_GB ):
  
  max_mem_GB, ttl = int(max_mem_GB), int(ttl)
  cache_sizes = list(np.logspace(26, np.log2(max_mem_GB*GB*2), num=128, base=2.0).astype(int))

  BASE_PATH = "/mnt/nfs/warmupEvalSplit/"
  warmup_reader_params = {"trace_path": "{}/{}_cache.0.warmup.sbin".format(BASE_PATH, trace_name), "trace_type": "t", "obj_id_type": "l", }
  eval_reader_params = {"trace_path": "{}/{}_cache.0.eval.sbin".format(BASE_PATH, trace_name), "trace_type": "t", "obj_id_type": "l", }
  if os.path.getsize(warmup_reader_params["trace_path"]) == 0:
    print("set {} to None".format(warmup_reader_params["trace_path"]))
    warmup_reader_params = None
  else:
    print("warmup {}".format(os.path.getsize(warmup_reader_params["trace_path"])))

  cache_params = {"default_ttl": 0}
  _plot_eviction_algo(trace_name, eval_reader_params, cache_sizes, cache_params, warmup_reader_params, num_of_threads)
  return True


def plot_eviction_algo(trace_name, eval_reader_params, cache_sizes, cache_params, warmup_reader_params, num_of_threads):
  all_xticks = [100*MB, 200*MB, 500*MB, 1000*MB, 2*GB, 3*GB, 4*GB, 5*GB, 8*GB, 10*GB, 12*GB, 16*GB]
  figname = "figEviction/{}_MRC".format(trace_name)
  if cache_params.get("default_ttl", 0) == 0:
    figname += "_nottl"
  else:
    figname += "_ttl{}".format(cache_params.get("default_ttl"))

  plt.set_n_colors(7)
  miss_ratio_dict = {}
  if cache_params.get("default_ttl", 0) == 0:
    algorithms = ("LRU", "FIFO", "slabLRU", "slabLRC", "slabObjLRU", "slabObjLRU-automove")
  else:
    algorithms = ("LRU", "FIFO", "slabLRU", "slabLRC", "slabObjLRU", "TTL_FIFO", "slabObjLRU-automove")
  for algorithm in algorithms:
    result = run_cache(eval_reader_params, algorithm, cache_sizes, cache_params, warmup_reader_params, num_of_threads=num_of_threads)
    miss_ratio = result["miss_cnt"]/result["req_cnt"] 
    plt.plot(cache_sizes, miss_ratio, linestyle="solid", linewidth=1.6, label=algorithm)
    miss_ratio_dict[algorithm] = miss_ratio
    print(algorithm)


  lru_miss_ratio = miss_ratio_dict["LRU"]
  pos = -1
  # while -pos < len(lru_miss_ratio) and lru_miss_ratio[pos] < lru_miss_ratio[-1]*1.08:
  #   pos -= 1
  # xticks = [i for i in all_xticks if i < cache_sizes[pos]]

  # plt.xlim((0, cache_sizes[pos]))
  plt.xscale("log")
  plt.xlabel("Cache size (MB)")
  plt.ylabel("Miss ratio")

  # plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(lambda x: "{:.2f}".format(x/1000/1000)))
  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(convert_size_to_str))
  # plt.xticks(xticks)
  plt.legend()
  plt.savefig(figname)
  plt.clf()  


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  ap.add_argument("--type", type=str, help="trace path")
  p = ap.parse_args()

  if p.type == "dist":
    plot_size_dist_heatmap(p.trace) 
  elif p.type == "mrc": 

