""" a tool to run all analysis on given traces 

"""


import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))

from utils.common import *
from core.traceStat import TraceStat 


def gen_trace_stat(trace_path, ofilename): 
  if ofilename is None: 
    ofilename = "traceStat." + trace_path.split("/")[-1]
  if os.path.exists(ofilename):
    logging.info("{} exists".format(ofilename))
  else:
    print("need to calculate stat {}".format(ofilename))
  if not os.path.exists(os.path.dirname(ofilename)):
    os.makedirs(os.path.dirname(ofilename))
  reader = TwrShortBinTraceReader(trace_path)
  stat = TraceStat(reader)
  ofile = open(ofilename, "w")
  ofile.write("{}\n".format(stat))
  ofile.write("##"*48+"\n")
  ofile.close() 


if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace", type=str, help="trace path")
  ap.add_argument("--type", type=str, help="compute type")
  ap.add_argument("--output", type=str, default=None, help="output path")
  # ap.add_argument("--window", type=int, default=60, help="the size of window in sec")
  p = ap.parse_args()

  if p.type == "trace_stat":
    gen_trace_stat(p.trace, p.output)









def _parallel_proxy(func_name, trace_path, *args):
  hdfs_host = "hadoop-dw2-user-nn.smf1.twitter.com"
  hdfs_port = "50070"
  hdfs_user = "junchengy"
  full_logging_hdfs_dir = "/user/junchengy/twemLogFull/disk/traces/smf1/twemcache_backend/prod/"
  full_logging_hdfs_dir = "/user/junchengy/twemLogFull/bin/twoDay2/"

  try: 
    reader = TwrShortBinTraceReaderHDFS(trace_path, hdfs_host, hdfs_port, hdfs_user, hdfs_buffer_size=128*1024*1024)
    # func_name(TwrBinTraceReader(trace_path), *args)
    # func_name(TwrTraceReader(trace_path), *args)
    func_name(reader, *args)
  except Exception as e:
    print("{} in {} {}".format(e, trace_path, func_name))

def run_all(traces, parallel=True):
  if parallel:
    futures_dict = {}
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as ppe:
      for trace in traces:
        print(trace)
        futures_dict[ppe.submit(_parallel_proxy, gen_trace_stat, trace, "stat/stat")] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_popularity_cnt, trace)] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_popularity_rank, trace)] = trace

        futures_dict[ppe.submit(_parallel_proxy, plot_req_rate, trace, 5)] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_req_rate, trace, 300)] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_req_rate, trace, 3600)] = trace

        futures_dict[ppe.submit(_parallel_proxy, plot_size_dist, trace, "all", True)] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_size_dist_heatmap, trace)] = trace
        futures_dict[ppe.submit(_parallel_proxy, plot_ttl_dist, trace)] = trace 

        futures_dict[ppe.submit(_parallel_proxy, plot_total_workingset_size, trace, 60, True, True)] = trace 

        futures_dict[ppe.submit(_parallel_proxy, plot_rw_ratio_over_time, trace, 3600)] = trace 

        # futures_dict[ppe.submit(_parallel_proxy, plot_workingset_overlap_heatmap, trace, 60, 1)] = trace 
        # futures_dict[ppe.submit(_parallel_proxy, plot_workingset_overlap_heatmap, trace, 3600, 1)] = trace 
        # futures_dict[ppe.submit(_parallel_proxy, plot_workingset_overlap_heatmap, trace, 3600, 2)] = trace 
        
        # futures_dict[ppe.submit(_parallel_proxy, print_final_workingset_size, trace)] = trace 
        # futures_dict[ppe.submit(_parallel_proxy, hotKey.print_hot_keys, trace, 1)] = trace 


      print("{} tasks all submitted".format(len(futures_dict)))

      for n, future in enumerate(as_completed(futures_dict)):
        _ = future.result()
        print("{}/{}".format(n+1, len(futures_dict)))

  else: 
    for trace in traces:
      _parallel_proxy(plot_workingset_overlap_heatmap, trace, 60, 1)
      _parallel_proxy(plot_workingset_overlap_heatmap, trace, 3600, 1)



def test_run(traces):
  for trace in traces:
    # reader = TwrBinTraceReader(trace)
    reader = TwrTraceReader(trace)
    # gen_trace_stat(reader, "stat/stat")
    plot_req_rate(reader, 60)
    # plot_size_dist_heatmap(reader)
    plot_total_workingset_size(reader, 1, False, None)


    # plot_total_workingset_size(reader, 300, True)
    # plot_popularity_rank(reader)
    # operations.plot_rw_ratio_over_time(reader)
    plot_workingset_overlap_heatmap(reader, 20, plot_type=1)
    # plot_workingset_overlap_heatmap(reader, 1200, plot_type=2)
    # plot_workingset_overlap_heatmap(reader, 3600, plot_type=1)
    # plot_workingset_overlap_heatmap(reader, 3600, plot_type=2)


    # logging.info(trace)

def test_run2():
  # reader = TwrTraceReader(os.path.expanduser("../twUtils/pr_pb_at_1"))
  reader = TwrTraceReader(os.path.expanduser("~/Downloads/log-twemcache.cmd.66.atla"))
  # operations.plot_rw_ratio_over_time(reader, window=60)
  # plot_total_workingset_size(reader, 5, False, None) 
  plot_cold_miss_ratio(reader, 60) 
  # plot_workingset_overlap_heatmap(reader, 20, plot_type=1)
  # plot_workingset_overlap_heatmap(reader, 5, plot_type=1)  


if __name__ == "__main__":

  pprint(TWR_full_all_job_one_task_two_day())
  # run_all(TWR_full_all_job_one_task_two_day(), True)
  # run_all(TWR_full_all_job_one_task_two_day(), False)

  # test_run(temp_data())
  # run_all(temp_data())
  # run_all([os.path.expanduser("~/Downloads/log-twemcache.cmd.66.atla"), ])
  # test_run2()








