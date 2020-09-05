# coding=utf-8


"""
    this module calculates the stat of the trace

"""

from pprint import pformat
from collections import defaultdict


class TraceStat:
    """
    this class provides statistics calculation of a given trace
    """
    def __init__(self, reader, top_N_popular=8):
        self.reader = reader
        self.top_N_popular = top_N_popular
        # stat data representation:
        #       0:  not initialized,
        #       -1: error while obtaining data

        self.num_of_requests = 0
        self.num_of_uniq_obj = 0
        self.cold_miss_ratio = 0

        self.top_N_popular_obj = []
        self.num_one_hit_wonders = 0
        self.freq_mean = 0
        self.time_span = 0

        self.ttl_dict = defaultdict(int)
        self.top_ttl_dict = {}

        self.key_size_mean_weighted_by_req = 0
        self.value_size_mean_weighted_by_req = 0
        self.obj_size_mean_weighted_by_req = 0
        self.req_size_mean_weighted_by_req = 0

        self.key_size_mean_weighted_by_obj = 0
        self.value_size_mean_weighted_by_obj = 0
        self.obj_size_mean_weighted_by_obj = 0
        self.req_size_mean_weighted_by_obj = 0
        self.op_ratio = defaultdict(int)

        self._calculate()


    def _calculate(self):
        """
        calculate all the stat using the reader
        :return:
        """

        req_cnt = defaultdict(int)
        sum_key_size_req, sum_value_size_req, sum_obj_size_req, sum_req_size_req = 0, 0, 0, 0
        sum_key_size_obj, sum_value_size_obj, sum_obj_size_obj, sum_req_size_obj = 0, 0, 0, 0
        first_req = next(self.reader)
        n_nonzero_sz_obj = 0

        for req in self.reader:
            if req.req_size > 0:
                sum_key_size_req += req.key_size * req.cnt 
                sum_value_size_req += req.value_size * req.cnt 
                sum_obj_size_req += req.obj_size * req.cnt 
                sum_req_size_req += req.req_size * req.cnt 

                if req.obj_id not in req_cnt:
                    sum_key_size_obj += req.key_size
                    sum_value_size_obj += req.value_size
                    sum_obj_size_obj += req.obj_size
                    sum_req_size_obj += req.req_size
                    n_nonzero_sz_obj += 1

            if req.op: 
                self.op_ratio[req.op] += 1
                if req.op in ("set", "add", "set", "add", "cas", "replace", "append", "prepend"):
                    ttl = req.ttl
                    # round up
                    if abs(ttl//10*10 - ttl) <= 2:
                        ttl = ttl // 10 * 10 
                    if ttl < 3600:
                        ttl = "{}s".format(ttl)
                    elif 24*3600 > ttl >= 3600:
                        ttl = "{:.1f}h".format(ttl/3600)
                    elif ttl >= 24*3600:
                        ttl = "{:.1f}d".format(ttl/3600/24)
                    ttl = ttl.replace(".0", "")
                    self.ttl_dict[ttl] += 1
            req_cnt[req.obj_id] += req.cnt

        last_req = req 
        self.reader.reset()

        self.num_of_uniq_obj = len(req_cnt)
        self.num_of_requests = sum(req_cnt.values())
        self.cold_miss_ratio = self.num_of_uniq_obj / self.num_of_requests
        self.time_span = last_req.real_time - first_req.real_time

        if n_nonzero_sz_obj == 0:
            print("all requests size 0")
        else:
            self.key_size_mean_weighted_by_req = sum_key_size_req/self.num_of_requests
            self.value_size_mean_weighted_by_req = sum_value_size_req/self.num_of_requests
            self.obj_size_mean_weighted_by_req = sum_obj_size_req/self.num_of_requests
            self.req_size_mean_weighted_by_req = sum_req_size_req/self.num_of_requests

            self.key_size_mean_weighted_by_obj = sum_key_size_obj/n_nonzero_sz_obj
            self.value_size_mean_weighted_by_obj = sum_value_size_obj/n_nonzero_sz_obj
            self.obj_size_mean_weighted_by_obj = sum_obj_size_obj/n_nonzero_sz_obj
            self.req_size_mean_weighted_by_obj = sum_req_size_obj/n_nonzero_sz_obj

        for op, cnt in self.op_ratio.items():
            self.op_ratio[op] = cnt/self.num_of_requests

        # find the top ttl used in the workload 
        total_ttl_cnt = sum(self.ttl_dict.values())
        for ttl, cnt in sorted(self.ttl_dict.items(), key=lambda x:-x[1]):
            self.top_ttl_dict[ttl] = cnt/total_ttl_cnt
            if len(self.top_ttl_dict) >= 10:
                break 

        # l is a list of (obj, freq) in descending order
        l = sorted(req_cnt.items(), key=lambda x: x[1], reverse=True)
        self.top_N_popular_obj = l[:self.top_N_popular]
        # count one-hit-wonders
        for i in range(len(l)-1, -1, -1):
            if l[i][1] == 1:
                self.num_one_hit_wonders += 1
            else:
                break

        self.freq_mean = self.num_of_requests / (float) (self.num_of_uniq_obj)

    def _gen_stat_str(self):
        """
        gegerate a stat str 
        
        """

        s = "dat: {}\nnumber of requests: {}\nnumber of uniq obj/blocks: {}\n" \
            "cold miss ratio: {:.4f}\ntop N popular (obj, num of requests): \n{}\n" \
            "number of obj/block accessed only once: {} ({:.4f})\n" \
            "weighted_by_req: obj_size_mean {:.0f}, req_size_mean {:.0f}, key_size_mean {:.0f}, value_size_mean {:.0f}\n"\
            "weighted_by_obj: obj_size_mean {:.0f}, req_size_mean {:.0f}, key_size_mean {:.0f}, value_size_mean {:.0f}\n"\
            "frequency mean: {:.2f}\n".format(self.reader.trace_path,
                                                self.num_of_requests, self.num_of_uniq_obj,
                                                self.cold_miss_ratio, pformat(self.top_N_popular_obj),
                                                self.num_one_hit_wonders, self.num_one_hit_wonders/self.num_of_uniq_obj,
                                                self.obj_size_mean_weighted_by_req, self.req_size_mean_weighted_by_req, 
                                                self.key_size_mean_weighted_by_req, self.value_size_mean_weighted_by_req,
                                                self.obj_size_mean_weighted_by_obj, self.req_size_mean_weighted_by_obj, 
                                                self.key_size_mean_weighted_by_obj, self.value_size_mean_weighted_by_obj,
                                                self.freq_mean)
        if self.time_span:
            s += "time span: {} ({:.2f} day)\n".format(self.time_span, self.time_span/3600/24)
        if len(self.op_ratio):
            op_ratio_str = "op: " + ", ".join(["{}:{:.4f}".format(op, ratio) for op, ratio in self.op_ratio.items()])
            s += op_ratio_str + "\n"
            # s += "op ratio: {}\n".format(pformat(self.op_ratio))
        if len(self.top_ttl_dict):
            s += "ttl: {} ttls used, ".format(len(self.ttl_dict)) + ", ".join(["{}:{:.4f}".format(ttl, ratio) for ttl, ratio in self.top_ttl_dict.items() if ratio >= 0.01])
        return s 

    def _gen_stat_json(self):
        raise RuntimeError("not implemented")

    def get_stat(self, return_format="str"):
        """
        return stat in the format of string or tuple
        :param return_format:
        :return:
        """

        if return_format == "str":
            return self._gen_stat_str()

        elif return_format == "tuple":
            return (self.num_of_requests, self.num_of_uniq_obj, self.cold_miss_ratio, self.top_N_popular_obj,
                    self.num_one_hit_wonders, self.freq_mean, self.time_span)

        elif return_format == "dict":
            d = self.__dict__.copy()

        elif return_format == "json": 
            return self._gen_json()

        else:
            raise RuntimeError("unknown return format, return string instead")
        return s


    def get_top_N(self):
        return self.top_N_popular_obj


    def __repr__(self):
        return self.get_stat()


    def __str__(self):
        return self.get_stat()






