

import os,sys, collections, struct
sys.path.append("../../")
from utilsTwr.common import *
from traceUtils.twrTraceWriter import TwrBinTraceWriterHDFS
from traceReader.twrTraceReaderHDFS import TwrTraceReaderHDFS
from core.traceReaderHDFS import TraceReaderHDFS
from pywebhdfs.webhdfs import PyWebHdfsClient


Req = collections.namedtuple('Req', ["logical_time", "obj_id", "real_time", "obj_size", "req_size", 
    "key_size", "value_size", "req_range_start", "req_range_end", "cnt", "op", "ttl", "client_id", "namespace"])
Req.__new__.__defaults__ = (None, None, None, 1, 1, 0, 1, None, None, 1, None, None, None, None)
op_mapping = {"get": 1, "gets": 2, "set":3, "add": 4, "cas":5, "replace": 6, "append": 7, "prepend": 8, "delete": 9, "incr": 10, "decr":11}
mystruct = struct.Struct("<IHIBI")    # ts, key size, value size, op, ttl 


def _write_to_ofile(req, ofile):
  ofile.write(mystruct.pack(req.real_time, req.key_size, req.value_size, req.op, req.ttl))
  # print(req.obj_id)
  ofile.write(struct.pack("{}s".format(req.key_size), req.obj_id.encode()))


def buffer_req_to_guarantee_time_monotonic(req, req_buffer, ofile, last_write_ts, buffer_time=8, ):  
  req_buffer[req.real_time].append(req)
  if req.real_time - last_write_ts > buffer_time:
    for ts in range(last_write_ts+1, req.real_time - buffer_time+1):
      if ts in req_buffer:
        for req in req_buffer[ts]:
          _write_to_ofile(req, ofile)
        del req_buffer[ts]
    last_write_ts = req.real_time - buffer_time
  return last_write_ts




# this parse the log line and output in a binary format with following fields ts key_size value_size op ttl raw_obj_id 
# note that each req has a different length due to the variable-length raw_obj_id, we need to use key_size to determine how long to read  
# this is to be consumed by CPP converter 
# CPP converter is used to reduce memory footprint of obj_mapping 
def _parse_log_line(line, last_ts, line_no, ifile_path):
  
  # 10.56.100.105:35136 - [24/Feb/2020:12:33:53 +0000] "get scz:50_t2c:1231508407833649152_LogFavBasedTweet_20M_145K_updated" 0 1421
  # 10.71.70.102:36902 - [18/Feb/2020:02:36:14 +0000] "gets NSFA1229529662008614912" 0 326
  # 10.52.170.102:33404 - [24/Feb/2020:12:33:53 +0000] "set scz:50_t2c:1231906474445524992_FavBasedTweet_20M_145K_updated 0 1582548139 1" 0 6
  # 10.86.222.112:35296 - [07/Feb/2020:05:03:22 +0000] "cas NSFA1168399815710920705 0 1583643802 278 342681834" 0 6
      
  line_split = line.strip("\n").split(" ")
  
  client_id, namespace = None, None

  ts = int(time.mktime(time.strptime(line_split[2].strip("[]"), "%d/%b/%Y:%H:%M:%S", )))
  if ts < last_ts:
    if last_ts - ts == 1:
      logging.warning("ignore timestamp out of order current time {} last time {}, line {}, line_no - {}, file {}".format(ts, last_ts, line.strip("\n"), line_no, ifile_path))
      ts = last_ts
    else:
      # raise RuntimeError("timestamp out of order current time {} last time {}, line {}, line_no - {}, file {}".format(ts, last_ts, line.strip("\n"), line_no, ifile_path))
      logging.warning("timestamp out of order current time {} last time {}, line {}, line_no - {}, file {}".format(ts, last_ts, line.strip("\n"), line_no, ifile_path))
      ts = last_ts


  obj_id_with_ns = line_split[5].strip('"')
  obj_id = obj_id_with_ns
  ksize, vsize, ttl = len(obj_id_with_ns), 0, 0
  op = op_mapping.get(line_split[4].strip('"'), -1)

  # note that the pos of size in line_split is different for get and set 
  if op == 1 or op == 2:   # get or gets 
    vsize = int(line_split[7])
    if vsize != 0:  # when the requested obj not in the cache, vsize is 0
      vsize = vsize - 13 - ksize
      vsize -= len(str(vsize)) 

    assert vsize >= 0, "vsize < 0, original size {} new size {}, line {}".format(int(line_split[7]), vsize, line)


  elif 3<=op <= 8:  # set, add, cas, replace, append, prepend
    ttl = int(line_split[7])
    if ttl > 30*24*3600:
      ttl = ttl - ts
    vsize = int(line_split[8].strip('"'))

  elif op == 9:    # delete 
    pass 

  elif op == 10 or op == 11:      # incr/decr
    # print(line)
    vsize = 4

  else: 
    raise RuntimeError("unknown op in line {}".format(line))

  if ttl < 0 and "chubbysnipe" not in ifile_path and "api_annotation_cache" not in ifile_path and "media_metadata" not in ifile_path and "dapi_latest_tweet" \
          not in ifile_path and "observability" not in ifile_path and "live_events" not in ifile_path and "onboarding_cache" not in ifile_path and "sc_profile_labels" not in ifile_path: 
    logging.warning("{}: ttl {}, line {}".format(ifile_path, ttl, line.strip()))
    ttl = 8000000
    # raise RuntimeError("ttl {}, line {}".format(ttl, line))

  return ts, obj_id, ksize, vsize, client_id, op, namespace, ttl

