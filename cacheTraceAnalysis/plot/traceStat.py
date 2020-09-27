"""
  this scripts plot the ratio of different operations 

""" 

import os
import re
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
import numpy as np
from utils.common import *


########################################################### trace stat ##########################################################
def load_trace_stat(trace_stat_file):
  """ load data from trace.stat file 
  """ 

  op_mapping = {"get":0, "gets":1, "set":2, "add":3, "replace":4, "append":5, "prepend":6, "cas":7, "delete":8, "incr":9, "decr":10}
  regex_req = re.compile(r"number of requests: (?P<n_req>\d+)")
  regex_obj = re.compile(r"number of uniq obj/blocks: (?P<n_obj>\d+)")
  regex_cold_miss = re.compile(r"cold miss ratio: (?P<cold_miss>0.\d+)")
  regex_one_hit = re.compile(r"number of obj/block accessed only once: (?P<one_hit>\d+)")
  regex_obj_size_req = re.compile(r"weighted_by_req: obj_size_mean (?P<obj_size>\d+), req_size_mean (?P<req_size>\d+), key_size_mean (?P<key_size>\d+), value_size_mean (?P<value_size>\d+)")
  regex_obj_size_obj = re.compile(r"weighted_by_obj: obj_size_mean (?P<obj_size>\d+), req_size_mean (?P<req_size>\d+), key_size_mean (?P<key_size>\d+), value_size_mean (?P<value_size>\d+)")
  regex_op = re.compile(r"op ratio: defaultdict\(\<class 'int'\>,(?P<op_str>[^)]+)")
  regex_ttl = re.compile(r"ttl: (?P<n_ttl>\d+) ttls used, (?P<ttl_details>.+)")

  cold_miss_ratio_list = []
  one_hit_ratio_list = []
  mean_freq_list = []
  obj_size_list = []
  key_size_list = []
  value_size_list = []
  val_key_size_ratio_list = []
  read_ratio_list = []
  write_ratio_list = []
  op_ratio_dict_list = defaultdict(list)
  mean_ttl_list = []  
  ttl_list = []  # all ttls used in the cache
  n_ttl_list = []
  ttl_variation_list1 = [] # in one cache maxTTL/minTTL 
  ttl_variation_list2 = [] # in one cache meanTTL/minTTL 
  smallest_ttl_list = []
  trace_info_dict = {}

  with open(trace_stat_file) as ifile:
    line = ifile.readline()
    while line: 
      if line.startswith("dat"):
        trace_name = line.split(":")[1].strip().split("/")[-1]
        line = ifile.readline()
        continue
      if line.startswith("number of requests"):
        n_req = int(line.split(":")[1])
      elif line.startswith("number of uniq"):
        n_obj = int(line.split(":")[1])
        mean_freq_list.append(n_req/n_obj)

      elif line.startswith("cold"):
        cold_miss_ratio = float(line.split(":")[1])
        cold_miss_ratio_list.append(cold_miss_ratio)

      elif line.startswith("number of obj/block"):
        n_one_hit = int(line.split(":")[1].strip().split(" ")[0])
        one_hit_ratio_list.append(n_one_hit/n_obj)

      elif line.startswith("weighted_by_req"):
        pass

      elif line.startswith("weighted_by_obj"):
        m = regex_obj_size_obj.search(line)
        obj_size_list.append(int(m.group("obj_size")))
        key_size_list.append(int(m.group("key_size")))
        value_size_list.append(int(m.group("value_size")))
        trace_info_dict[trace_name] = int(m.group("obj_size"))
        if int(m.group("key_size")) != 0: 
          val_key_size_ratio_list.append(int(m.group("value_size"))/int(m.group("key_size")))

      elif line.startswith("op"):
        # 1:get, 2:gets, 3:set, 5:add, 6:replace, 7: append, 8: prepend, 9: cas, 10: delete, 11:incr, 12:decr
        # get:1, gets:2, set:3, add:4, cas:5, replace: 6, append: 7, prepend: 8, delete: 9, incr: 10, decr:11

        op_ratio_list = [0] * 11
        for s in line[3:].split(","):
          op, ratio = s.strip().split(":")
          op, ratio = op_mapping[op.strip()], float(ratio)
          op_ratio_list[op] = ratio
        
        for n, ratio in enumerate(op_ratio_list):
          op_ratio_dict_list[n].append(ratio)

        read_ratio_list.append(op_ratio_list[0]+op_ratio_list[1])
        write_ratio_list.append(sum(op_ratio_list[2:]) - op_ratio_list[8])


      elif line.startswith("ttl"):
        m = regex_ttl.search(line)
        n_ttl = int(m.group("n_ttl"))
        ttl_detils = m.group("ttl_details")
        n_ttl_list.append(n_ttl)

        mean_ttl = 0
        cur_trace_ttl_set = set()
        ttl_line_split = ttl_detils.split(",")
        ps = 0
        for ttl_tuple in ttl_line_split:
          t, p = ttl_tuple.split(":")
          # if float(p) > 0.01:
          if t[-1] == "h":
            t = float(t[:-1]) * 3600
          elif t[-1] == "d":
            t = float(t[:-1]) * 3600 * 24
          elif t[-1] == "s":
            t = int(t[:-1])
          else:
            raise RuntimeError("unknown ttl " + t)
          mean_ttl += t * float(p)
          ps += float(p)
          ttl_list.append(t)
          cur_trace_ttl_set.add(t)
        mean_ttl /= ps # temp fix for a bug where the nubmer of TTLs are limited to 10 in traceStat

        mean_ttl_list.append(mean_ttl)
        t = np.array(list(cur_trace_ttl_set))

        if len(cur_trace_ttl_set) > 1:
          smallest_ttl_list.append(np.min(t))
          ttl_variation_list1.append(np.max(t)/max(np.min(t), 60))
          ttl_variation_list2.append(mean_ttl/max(np.min(t), 60))

      line = ifile.readline()

    # pprint(trace_info_dict)
    return cold_miss_ratio_list, one_hit_ratio_list, obj_size_list, key_size_list, value_size_list, \
            val_key_size_ratio_list, read_ratio_list, write_ratio_list, op_ratio_dict_list, mean_ttl_list, \
            n_ttl_list, ttl_variation_list1, ttl_variation_list2, smallest_ttl_list,


