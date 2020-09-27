

import os, sys, glob
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
from utils.common import *
import pickle
import bisect
from concurrent.futures import ProcessPoolExecutor, as_completed


METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/metadata/eviction/")


def _find_eval_cache_sizes(cache_sizes, miss_ratio):
  # find the size when miss ratio no longer decrease
  largest_size_pos = bisect.bisect_left(-miss_ratio, -min(miss_ratio))
  largest_size = cache_sizes[min(largest_size_pos, len(cache_sizes)-1)]
  eval_sizes = [largest_size*0.05, largest_size*0.20, largest_size*0.65, largest_size*0.90]
  eval_size_pos = [min(bisect.bisect_left(cache_sizes, s), len(cache_sizes)-1) for s in eval_sizes]
  return eval_sizes, eval_size_pos

def _find_best_alg_in_miss_ratio_dict(miss_ratio_dict, n_eval_sizes):
  best_algo_at_sizes = [None] * n_eval_sizes
  algo_mr_at_sizes = [[] for _ in range(n_eval_sizes)]
  for algorithm, miss_ratio_at_sizes in miss_ratio_dict.items():
    for i, mr in enumerate(miss_ratio_at_sizes):
      algo_mr_at_sizes[i].append((algorithm, mr))
  for i in range(n_eval_sizes):
    s = sorted(algo_mr_at_sizes[i], key=lambda x: x[1])
    best_algo_at_sizes[i] = s[0][0]
    j = 1
    while j < len(miss_ratio_dict) and s[j][1] == s[0][1]:
      best_algo_at_sizes[i] += "-" + s[j][0]
      j += 1

  # print(best_algo_at_sizes)
  return best_algo_at_sizes

def analyze_best_algo():
  n_eval_sizes = 4
  best_algo_cnt = [defaultdict(int) for _ in range(n_eval_sizes)]
  FIFO_LRU_diff = [[] for i in range(n_eval_sizes)]
  # get all available results 
  caches = sorted(list(set(["_".join(i.split("/")[-1].split(".")[0].split("_")[1:]) for i in glob.glob("{}/eviction_*.pickle".format(METADATA_DIR))])))
  for cache_name in caches:
    miss_ratio_dict = {}
    eval_sizes, eval_size_pos = None, None
    for algorithm in ("LRU", "FIFO", "slabLRU", "slabObjLRU"): 
      metadata_list = [i for i in glob.glob("{}/eviction_{}*_{}_ttl*.pickle".format(METADATA_DIR, cache_name, algorithm))]
      # pprint(metadata_list)
      assert(len(metadata_list) == 1)
      with open(metadata_list[0], "rb") as ifile:
        result = pickle.load(ifile)
      miss_ratio = (result["miss_cnt"]/result["req_cnt"]) 
      cache_sizes = result["cache_size"]
      # because each cache requires different sizes, we find the size for evaluation
      if algorithm == "LRU":
        eval_sizes, eval_size_pos = _find_eval_cache_sizes(cache_sizes, miss_ratio)
        # print("{:40}".format(cache_name), ["{:.2f} GB".format(i/GB) for i in eval_sizes], eval_size_pos, end="\t")
      miss_ratio_at_eval_sizes = [miss_ratio[i] for i in eval_size_pos]
      miss_ratio_dict[algorithm] = miss_ratio_at_eval_sizes 

    best_algo_at_sizes = _find_best_alg_in_miss_ratio_dict(miss_ratio_dict, n_eval_sizes)
    for size_i, algos in enumerate(best_algo_at_sizes):
      if "-" in algos:
        # if multiple algorithms have the same miss ratio
        algo_list = algos.split("-")
        if len(algo_list) > 2:
          continue
        for algo in algo_list:
          best_algo_cnt[size_i][algo] += 1/len(algo_list)
      else:
        best_algo_cnt[size_i][algos] += 1

    for i in range(n_eval_sizes):
      diff = (miss_ratio_dict["FIFO"][i] - miss_ratio_dict["LRU"][i])/max(0.002, miss_ratio_dict["LRU"][i])
      FIFO_LRU_diff[i].append(diff)


  for best_algo_cnt_at_size_i in best_algo_cnt:
    pprint(best_algo_cnt_at_size_i)

  for i, sz_str in enumerate(("very small", "small", "medium", "large")):
    plotTools.plot_cdf(FIFO_LRU_diff[i], label=sz_str, linewidth=2.4)

  plt.xlim((-0.64, 0.64))
  plt.ylim((-0.04, 1.04))
  plt.xlabel(r"miss ratio $\frac{FIFO-LRU}{LRU}$")
  plt.ylabel("Fraction of workloads (CDF)")
  plt.legend()
  plt.grid(linestyle="--")
  plt.savefig("fig/fifo_lru_diff")
  plt.clf()


def plot_best_algo():
  algorithms = ("LRU", "FIFO", "slabLRU", "Memcached-LRU")

  # this is obtained from analyze_best_algo 
  very_small_cache_size = np.array((23.5, 5.0, 9.0, 3.5))
  small_cache_size = np.array((15.0, 13.0, 10.0, 2.0))
  medium_cache_size = np.array((17.0, 12.0, 8.0, 1.0))
  large_cache_size = np.array((15.0, 15.5, 4.0, 1.5))

  small_cache_size = small_cache_size/np.sum(small_cache_size)
  medium_cache_size = medium_cache_size/np.sum(medium_cache_size)
  large_cache_size = large_cache_size/np.sum(large_cache_size)
  very_small_cache_size = very_small_cache_size/np.sum(very_small_cache_size)
  plot_data = np.array((very_small_cache_size, small_cache_size, medium_cache_size, large_cache_size))

  plt.bar(np.arange(plot_data.shape[0]), plot_data[:, 0], width=0.4, label=algorithms[0])
  plt.bar(np.arange(plot_data.shape[0]), plot_data[:, 1], width=0.4, bottom=plot_data[:, 0], label=algorithms[1])
  plt.bar(np.arange(plot_data.shape[0]), plot_data[:, 2], width=0.4, bottom=np.sum(plot_data[:, :2], axis=1), label=algorithms[2])
  plt.bar(np.arange(plot_data.shape[0]), plot_data[:, 3], width=0.4, bottom=np.sum(plot_data[:, :3], axis=1), label=algorithms[3])
  plt.xticks(np.arange(4), ("very small", "small", "medium", "large"), rotation=16, ha='center')
  plt.ylim((0, 1.08))
  plt.xlabel("Cache size")
  plt.ylabel("Fraction of workloads being best")
  plt.legend(ncol=2, bbox_to_anchor=(1.00, 1.28))
  plt.savefig("fig/best_algo")
  plt.clf()



if __name__ == "__main__": 
    analyze_best_algo()
    plot_best_algo()







