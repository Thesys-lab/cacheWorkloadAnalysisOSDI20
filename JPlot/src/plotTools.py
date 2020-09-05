

import src.pyplot as plt
from collections import defaultdict


def plot_cdf(data_list=None, data_dict=None, **plot_params):
  if data_dict is None and data_list is not None:
    data_dict = defaultdict(int)
    for d in data_list:
      data_dict[d] += 1

  x, y = list(zip(*(sorted(data_dict.items(), key=lambda x: x[0]))))
  y_sum = sum(y)
  y_cdf = [y[0]]
  for i in range(1, len(y)): 
    y_cdf.append(y[i]+y_cdf[-1])
  y_cdf = [i/y_sum for i in y_cdf]
  plt.plot(x, y_cdf, nomarker=True, **plot_params)
  # plt.ylim((0, 1))
  plt.ylabel("Fraction (CDF)")
  plt.grid(linestyle="--")


def plot_ccdf(data_list=None, data_dict=None, **plot_params):
  if data_dict is None and data_list is not None:
    data_dict = defaultdict(int)
    for d in data_list:
      data_dict[d] += 1

  x, y = list(zip(*(sorted(data_dict.items(), key=lambda x: x[0]))))
  y_sum = sum(y)
  y_cdf = [y[0]]
  for i in range(1, len(y)): 
    y_cdf.append(y[i]+y_cdf[-1])
  y_ccdf = [1-i/y_sum for i in y_cdf]
  plt.plot(x, y_ccdf, nomarker=True, **plot_params)
  # plt.ylim((0, 1))
  plt.ylabel("Fraction (CCDF)")
  plt.grid(linestyle="--")


def plot_bar(data_list):
  pass

