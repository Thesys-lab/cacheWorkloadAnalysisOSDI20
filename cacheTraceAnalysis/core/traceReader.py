
try: 
  from .req import Req
except:
  # import os, sys 
  # sys.path.append(os.path.dirname(os.path.abspath(__file__)))
  # print(sys.path[-1])
  from req import Req
import os
import csv
import struct

try:
  from hdfs import InsecureClient
except:
  pass


MAX_TXT_TRACE_LINE_LEN = 1024

class TraceReader:
  def __init__(self, trace_path, trace_type, real_time_field=-1, obj_id_field=-1, obj_size_field=-1,
         cnt_field=-1, op_field=-1, **kwargs):
    self.trace_path = trace_path
    self.trace_type = "binary" if trace_type.lower() in ("binary", "bin", "b") else trace_type.lower()
    self.trace_file = None
    # binary trace only 
    self.struct = ""
    self.struct_size = -1

    self.n_req = 0
    self.n_read_req = 0
    self.real_time_field = real_time_field
    self.obj_id_field = obj_id_field
    self.obj_size_field = obj_size_field
    self.cnt_field = cnt_field
    self.op_field = op_field
    self.ttl_field = kwargs.pop("ttl_field", -1)
    self.key_size_field = kwargs.pop("key_size_field", -1)
    self.value_size_field = kwargs.pop("value_size_field", -1)
    self.req_selector = kwargs.pop("req_selector", None)
    self.req = Req(0, None)

    assert len(kwargs) == 0, "kwargs not empty {}".format(kwargs)
    self._open_trace()

  def _open_trace(self):
    self.trace_file = open(self.trace_path, "rb")
    # if self.trace_type == "binary":
    #   self.trace_file = open(self.trace_path, "rb")
    # else:
    #   self.trace_file = open(self.trace_path, )
    self.n_read_req = 0

  def __enter__(self):
    self._open_trace()
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    self.trace_file.close()
    self.trace_file = None

  def __len__(self):
    if self.trace_type == "binary":
      self.n_req = os.path.getsize(self.trace_path)//self.struct.size 
      assert self.n_req * self.struct.size == os.path.getsize(self.trace_path), "trace file size is not mulitple of req struct size"

    if self.n_req == 0:
      while self.read_one_req():
        self.n_req += 1
      self.reset()
    return self.n_req

  def __iter__(self):
    return self

  def __next__(self):
    req = self.read_one_req()
    if req:
      return req
    else:
      raise StopIteration

  def __exit__(self):
    if self.trace_file is not None:
      self.trace_file.close()

  def reset(self): 
    self.trace_file.seek(0, 0)

  def read_next_req(self):
    return self.read_one_req()

  def read_prev_req(self): 
    if self.trace_type == "binary": 
      self.trace_file.seek(-self.struct.size, 1)
      return self.read_one_req()
    else: 
      raise RuntimeError("non-binary trace does not support this operation efficiently")

  def jump_to_end(self):
    self.trace_file.seek(0, 2)
    # if self.trace_type == "binary": 
    #   self.trace_file.seek(0, 2)
    # else: 
    #   raise RuntimeError("non-binary trace does not support this operation efficiently")

  def read_first_req(self):
    cur_pos = self.trace_file.tell()
    self.seek(0, 0)
    req = self.read_one_req()
    self.trace_file.seek(cur_pos, 0)
    return req
    
  def read_last_req(self):
    cur_pos = self.trace_file.tell()
    if self.trace_type == "binary":
      self.trace_file.seek(-self.struct_size, 2)
    else:
      self.trace_file.seek(-MAX_TXT_TRACE_LINE_LEN, 2)
    req = self.read_one_req()
    while req:
      last_req = req 
      req = self.read_one_req()

    self.trace_file.seek(cur_pos, 0)
    return last_req

  ## abstract method 
  def read_one_req(self):
    if self.trace_file is None:
      self._open_trace()
    self.n_read_req += 1
    return None




