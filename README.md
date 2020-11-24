# In Memory Caching Workload Analysis OSDI'20 

### Description 
This is the analysis code used for the following paper. 

```
Juncheng Yang, Yao Yue, Rashmi Vinayak, A large scale analysis of hundreds of in-memory cache clusters at Twitter. 14th USENIX Symposium on Operating Systems Design and Implementation (OSDI 20), 2020.

```


### Repo explanation 
* cacheTraceAnalysis folder contains all the scripts we use to compute the analysis and generate the figures.  
* JPlot is an internal plotting library 
* data folder contains some precomputed results 

### Data 
Data can been accessed at <https://ftp.pdl.cmu.edu/pub/datasets/twemcacheWorkload/twoDay/>. 
The data is binary in the following format, each trace contains a sequence of requests, each request is represented in 20 bytes: 
```
struct req {
    uint32_t timestamp;
    uint64_t obj_id; 
    uint32_t key_len:8; 
    uint32_t val_len:24;
    uint32_t op:8;
    uint32_t ttl:24;
} 
```

You do not need to write a reader for the trace, the scripts in the repo contains reader that can read the traces. 


### Trace Analysis  
Several figures are based on the statistics of the traces, to calculate the statistics for a trace, run 

`python3 evalTrace.py --trace /path/to/trace --type=trace_stat`, 

note that each trace stat can take hours to days to run. In the case of not having enough computation capacity, we have provided computed stat under `data/`. 


#### Fig 2 
These two figures are generated by querying production systems, so the plot data cannot be regenerated. 

#### Fig 3
this set of figures are plotted using 7-day traces, the two traces used are `ibis_api_cache` and `botmaker_2_cache`  
`python3 plot/reqRate.py --trace /path/to/ibis_api_cache.sbin`
`python3 plot/reqRate.py --trace /path/to/botmaker_2_cache.sbin`


#### Fig 4, 5, 9 
this set of figures are generated using one script, precomputed trace_stat is under `data/trace_stat.core.twoday` 
`python3 plot/traceStat.py --trace_stat /path/to/trace_stat`

#### Fig 6
This set of figures are also generated using the 7-day traces, the two traces used are `simclusters_core_cache`, and `pushservice_mh_cache`. 
the two traces used are xx, to plot the figures, run 
`python3 plot/workingset.py --trace /path/to/pinkfloyd_cache`
`python3 plot/workingset.py --trace /path/to/simclusters_core_cache`

#### Fig 7, 8, 11
Fig 7 is calculated and plot using `popularity.py`, which given a trace plots popularity-rank plot and output alpha and R2, which are used to plot Fig. 8, and Fig. 11. 

#### Fig 10 
Fig 10 are generated using 7 day traces, the four traces are `onboarding_task_service_cache`, `timelines_content_features_cache`, `timelines_ranked_tweet_cache`, `ibis_api_cache`. 

To generate the figure run 
`python3 plot/sizeDistHeatmap.py --trace /path/to/trace`

#### Fig 12, 13, 14 
This set of figures are computed using libCacheSim (see below), it needs to be compiled before running the simulations. 
The four traces in Fig 12 are media_metadata_cache, strato_negative_result, graph_feature_service, timelines_ranked_tweet (using the pre-split the warmup and eval traces under cacheSimEval folder <https://ftp.pdl.cmu.edu/pub/datasets/twemcacheWorkload/cacheSimEval>). 
I have also attached the script for generating the warmup and evaluation traces (simulator.py:split_warmup_eval), so if you want to regenerate the warmup and eval trace, you are welcome to. In addition, we can also provide the warmup and eval traces for other caches, but it would take some time to transfer the data from production data center to outside world. 
In detail, to run the simulation on the four traces (after compiling the simulator), please use 
```
python3 simulator.py --trace_name media_metadata --cache_size 8 --base_path /path/to/traceDir/ --num_of_threads 32 
python3 simulator.py --trace_name strato_negative_result --cache_size 8 --base_path /path/to/traceDir/ --num_of_threads 32 
python3 simulator.py --trace_name graph_feature_service --cache_size 8 --base_path /path/to/traceDir/ --num_of_threads 32 
python3 simulator.py --trace_name timelines_ranked_tweet --cache_size 8 --base_path /path/to/traceDir/ --num_of_threads 32 
```


The two traces in Fig 13 are plotted with libCacheSim as well using the inter-arrival gap calculation, to run and plot, please do 

`python3 dist.py --plot_type=inter_arrival --trace_path=/path/to/trace` 

The two traces in the two figures are strato_negative_result and graph_feature_service. 


The two figures in Fig 14 are generated using script simCompare.py, to generate the figure, simply run `python3 simCompare.py`, notice that the data used to plot the figures are the metadata from running simulations on all traces, due to the huge amount of computation, we have attached a copy of the metadata we have generated under `data/metadata/eviction`, you can rerun the simulations and replace the metadata under this directory. 



#### Simulation 
We use the libCacheSim (libMimircache) simulator <https://github.com/1a1a11a/libCacheSim>, one copy is contained in this repo under simulator. 
We added a Python binding for easy running and plotting. Note that the binding code is not cleaned, we are working on a migration of the binding and a heacy rebase of the libCacheSim. The version in this repo is not up-to-date, but it was the same version used to generate the figures. For future updates, please check the libCacheSim repo. 

To compile the Python3 extension you need to install glib-dev, numpy, and tcmalloc. 
On Ubuntu, this can be installed by running
`sudo apt install libglib2.0-dev libgoogle-perftools-dev`. 

After all dependencies are installed, the simulator and Python binding can be compiled using `python3 setup.py build_ext -i` under the simulator folder. 

Then copy the compiled library to the plot folder by running `cp libMC* ../plot/`




### License
```
Copyright 2020, Carnegie Mellon University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```