########################################################### trace stat ##########################################################
def plot_trace_stat(trace_stat_file):
  from matplotlib.ticker import MaxNLocator
  cold_miss_ratio_list, one_hit_ratio_list, obj_size_list, key_size_list, value_size_list, val_key_size_ratio_list, \
    read_ratio_list, write_ratio_list, op_ratio_dict_list, ttl_list, \
    n_ttl_list, ttl_variation_list1, ttl_variation_list2, smallest_ttl_list = load_trace_stat(trace_stat_file)


  plotTools.plot_cdf(cold_miss_ratio_list)
  plt.xlabel("Cold miss ratio")
  # plt.xlim((0, 0.2))
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/cold_miss".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(one_hit_ratio_list)
  plt.xlabel("One hit wonder ratio")
  # plt.xlim((0.2, 0.4))
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/one_hit".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf([i for i in obj_size_list])
  plt.xscale("log")
  # plt.xticks((10, 100, 1000, 10000, 100000))
  plt.xlabel("Object size (byte)")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/size_obj".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(key_size_list)
  plt.xlabel("Key size (byte)")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/size_key".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(value_size_list)
  plt.xscale("log")
  # plt.xticks((1, 10, 100, 1000, 10000, 100000))
  plt.xlabel("Value size (byte)")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/size_val".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(val_key_size_ratio_list)
  # plt.axvline(x=5, linewidth=2)
  # plt.axvline(x=6, linewidth=2)
  plt.xscale("log")
  plt.xticks((0.1, 1, 10, 100, 1000))
  plt.xlabel("Value/key size ratio")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/size_valKey_szRatio".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()


  plotTools.plot_ccdf(read_ratio_list)
  plt.xlabel("Read ratio")
  plt.ylabel("Fraction of clusters (CCDF)")
  # plt.xlim((0.99,1))
  plt.savefig("{}/read_ratio".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_ccdf(write_ratio_list)
  plt.ylabel("Fraction of clusters (CCDF)")
  plt.xlabel("Write ratio")
  # plt.xlim((0,0.01))
  plt.savefig("{}/write_ratio_ccdf".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()


  plotTools.plot_cdf(write_ratio_list)
  plt.xlabel("Write ratio")
  # plt.xlim((0,0.01))
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/write_ratio".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()


  plotTools.plot_cdf(ttl_list)
  plt.xscale("log")
  plt.axvline(x=1200, linestyle="--", color="black", linewidth=2)
  plt.text(x=16, y=0.80, s="<20 min")
  plt.axvline(x=3600*24*2, linestyle="--", color="black", linewidth=2)
  plt.text(x=3600*24*2+12800, y=0.08, s=" >2 day")
  plt.xticks((100, 1000, 10000, 100000, 1000000))
  plt.xlabel("Mean TTL (s)")
  plt.ylabel("Fraction of clusters (CDF)")
  # plt.xticks((60, 3600, 3600*24), ("1 min", "1 hour", "1 day"))
  plt.savefig("{}/ttl".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(smallest_ttl_list)
  plt.xscale("log")
  plt.axvline(x=300, linestyle="--", color="black", linewidth=2)
  plt.text(x=6, y=0.80, s="<5 min")
  plt.axvline(x=3600*6, linestyle="--", color="black", linewidth=2)
  plt.text(x=3600*6+6400, y=0.08, s=" >6 hour")
  # plt.xticks((60, 3600, 3600*24), ("1 min", "1 hour", "1 day"))
  plt.ylim((0, 1))
  plt.xlabel("The smallest TTL (s)")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/ttl_smallest".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plt.set_n_colors(2)
  plotTools.plot_cdf(ttl_variation_list1, label="$\\frac{TTL_{max}}{max(TTL_{min}, 60)}$")
  # plotTools.plot_cdf(ttl_variation_list2, label="$\\frac{TTL_{mean}}{max(TTL_{min}, 60)}$")
  plt.xscale("log")
  plt.xlabel("TTL range")
  plt.ylabel("Fraction of clusters (CDF)")
  # plt.axvline(x=1.3)
  # plt.axvline(x=1.8)
  # plt.axvline(x=8)
  # plt.axvline(x=50)
  plt.legend(fontsize=30)
  plt.xticks((1, 10, 100, 1000, 10000))
  plt.savefig("{}/ttlvar".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  plotTools.plot_cdf(n_ttl_list)
  # plt.ylim((0.4, 1))
  # plt.yticks((0.4, 0.6, 0.8, 1))
  plt.xscale("log")
  plt.xlabel("#TTL used")
  plt.ylabel("Fraction of clusters (CDF)")
  plt.savefig("{}/ttl_nttl".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()

  op_ratio_matrix = np.array([op_ratio_dict_list[i] for i in range(12) if i in op_ratio_dict_list])
  plt.boxplot(op_ratio_matrix.T, whis=(10, 90), labels=("get", "gets", "set", "add", "replace", "append", "prepend", "cas", "delete", "incr", "decr"))
  # plt.boxplot(op_ratio_matrix.T, whis=(10, 90), labels=("get", "gets", "set", "add", "cas", "replace", "append", "prepend", "delete", "incr", "decr"))

  plt.ylabel("Fraction of requests")
  plt.xticks(rotation=60) # , ha="right")
  plt.savefig("{}/op_ratio_box".format(FIG_DIR), no_save_plot_data=True)
  plt.clf()




if __name__ == "__main__":
  import argparse 
  ap = argparse.ArgumentParser()
  ap.add_argument("--trace_stat", type=str, 
                  default=os.path.join(os.path.dirname(__file__), "../../data/trace_stat.core.twoday"), 
                  help="file path to trace_stat")
  p = ap.parse_args()

  plot_trace_stat(p.trace_stat)








