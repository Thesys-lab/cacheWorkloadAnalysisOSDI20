""" 
  TwrBinTraceReader format:   unix_ts(uint32), obj_id(uint64), key-size(uint16), value-size(uint32), client(uint16), 
  op(uint16 1:get, 2:gets, 3:set, 5:add, 6: replace, 7: append, 8: prepend, 9: cas, 10: delete, 11:incr, 12:decr), 
  namespace(uint64), ttl(uint32)
  trace_long_format_struct_str = "<IQHIHHQI"


  TwrShortBinReader format: 
    real_time, obj_id, key and value size (first 12 bits key size, last 20 bits value size), op and ttl (first 8 bit op, last 24 bit ttl, ttl_max=8000000)
    trace_short_format_struct_str = "<IQII"

  Jason <peter.waynechina@gmail.com> 
"""

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import struct
import collections
from core.req import Req
from core.traceReader import TraceReader


class TwrBinTraceReader(TraceReader):
  def __init__(self, trace_path, *args, **kwargs):
    TraceReader.__init__(self, trace_path, "binary", real_time_field=1, obj_id_field=2, key_size_field=3, value_size_field=4, 
      op_field=6, ttl_field=8, **kwargs)
    self.struct = struct.Struct("<IQHIHHQI")
    self.struct_size = self.struct.size 
    self.client_field = 5
    self.namespace_field = 7
    self.per_struct_size_overhead = 60
    # self.op_mapping = ("get", "gets", "set", "NA", "add", "replace", "append", "prepend", "cas", "delete", "incr", "decr")
    self.op_mapping = ("get", "gets", "set", "add", "cas", "replace", "append", "prepend", "delete", "incr", "decr")


  def read_one_req(self):
    TraceReader.read_one_req(self)
    bin_data = self.trace_file.read(self.struct_size)
    if not bin_data:
      return None
    item = self.struct.unpack(bin_data)
    key_size = int(item[self.key_size_field-1]) 
    value_size = int(item[self.value_size_field-1]) 
    obj_size = key_size + value_size
    if value_size == 0:
      obj_size = 0
    op = self.op_mapping[int(item[self.op_field-1])-1]
    ttl = int(item[self.ttl_field-1])
    if isinstance(self.req, tuple):
      req = Req(logical_time=self.n_read_req, real_time=int(item[self.real_time_field-1]), 
                obj_id=int(item[self.obj_id_field-1]), op = op, ttl=ttl, key_size=key_size, value_size=value_size,
                obj_size=obj_size, req_size=obj_size, cnt=1) 
      self.req = req
    else: 
      self.req.logical_time, self.req.real_time = self.n_read_req, int(item[self.real_time_field-1]) 
      self.req.obj_id, self.req.op, self.req.ttl, self.req.cnt = int(item[self.obj_id_field-1]), op, ttl, 1
      self.req.key_size, self.req.value_size, self.req.obj_size, self.req.req_size = key_size, value_size, obj_size, obj_size 
    return self.req

  def __len__(self):
    self.n_req = os.path.getsize(self.trace_path)//self.struct.size 
    assert self.n_req * self.struct.size == os.path.getsize(self.trace_path), "trace file size is not mulitple of req struct size"
    return self.n_req


# this is only for /disk/traces/allJobOneTaskLong/ on pm1, a one-week temporal sampled data 
class TwrShortBinTraceReaderOld(TraceReader):
  def __init__(self, trace_path, *args, **kwargs):
    TraceReader.__init__(self, trace_path, "binary", real_time_field=1, obj_id_field=2, obj_size_field=3)
    self.struct = struct.Struct("<IQII")
    self.struct_size = self.struct.size 
    self.per_struct_size_overhead = 60
    self.op_mapping = ("get", "gets", "set", "add", "cas", "replace", "append", "prepend", "delete", "incr", "decr")
    self.op_ttl_field = 4

  def read_one_req(self):
    TraceReader.read_one_req(self)
    try:
    # if 1:
      bin_data = self.trace_file.read(self.struct_size)
      if not bin_data:
        return None
      item = self.struct.unpack(bin_data)
      real_time = int(item[self.real_time_field-1])
      obj_id = int(item[self.obj_id_field-1])
      obj_size = int(item[self.obj_size_field-1])
      op_ttl = int(item[self.op_ttl_field-1])
      op = op_ttl & (0x0100-1)
      ttl = op_ttl >> 8
      if op -1 > 10:
        print("op {}".format(op-1))
      op = self.op_mapping[op-1]

      req = Req(logical_time=self.n_read_req, real_time=real_time, 
                obj_id=obj_id, op = op, ttl=ttl, 
                obj_size=obj_size, req_size=obj_size)
    except Exception as e:
      print("TwrShortBinTraceReader err: {}".format(e))
      self.n_read_req -= 1
      return self.read_one_req()
    return req


class TwrShortBinTraceReader(TraceReader):
  def __init__(self, trace_path, *args, **kwargs):
    TraceReader.__init__(self, trace_path, "binary", real_time_field=1, obj_id_field=2, **kwargs)
    self.struct = struct.Struct("<IQII")
    self.struct_size = self.struct.size 
    self.per_struct_size_overhead = 60
    self.op_mapping = ("get", "gets", "set", "add", "cas", "replace", "append", "prepend", "delete", "incr", "decr")
    self.kv_size_field = 3
    self.op_ttl_field = 4

  def read_one_req(self):
    # while True:
    TraceReader.read_one_req(self)
    bin_data = self.trace_file.read(self.struct_size)
    if not bin_data:
      return None
    item = self.struct.unpack(bin_data)
    real_time = int(item[self.real_time_field-1])
    obj_id = int(item[self.obj_id_field-1])
    # key and value size (first 12 bits is key size, last 20 bits is value size) 
    kv_size = int(item[self.kv_size_field-1])
    key_size, value_size = (kv_size >> 22) & (0x00000400-1), kv_size & (0x00400000 - 1) 
    obj_size = key_size + value_size
    if value_size == 0:
      obj_size = 0

    # op and ttl (first 8 bit op, last 24 bit ttl, ttl_max=8000000)
    op_ttl = int(item[self.op_ttl_field-1])
    op = (op_ttl >> 24) & (0x00000100-1)
    ttl = op_ttl & (0x01000000-1)
    op = self.op_mapping[op-1]

    if isinstance(self.req, tuple):
      req = Req(logical_time=self.n_read_req, real_time=real_time, 
                obj_id=obj_id, op = op, ttl=ttl, key_size=key_size, value_size=value_size,
                obj_size=obj_size, req_size=obj_size, cnt=1) 
      self.req = req
    else: 
      self.req.logical_time, self.req.real_time = self.n_read_req, real_time 
      self.req.obj_id, self.req.op, self.req.ttl, self.req.cnt = obj_id, op, ttl, 1
      self.req.key_size, self.req.value_size, self.req.obj_size, self.req.req_size = key_size, value_size, obj_size, obj_size 
    return self.req

if __name__ == "__main__":
  from collections import defaultdict
  reader = TwrShortBinTraceReader("/Users/junchengy/Downloads/log-twemcache.cmd.bin")
  obj_cnt_dict = defaultdict(int)
  ttl_cnt_dict = defaultdict(int)
  for n, req in enumerate(reader):
    if n < 8:
      print(req)
    obj_cnt_dict[req.obj_id] += req.cnt
    ttl_cnt_dict[req.ttl] += 1
  print(sorted(obj_cnt_dict.items(), key=lambda x:-x[1])[:20])
  print(ttl_cnt_dict)



