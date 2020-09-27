

import libMC
import os
from pprint import pprint

MB = 1024*1024 
GB = 1024*1024*1024 

def f1():
  reader_params = {"trace_path": "trace.vscsi", "trace_type": "v", "obj_id_type": "l", }
  cache_sizes = [10*MB, 100*MB, 1000*MB]
  lru = libMC.get_miss_ratio_curve(reader_params, algorithm="LRU", cache_params={"default_ttl": 0}, cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  pprint(lru)
  fifo = libMC.get_miss_ratio_curve(reader_params, algorithm="FIFO", cache_params={"default_ttl": 0}, cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  pprint(fifo)

  lru = libMC.get_miss_ratio_curve(reader_params, algorithm="LRU", cache_params={"default_ttl": 30}, cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  pprint(lru)
  fifo = libMC.get_miss_ratio_curve(reader_params, algorithm="FIFO", cache_params={"default_ttl": 30}, cache_sizes=cache_sizes, warmup_perc=0, num_of_threads=os.cpu_count())
  pprint(fifo)

def f2():
  reader_params = {"trace_path": "trace.vscsi", "trace_type": "v", "obj_id_type": "l", }
  # dist = libMC.get_stack_dist(reader_params)
  # dist = libMC.get_future_stack_dist(reader_params)
  # dist = libMC.get_last_access_dist(reader_params)
  # dist = libMC.get_next_access_dist(reader_params)
  # dist = libMC.get_stack_byte(reader_params)
  # dist = libMC.get_reuse_time(reader_params)

  dist_cnt = libMC.get_last_access_dist_cnt(reader_params, log_base=1.08); 

  # dist_cnt = dist
  print(dist_cnt.shape, dist_cnt)
  # print(dist[200:240])



if __name__ == "__main__":
  f1()



