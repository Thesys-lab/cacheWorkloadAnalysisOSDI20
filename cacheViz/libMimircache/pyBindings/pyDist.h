//
//  pyDist.h
//  export the dist func of libMimircache
//
//  Created by Juncheng on 04/18/20.
//  Copyright © 2016-2020 Juncheng. All rights reserved.
//

#ifndef PYDIST_H
#define PYDIST_H

#include "pyUtils.h"
#include "pyInit.h"

typedef gint64* (*dist_func)(reader_t*); 
typedef gint32* (*dist_cnt_func)(reader_t*, double, gint64*); 


static PyObject *_get_dist(PyObject *self, PyObject *args,
                                PyObject *keywds, dist_func dist_func_ptr){
  reader_t *reader;
  PyObject *py_reader_params;

  static char *kwlist[] = {"reader_params", NULL};

  // parse arguments
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O", kwlist, &py_reader_params))
    return Py_err_handle("parsing argument failed");

  // setup reader and cache
  reader = py_setup_reader(py_reader_params);
  gint64 *dist = dist_func_ptr(reader); 


  npy_intp dims[1] = {get_num_of_req(reader)};
  PyObject *np_dist = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  long long *np_dist_array = PyArray_GETPTR1((PyArrayObject *) np_dist, 0);
  for (long i = 0; i < (long) get_num_of_req(reader); i++) {
    np_dist_array[i] = dist[i];
  }

  g_free(dist);
  close_reader(reader);
  return np_dist;
}


static PyObject *_get_dist_cnt(PyObject *self, PyObject *args,
                                PyObject *keywds, dist_cnt_func dist_cnt_func_ptr){
  reader_t *reader;
  PyObject *py_reader_params;
  double log_base; 
  gint64 n_dist_cnt; 

  static char *kwlist[] = {"reader_params", "log_base", NULL};

  // parse arguments
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "Od", kwlist, &py_reader_params, &log_base)){
    Py_err_handle("parsing argument failed\n");
    Py_RETURN_NONE; 
  }

  // setup reader and cache
  reader = py_setup_reader(py_reader_params);
  gint32 *dist_cnt = dist_cnt_func_ptr(reader, log_base, &n_dist_cnt); 


  npy_intp dims[1] = {n_dist_cnt};
  PyObject *np_dist = PyArray_SimpleNew(1, dims, NPY_LONGLONG);
  long long *np_dist_array = PyArray_GETPTR1((PyArrayObject *) np_dist, 0);
  for (long i = 0; i < (long) n_dist_cnt; i++) {
    np_dist_array[i] = dist_cnt[i];
    // printf("%ld\n", dist_cnt[i]);
  }

  g_free(dist_cnt);
  close_reader(reader);
  return np_dist;
}


static PyObject *Py_dist_get_stack_dist(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist(self, args, keywds, get_stack_dist); 
}

static PyObject *Py_dist_get_future_stack_dist(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist(self, args, keywds, get_future_stack_dist); 
}

static PyObject *Py_dist_get_last_access_dist(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist(self, args, keywds, get_last_access_dist); 
}

static PyObject *Py_dist_get_next_access_dist(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist(self, args, keywds, get_next_access_dist); 
}

// static PyObject *Py_dist_get_stack_byte(PyObject *self, PyObject *args, PyObject *keywds) {
//   return _get_dist(self, args, keywds, get_stack_byte); 
// }

static PyObject *Py_dist_get_reuse_time(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist(self, args, keywds, get_reuse_time); 
}





// static PyObject *Py_dist_get_stack_dist_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
//   return _get_dist(self, args, keywds, get_stack_dist_cnt_in_bins); 
// }

// static PyObject *Py_dist_get_future_stack_dist_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
//   return _get_dist(self, args, keywds, get_future_stack_dist_cnt_in_bins); 
// }

static PyObject *Py_dist_get_last_access_dist_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_cnt(self, args, keywds, get_last_access_dist_cnt_in_bins); 
}

static PyObject *Py_dist_get_first_access_dist_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_cnt(self, args, keywds, get_first_access_dist_cnt_in_bins); 
}

// static PyObject *Py_dist_get_next_access_dist_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
//   return _get_dist(self, args, keywds, get_next_access_dist_cnt_in_bins); 
// }


// static PyObject *Py_dist_get_stack_byte(PyObject *self, PyObject *args, PyObject *keywds) {
//   return _get_dist(self, args, keywds, get_stack_byte_cnt_in_bins); 
// }

static PyObject *Py_dist_get_reuse_time_cnt(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_cnt(self, args, keywds, get_reuse_time_cnt_in_bins); 
}


#endif
