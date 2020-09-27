//
//  pySim.h
//  export the simulation func of libMimircache
//
//  Created by Juncheng on 04/18/20.
//  Copyright © 2016-2020 Juncheng. All rights reserved.
//

#ifndef PYSIM_H
#define PYSIM_H

#include "pyUtils.h"
#include "pyInit.h"

static PyObject *Py_sim_get_mrc(PyObject *self, PyObject *args,
                                PyObject *keywds) {
  reader_t *reader, *warmup_reader = NULL;
  int num_of_threads = 1;
  double warmup_perc = 0;
  cache_t *cache;
  guint64 *cache_sizes;
  int num_of_sizes;
  char *algorithm; 
  PyObject *py_reader_params, *py_warmup_reader_params=NULL, *py_cache_params=NULL, *py_cache_sizes;


  static char *kwlist[] = {"reader_params", "algorithm", "cache_sizes", "cache_params", 
                           "warmup_reader_params", "warmup_perc", "num_of_threads", NULL};
  // parse arguments
  if (!PyArg_ParseTupleAndKeywords(
          args, keywds, "OsO|OOdi", kwlist, &py_reader_params, &algorithm, 
          &py_cache_sizes, &py_cache_params, &py_warmup_reader_params, &warmup_perc, &num_of_threads)){
    ERROR("parsing argument failed in Py_sim_get_mrc\n");
    Py_RETURN_NONE;
  }

  if (!PyList_Check(py_cache_sizes)) {
    ERROR("py_cache_sizes is not a valid list");
    Py_RETURN_NONE;
  }

  num_of_sizes = (int)PyList_Size(py_cache_sizes);
  cache_sizes = g_new(guint64, num_of_sizes);
  for (int i = 0; i < num_of_sizes; i++)
    cache_sizes[i] = (guint64)PyLong_AsLong(PyList_GetItem(py_cache_sizes, i));

  // setup reader and cache
  reader = py_setup_reader(py_reader_params);
  if (py_warmup_reader_params && py_warmup_reader_params != Py_None)
    warmup_reader = py_setup_reader(py_warmup_reader_params); 
  cache = py_setup_cache(algorithm, py_cache_params, reader, 1024*1024*1024);
  if (reader == NULL) {
    Py_RETURN_NONE;
  } 
  if (cache == NULL) {
    Py_RETURN_NONE; 
  }
  INFO("%s warmup %lf - warmup reader %p - %d thread - default_ttl %ld\n", algorithm, warmup_perc, warmup_reader, num_of_threads, cache->core.default_ttl); 

  // run the trace
  profiler_res_t *results = get_miss_ratio_curve(
      reader, cache, num_of_sizes, cache_sizes, warmup_reader, warmup_perc, num_of_threads);

  PyObject *ret_dict = PyDict_New();
  npy_intp dims[1] = {num_of_sizes};

  PyObject *np_miss_cnt = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_miss_bytes = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_cache_size = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_used_bytes = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_stored_obj_cnt = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_expired_bytes = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  PyObject *np_expired_obj_cnt = PyArray_SimpleNew(1, dims, NPY_LONGLONG);

  long long *miss_cnt_array = PyArray_GETPTR1((PyArrayObject *)np_miss_cnt, 0);
  long long *miss_bytes_array = PyArray_GETPTR1((PyArrayObject *)np_miss_bytes, 0);
  long long *cache_size_array = PyArray_GETPTR1((PyArrayObject *)np_cache_size, 0);
  long long *used_bytes_array = PyArray_GETPTR1((PyArrayObject *)np_used_bytes, 0); 
  long long *stored_obj_cnt_array = PyArray_GETPTR1((PyArrayObject *)np_stored_obj_cnt, 0); 
  long long *expired_bytes_array = PyArray_GETPTR1((PyArrayObject *)np_expired_bytes, 0); 
  long long *expired_obj_cnt_array = PyArray_GETPTR1((PyArrayObject *)np_expired_obj_cnt, 0); 

  for (int i = 0; i < num_of_sizes; i++) {
    miss_cnt_array[i] = results[i].miss_cnt;
    miss_bytes_array[i] = results[i].miss_byte;
    cache_size_array[i] = results[i].cache_size; 
    // used_bytes_array[i] = results[i].cache_state.used_bytes; 
    // stored_obj_cnt_array[i] = results[i].cache_state.stored_obj_cnt; 
    // expired_bytes_array[i] = results[i].cache_state.expired_bytes; 
    // expired_obj_cnt_array[i] = results[i].cache_state.expired_obj_cnt; 
  }

  PyDict_SetItemString(ret_dict, "cache_size", np_cache_size);
  // PyDict_SetItemString(ret_dict, "used_bytes", np_used_bytes);
  // PyDict_SetItemString(ret_dict, "expired_bytes", np_expired_bytes);
  // PyDict_SetItemString(ret_dict, "stored_obj_cnt", np_stored_obj_cnt);
  // PyDict_SetItemString(ret_dict, "expired_obj_cnt", np_expired_obj_cnt);
  PyDict_SetItemString(ret_dict, "miss_cnt", np_miss_cnt);
  PyDict_SetItemString(ret_dict, "miss_bytes", np_miss_bytes);
  PyDict_SetItemString(ret_dict, "req_cnt",
                       PyLong_FromLongLong(results[0].req_cnt));
  PyDict_SetItemString(ret_dict, "req_bytes",
                       PyLong_FromLongLong(results[0].req_byte));

  g_free(results);
  cache->core.cache_free(cache);
  close_reader(reader);
  return ret_dict;
}

#endif
