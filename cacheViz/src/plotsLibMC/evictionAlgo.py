
import os,sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
from functools import partial
import libMC
from utilsTwr.common import *
import matplotlib.ticker as ticker


def convert_size_to_str(sz, pos=None):
  if sz>TiB:
    return "{:.0f} TiB".format(sz/TiB)
  elif sz>GiB: 
    return "{:.0f} GiB".format(sz/GiB)
  elif sz>MiB: 
    return "{:.0f} MiB".format(sz/MiB)
  elif sz>KiB: 
    return "{:.0f} KiB".format(sz/KiB)
  else:
    return "{} B".format(sz)

def f1():
  trace_path = os.path.expanduser("~/twr.sbin")
  cache_sizes = list([10*MiB, 100*MiB, 1000*MiB])
  cache_sizes = list(range(1*MiB, 200*MiB, 10*MiB))
  # reader_params = {"trace_path": "../../trace.vscsi", "trace_type": "v", "obj_id_type": "l", }
  reader_params = {"trace_path": trace_path, "trace_type": "t", "obj_id_type": "l", }
  lru         = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "LRU"},       cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  fifo        = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "FIFO"},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slabLRC     = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "slabLRC"},   cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slabLRU     = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "slabLRU"},   cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slabObjLRU  = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "slabObjLRU"},cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # pprint(lru) 
  # pprint(fifo)
  # pprint(slabLRC)

  lru_miss_ratio = lru["miss_cnt"]/lru["req_cnt"]
  fifo_miss_ratio = fifo["miss_cnt"]/fifo["req_cnt"]
  slabLRC_miss_ratio = slabLRC["miss_cnt"]/slabLRC["req_cnt"]
  slabLRU_miss_ratio = slabLRU["miss_cnt"]/slabLRU["req_cnt"]
  slabObjLRU_miss_ratio = slabObjLRU["miss_cnt"]/slabObjLRU["req_cnt"]

  plt.plot(cache_sizes, lru_miss_ratio, label="LRU")
  plt.plot(cache_sizes, fifo_miss_ratio, label="FIFO")
  plt.plot(cache_sizes, slabLRC_miss_ratio, label="slabLRC")
  plt.plot(cache_sizes, slabLRU_miss_ratio, label="slabLRU")
  plt.plot(cache_sizes, slabObjLRU_miss_ratio, label="slabObjLRU")
  plt.xlabel("Cache size (MB)")
  plt.ylabel("Miss ratio")

  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(convert_size_to_str))
  plt.xticks([100*MiB, 1000*MiB])
  plt.legend()
  plt.savefig("{}_MRC".format(trace_path.split("/")[-1]))
  plt.clf()


def f2(ttl=0):
  import numpy as np
  plt.set_n_colors(5)
  trace_path = os.path.expanduser("~/twr.sbin")
  trace_path_warmup = os.path.expanduser("~/data/twr/warmupEvalSplit/devices_cache.0.warmup.sbin")
  trace_path_eval = os.path.expanduser("~/data/twr/warmupEvalSplit/devices_cache.0.eval.sbin")
  trace_path_warmup = os.path.expanduser("~/data/twr/warmupEvalSplit/observability_cache.0.warmup.sbin")
  trace_path_eval = os.path.expanduser("~/data/twr/warmupEvalSplit/observability_cache.0.eval.sbin")
  cache_sizes = [1*MiB, 2*MiB, 4*MiB, 8*MiB, 16*MB, 32*MB, 64*MB, 128*MB, 256*MB, 512*MB, 1024*MB, 2*GB]
  cache_sizes = list(np.logspace(24, np.log2(8*GB), num=4, base=2.0).astype(int))
  # cache_sizes = [32*MB, 128*MB, 512*MB, 1024*MB]
  cache_sizes = [128*MB, 1024*MB]
  eval_reader_params = {"trace_path": trace_path_eval, "trace_type": "t", "obj_id_type": "l"}
  warmup_reader_params = {"trace_path": trace_path_warmup, "trace_type": "t", "obj_id_type": "l"}
  # lru         = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="LRU", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl},       cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # fifo        = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="FIFO", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # slabLRC        = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="slabLRC", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl, "slab_size": 2*1024*1024},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # slabLRU        = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="slabLRU", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # slabObjLRU        = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="slabObjLRU", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl, "slab_move_strategy": 1},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=1)
  TTL_FIFO        = libMC.get_miss_ratio_curve(eval_reader_params, algorithm="TTL_FIFO", warmup_reader_params=warmup_reader_params, cache_params={"default_ttl": ttl, "slab_move_strategy": 1},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=1)

  lru_miss_ratio = lru["miss_cnt"]/lru["req_cnt"]
  fifo_miss_ratio = fifo["miss_cnt"]/fifo["req_cnt"]
  slabLRC_miss_ratio = slabLRC["miss_cnt"]/slabLRC["req_cnt"]
  slabLRU_miss_ratio = slabLRU["miss_cnt"]/slabLRU["req_cnt"]
  slabObjLRU_miss_ratio = slabObjLRU["miss_cnt"]/slabObjLRU["req_cnt"]

  plt.plot(cache_sizes, lru_miss_ratio, label="LRU")
  plt.plot(cache_sizes, fifo_miss_ratio, label="FIFO")
  plt.plot(cache_sizes, slabLRC_miss_ratio, label="slabLRC")
  plt.plot(cache_sizes, slabLRU_miss_ratio, label="slabLRU")
  plt.plot(cache_sizes, slabObjLRU_miss_ratio, label="slabObjLRU")
  plt.xlabel("Cache size (MB)")
  plt.ylabel("Miss ratio")

  plt.gca().xaxis.set_major_formatter(ticker.FuncFormatter(convert_size_to_str))
  # plt.xticks([100*MiB, 1000*MiB])
  plt.legend()
  plt.savefig("{}_MRC_ttl{}".format(trace_path_eval.split("/")[-1], ttl))
  plt.clf()


def f4():
  trace_path = "../../libMimircache/libMimircache/data/trace.vscsi"
  cache_sizes = list(range(128*MiB, 16*GB, 128*MiB))
  reader_params = {"trace_path": trace_path, "trace_type": "v", "obj_id_type": "l", }
  # reader_params = {"trace_path": trace_path, "trace_type": "b", "obj_id_type": "l", "fmt": "IIII", "real_time_field": 1, "obj_id_field": 2, "obj_size_field": 3}
  # reader_params = {"trace_path": trace_path, "trace_type": "p", "obj_id_type": "l", }
  # lru         = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "LRU"},       cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  # fifo        = libMC.get_miss_ratio_curve(reader_params, {"algorithm": "FIFO"},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())

  lru         = libMC.get_miss_ratio_curve(reader_params, algorithm="LRU", cache_params={"default_ttl": 0},       cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  fifo        = libMC.get_miss_ratio_curve(reader_params, algorithm="FIFO", cache_params={"default_ttl": 0},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slablrc     = libMC.get_miss_ratio_curve(reader_params, algorithm="slabLRC", cache_params={"default_ttl": 0},       cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slablru     = libMC.get_miss_ratio_curve(reader_params, algorithm="slabLRU", cache_params={"default_ttl": 0},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  slabobjlru  = libMC.get_miss_ratio_curve(reader_params, algorithm="slabObjLRU", cache_params={"default_ttl": 0},      cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  pprint(lru["miss_cnt"])
  pprint(fifo["miss_cnt"])
  pprint(slablrc["miss_cnt"])
  pprint(slablru["miss_cnt"])
  pprint(slabobjlru["miss_cnt"])

  
if __name__ == "__main__":
  # f2(0)
  f2(148)