def prepare_for_CPP_converter(task_name, in_dir, ofile_path, hdfs_host, hdfs_port, hdfs_user): 
  hdfs_client = PyWebHdfsClient(host=hdfs_host,port=str(hdfs_port), user_name=hdfs_user)
  file_statuses = hdfs_client.list_dir(in_dir)["FileStatuses"]["FileStatus"]
  # pprint(file_statuses)
  for file_status in file_statuses:
    file_list = sorted([file_status["pathSuffix"] for file_status in file_statuses 
                        if "COPY" not in file_status["pathSuffix"]], key=lambda x: int(x.split(".")[-1]))

  ofile = open(ofile_path, "wb")
  req_buffer = defaultdict(list)
  finished_log_idx, n_req_total, last_write_ts, obj_id_mapping = -1, 0, 0, {}

  for ifile_name in file_list:
    n_req = 0
    ifile_path = "{}/{}".format(in_dir, ifile_name)
    file_idx = int(ifile_name.split(".")[-1])
    if file_idx < finished_log_idx:
      logging.info("skip {}".format(ifile_path))
    trace_reader = TraceReaderHDFS(ifile_path, "twr", hdfs_host, hdfs_port, hdfs_user, hdfs_buffer_size=128*MB)

    raw_line = trace_reader.read_one_req()
    while raw_line:
      line = raw_line.decode()
      n_req += 1
      ts, obj_id, ksize, vsize, client_id, op, namespace, ttl = _parse_log_line(line, last_write_ts, 
        line_no=n_req, ifile_path="{}/{}".format(in_dir, ifile_name))

      if last_write_ts == 0:
        last_write_ts = ts - 1

      # gizmoduck start time 
      if task_name == "gizmoduck_cache" or task_name == "wtf_req_cache":
        if ts < 1585706400:
          raw_line = trace_reader.read_one_req()
          continue 
        # # gizmoduck end time 
        # if ts > 1585706400 + 3600 * 24 * 2:
        #   break 

      # friday 4pm
      if ts < 1585324800:
        raw_line = trace_reader.read_one_req()
        continue 

      # next friday 4pm GMT 
      if ts > 1585929600:
        break 


      req = Req(real_time=ts, obj_id=obj_id, key_size=ksize, value_size=vsize, op=op, ttl=ttl)
      last_write_ts = buffer_req_to_guarantee_time_monotonic(req, req_buffer, ofile, last_write_ts, 2)
      raw_line = trace_reader.read_one_req()
    n_req_total += n_req 
    t1 = time.time()
    logging.info("finish converting one file - {} kReq / total {} kReq, {} kobj, dump time {:.2f}s ifile {}".format(
      n_req//1000, n_req_total//1000, len(obj_id_mapping)//1000, time.time()-t1, "/".join(ifile_path.split("/")[-4:])))

  for ts in sorted(req_buffer.keys()):
    for req in req_buffer[ts]:
      _write_to_ofile(req, ofile)

  logging.info("****************************** finish all conversion {} kReq, ofile {}".format(n_req_total//1000, ofile_path))
  with open("conversion.finish", "a") as ofile2:
    ofile2.write("{}\n".format(in_dir))

  ofile.flush()
  ofile.close()
  return n_req_total, len(obj_id_mapping)


def run_prepare_all(odir, hdfs_host, hdfs_port, hdfs_user):
  os.environ['TZ'] = "UTC"
  time.tzset()
  finished_conversion = set()
  with open("conversion.finish", "r") as ifile:
    for line in ifile:
      finished_conversion.add(line.strip("\n"))
  data_list0 = ["botmaker_2_cache/0", "prediction_from_ranking_cache/0", "taxi_v3_prod_cache/0", "twemcache_video_spam_cache/0", "wtf_req_cache/0", "exchange_auctioncache_cache/0", "geolocationservice_cache/0", "tls_unread_counts_cache/0", ]
  data_list1 = ["botmaker_2_cache/1", "prediction_from_ranking_cache/1", "twemcache_video_spam_cache/1", "wtf_req_cache/1", "exchange_auctioncache_cache/1", "geolocationservice_cache/1", "tls_unread_counts_cache/1",]
  data_list = data_list1
  cache_dir_list = ["/user/junchengy/twemLogFull/disk/traces/smf1/twemcache_backend/prod/{}/".format(cache_name) for cache_name in data_list]
  print("{} cache dir - {} finished".format(len(cache_dir_list), sum([1 for cache_dir in cache_dir_list if cache_dir in finished_conversion])))

  futures_dict = {}
  with ProcessPoolExecutor(max_workers=os.cpu_count()) as ppe:
    for cache_dir in cache_dir_list:
      if cache_dir in finished_conversion:
        continue
      # print(cache_dir, cache_dir.split("/")[-3:-1])
      task_name = ".".join(cache_dir.split("/")[-3:-1])
      ofile_path = "{}/{}.forCPP".format(odir, task_name)
      print(cache_dir, ofile_path)
      # prepare_for_CPP_converter("test", cache_dir, ofile_path, hdfs_host, hdfs_port, hdfs_user)
      # 1/0
      futures_dict[ppe.submit(prepare_for_CPP_converter, task_name, cache_dir, ofile_path, hdfs_host, hdfs_port, hdfs_user)] = cache_dir
    print("all tasks has been submitted now")
    for n, future in enumerate(as_completed(futures_dict)):
      n_req = future.result()
      cahce_dir = futures_dict[future]
      logging.info("{}/{}".format(n+1, len(futures_dict)))


def _cpp_convert(ifile, ofile):
  p = subprocess.run("./CPPConvert -f 1 -i {} -w {}".format(ifile, ofile), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  print("{} {}\n{}".format(ifile.split("/")[-1], p.stdout.decode(), p.stderr.decode()))
  return p.stdout.decode(), p.stderr.decode()


def run_convert_all():
  data_list0 = ["botmaker_2_cache/0", "prediction_from_ranking_cache/0", "taxi_v3_prod_cache/0", "twemcache_video_spam_cache/0", "wtf_req_cache/0", "exchange_auctioncache_cache/0", "geolocationservice_cache/0", "tls_unread_counts_cache/0", ]
  in_dir = "/disk/cppConversion/"
  out_dir = "/disk/cppConverted/"
  futures_dict = {}
  with ProcessPoolExecutor(max_workers=os.cpu_count()) as ppe:
    # for trace_for_cpp in os.list_dir(in_dir):
    for d in data_list0:
      trace_for_cpp = d.replace("/", ".") + ".forCPP" 
      futures_dict[ppe.submit(_cpp_convert, "{}/{}".format(in_dir, trace_for_cpp), "{}/{}".format(out_dir, trace_for_cpp.replace(".forCPP", ".sbin")))] = trace_for_cpp
    print("all tasks has been submitted now")
    for n, future in enumerate(as_completed(futures_dict)):
      n_req = future.result()
      cahce_dir = futures_dict[future]
      logging.info("{}/{}".format(n+1, len(futures_dict)))






if __name__ == "__main__":
  hdfs_host = "hadoop-dw2-user-nn.smf1.twitter.com"
  hdfs_port = "50070"
  hdfs_user = "junchengy"

  run_prepare_all("/disk/cppConversion/", hdfs_host, hdfs_port, hdfs_user, )
  # run_convert_all()


