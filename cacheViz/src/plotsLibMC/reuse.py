

import libMC
import os,sys
import numpy as np
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utilsTwr.common import *


def f2():
  reader_params = {"trace_path": os.path.expanduser("~/twr.sbin"), "trace_type": "t", "obj_id_type": "l", }
  # reader_params = {"trace_path": os.path.expanduser("../../libMimircache/libMimircache/data/trace.vscsi"), "trace_type": "v", "obj_id_type": "l", }
  reader_params = {"trace_path": os.path.expanduser("~/akamai.bucket100.bin.short0"), "trace_type": "b", "obj_id_type": "l", "fmt": "III", "real_time_field": 1, "obj_id_field": 2, "obj_size_field": 3}
  stack_dist = libMC.get_stack_dist(reader_params)
  # dist = libMC.get_future_stack_dist(reader_params)
  dist = libMC.get_last_access_dist(reader_params)


  # dist = libMC.get_next_access_dist(reader_params)
  # dist = libMC.get_stack_byte(reader_params)
  # reuse_time = libMC.get_reuse_time(reader_params)




  # print(dist.shape, dist)
  # print(dist[200:240])

  # print(stack_dist[2016:2040])
  # print(dist[2016:2040])

  r = (stack_dist[stack_dist!=-1]+1)/(dist[dist!=-1]+1)
  print(r)
  print(np.mean(r))


f2() 