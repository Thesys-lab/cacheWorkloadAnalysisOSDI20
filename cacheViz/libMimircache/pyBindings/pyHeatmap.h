//
//  pyHeatmap.h
//  export the heatmap func of libMimircache
//
//  Created by Juncheng on 0/08/20.
//  Copyright © 2016-2020 Juncheng. All rights reserved.
//

#ifndef PYHEATMAP_H
#define PYHEATMAP_H

#include "pyUtils.h"
#include "pyInit.h"
#include "../libMimircache/libMimircache/include/mimircache/distHeatmap.h"


typedef heatmap_plot_matrix_t* (*cal_dist_heatmap_func_ptr)(reader_t *, gint32, double); 

static PyObject *_get_dist_heatmap(PyObject *self, PyObject *args,
                                PyObject *keywds, 
                                cal_dist_heatmap_func_ptr cal_dist_heatmap){
  reader_t *reader;
  PyObject *py_reader_params;
  int window; 
  double log_base; 

  static char *kwlist[] = {"reader_params", "window", "log_base", NULL};

  // parse arguments
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "Oi|d", kwlist, &py_reader_params, &window, &log_base))
    return Py_err_handle("parsing argument failed");

  // setup reader and cache
  reader = py_setup_reader(py_reader_params);
  heatmap_plot_matrix_t *hm_matrix = cal_dist_heatmap(reader, window, log_base); 


  // create numpy array
  npy_intp dims[2] = { hm_matrix->n_pts, hm_matrix->n_window };
  PyObject* ret_array = PyArray_ZEROS(2, dims, NPY_DOUBLE, 0);


  gint32 i, j;
  double **matrix = hm_matrix->matrix;
  double *array;
  /* change it to opposite will help with cache, but may be confusing */
  for (i=0; i<hm_matrix->n_pts; i++){
    array = (double*) PyArray_GETPTR1((PyArrayObject *)ret_array, i);
    for (j=0; j<hm_matrix->n_window; j++)
      if (matrix[j][i]){
        array[j] = matrix[j][i];
        if (array[j] > 1){
          printf("found one larger than one in heatmap %d %d\n", i, j); 
        }
      }
  } 

  // print_heatmap_plot_matrix(hm_matrix); 
  free_heatmap_plot_matrix(hm_matrix);
  close_reader(reader);
  return ret_array;
}


static PyObject *Py_heatmap_get_stack_dist_heatmap(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_heatmap(self, args, keywds, get_stack_dist_heatmap_matrix); 
}

static PyObject *Py_heatmap_get_last_access_dist_heatmap(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_heatmap(self, args, keywds, get_last_access_dist_heatmap_matrix); 
}

static PyObject *Py_heatmap_get_reuse_time_heatmap(PyObject *self, PyObject *args, PyObject *keywds) {
  return _get_dist_heatmap(self, args, keywds, get_reuse_time_heatmap_matrix); 
}




#endif
