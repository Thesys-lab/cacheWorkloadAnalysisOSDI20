

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import numpy as np
import subprocess
import libMC


def _run_cache(reader_params, algorithm, cache_sizes, cache_params=None, warmup_reader_params=None, warmup_perc=0, num_of_threads=-1):
  if num_of_threads == -1:
    num_of_threads = os.cpu_count()
  if cache_params is None: 
    cache_params = {"default_ttl": 0}
  metadata_file = "eviction_{}_{}_ttl{}.pickle".format(reader_params["trace_path"].split("/")[-1], algorithm, cache_params.get("default_ttl", 0))
  result = load_metadata(metadata_file)

  if algorithm == "slabObjLRU-automove":
    algorithm = "slabObjLRU"
    cache_params["slab_move_strategy"] = 1

  if result is None:
    if warmup_reader_params is None:
      result = libMC.get_miss_ratio_curve(reader_params, algorithm=algorithm, cache_params=cache_params, cache_sizes=cache_sizes, 
                                          warmup_perc=warmup_perc, num_of_threads=num_of_threads)
    else:
      result = libMC.get_miss_ratio_curve(reader_params, warmup_reader_params=warmup_reader_params, algorithm=algorithm, 
                                          cache_params=cache_params, cache_sizes=cache_sizes, 
                                          warmup_perc=warmup_perc, num_of_threads=num_of_threads)
    save_metadata(result, metadata_file)

  return result 


def _plot_eviction_algo(cache_sizes, cache_params, warmup_reader_params, eval_reader_params, num_of_threads):
  plt.set_n_colors(5)
  miss_ratio_dict = {}
  algorithms = ("LRU", "FIFO", "slabLRU", "slabObjLRU")
  for algorithm in algorithms:
    result = _run_cache(eval_reader_params, algorithm, cache_sizes, cache_params, warmup_reader_params, num_of_threads=num_of_threads)
    miss_ratio = result["miss_cnt"]/result["req_cnt"] 
    plt.plot(cache_sizes, miss_ratio, linestyle="solid", linewidth=4, label=algorithm.replace("slabObjLRU", "Memcached-LRU"))
    miss_ratio_dict[algorithm] = miss_ratio
    print("{} finishes".format(algorithm))


def run_eviction_algo(trace_name, max_mem_GB, base_path, num_of_threads=-1):
  """ run the available cache replace algorithms """
  # xticks = [100*MB, 200*MB, 500*MB, 1000*MB, 2*GB, 3*GB, 4*GB, 5*GB, 8*GB, 10*GB, 12*GB, 16*GB]

  cache_sizes = list(np.logspace(26, np.log2(max_mem_GB*GB), num=128, base=2.0).astype(int))
  figname = "fig/{}_MRC".format(trace_name)

  warmup_reader_params = {"trace_path": "{}/{}_cache.0.warmup.sbin".format(base_path, trace_name), "trace_type": "t", "obj_id_type": "l", }
  eval_reader_params = {"trace_path": "{}/{}_cache.0.eval.sbin".format(base_path, trace_name), "trace_type": "t", "obj_id_type": "l", }
  if os.path.getsize(warmup_reader_params["trace_path"]) == 0:
    logging.warn("warmup trace does not exist {}, now set warmup reader to None".format(warmup_reader_params["trace_path"]))
    warmup_reader_params = None
  else:
    logging.info("warmup reader {} requests".format(os.path.getsize(warmup_reader_params["trace_path"])//20))

  ttl = {"gizmoduck_lru": 12*3600, "timelines_real_time_aggregates": 48*3600, "livepipeline": 3600, "simclusters_v2_entity_cluster_scores": 8*3600, "media_metadata":967400, "timelines_ranked_tweet": 980, "graph_feature_service": 8*3600, "geouser": 3600, "simclusters_core": 24*3600, "simclusters_core_esc": 24*3600, "limiter_feature_med": 24*3600, "expandodo": 24*3600, "pinkfloyd": 2*3600, "blender_adaptive": 24*3600, "taxi_v3_prod": 24*3600 , "timelines_impressionstore": 24*3600, "timelines_follow_socialproof": 24*3600, "content_recommender_core_svcs": 2*3600, "ibis_api": 432000, "ibis_dedup": 3*3600, "search_roots": 2*3600, "observability": 3600, "search_roots": 1200, "wtf_req": 4*3600, "control_tower_probe": 1500}
  cache_params = {"default_ttl": ttl[trace_name]} 
  cache_params = {"default_ttl": 0} 
  _plot_eviction_algo(cache_sizes, cache_params, warmup_reader_params, eval_reader_params, num_of_threads)

  plt.xscale("log")
  plt.xlabel("Cache size (MB)")
  plt.ylabel("Miss ratio")

  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(convert_size_to_str))
  plt.legend(ncol=2, bbox_to_anchor=(1, 1.28))
  plt.grid(linestyle="--")
  plt.savefig(figname)
  plt.clf()  


def split_warmup_eval(cache_name, base_path, shard_idx=0):
  """ this is used to generate the warmup and evaluation trace
  it contains hard coded time and not usable on other trace
  """ 

  ttl = {"gizmoduck_lru": 12*3600, "timelines_real_time_aggregates": 48*3600, "livepipeline": 3600, "simclusters_v2_entity_cluster_scores": 8*3600, "media_metadata":967400, "timelines_ranked_tweet": 980, "graph_feature_service": 8*3600, "geouser": 3600, "simclusters_core": 24*3600, "simclusters_core_esc": 24*3600, "limiter_feature_med": 24*3600, "expandodo": 24*3600, "pinkfloyd": 2*3600, "blender_adaptive": 24*3600, "taxi_v3_prod": 24*3600 , "timelines_impressionstore": 24*3600, "timelines_follow_socialproof": 24*3600, "content_recommender_core_svcs": 2*3600, "ibis_api": 432000, "ibis_dedup": 3*3600, "search_roots": 2*3600, "observability": 3600, "search_roots": 1200, "wtf_req": 4*3600, "control_tower_probe": 1500}
  path_prefix = "{}/{}.{}".format(base_path, cache_name, shard_idx)
  # we use either the mean TTL or 4.4 days as warmup time 
  # if we have TTL of the trace (this is the common case), we take TTL time of the trace for warmup 
  # otherwise we took 4.4 days 
  warmup_end_ts = 1585785600-87600      # Wed 12AM     4.4 days warmup 
  if cache_name[:-6] in ttl:
    warmup_end_ts = 1585353600 + ttl[cache_name[:-6]]      # Sat 12AM + ttl 
  eval_end_ts = warmup_end_ts + 87600
  p = subprocess.run("./CPPConverter -f 2 -i {}.sbin -w {}.warmup.sbin -e {}.eval.sbin -a {} -b {}".format(path_prefix, path_prefix, path_prefix, warmup_end_ts, eval_end_ts), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)



if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace_name", type=str, required=True, help="trace name")
  ap.add_argument("--cache_size", type=int, required=True, help="max cache size in GB")
  ap.add_argument("--base_path", type=str,  required=True, help="base path")
  ap.add_argument("--num_of_threads", type=int, default=-1, help="the number of threads")
  p = ap.parse_args()

  run_eviction_algo(p.trace_name, p.cache_size, p.base_path, p.num_of_threads)


