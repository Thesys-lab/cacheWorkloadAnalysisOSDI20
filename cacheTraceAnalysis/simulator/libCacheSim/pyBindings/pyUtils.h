//
// Created by Juncheng Yang on 12/9/19.
//

#ifndef PYCOMMON_H
#define PYCOMMON_H

// python3-config --include
// np.get_include()

#define PY_SSIZE_T_CLEAN
#define NPY_NO_DEPRECATED_API 11

#if defined(__linux__) || defined(__APPLE__)
#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/npy_math.h>
//#elif __APPLE__
//#include
//"/usr/local/Cellar/python/3.7.5/Frameworks/Python.framework/Versions/3.7/include/python3.7m/Python.h"
//#include
//"/Users/jason/Library/Python/3.7/lib/python/site-packages/numpy/core/include/numpy/arrayobject.h"
//#include
//"/Users/jason/Library/Python/3.7/lib/python/site-packages/numpy/core/include/numpy/npy_math.h"
#elif _WIN32
#warning "libMimircache does not support windows"
#endif

#include <glib.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <glib.h>

#include "../libMimircache/libMimircache/cacheAlgo/include/cacheAlgoHeaders.h"
#include "../libMimircache/libMimircache/include/mimircache.h"


static PyObject* Py_err_handle(char* err_str) {
  ERROR("%s", err_str);
  // ERROR(err_str, ##__VA_ARGS__); 
  PyErr_SetString(PyExc_RuntimeError, err_str);
  Py_RETURN_NONE;
}

static char* py_str_to_char_array(PyObject* py_obj) {
  if (py_obj == NULL) {
    Py_err_handle("null obj cannot be converted to char array\n");
    return NULL; 
  }
  char* char_array = NULL;
  PyObject* temp_bytes =
      PyUnicode_AsEncodedString(py_obj, "utf-8", "strict");  // Owned reference
  if (temp_bytes != NULL) {
    char_array = g_strdup(PyBytes_AS_STRING(temp_bytes));  // Borrowed pointer
    Py_DECREF(temp_bytes);
  }
  return char_array;
}

static char* py_str_cp_to_char_array(PyObject* py_obj, char* char_array,
                                     int max_size) {
  if (py_obj == NULL) {
    Py_err_handle("null obj cannot be copy to char array\n");
    return NULL;
  }
  PyObject* temp_bytes =
      PyUnicode_AsEncodedString(py_obj, "utf-8", "strict");  // Owned reference
  if (temp_bytes != NULL) {
    if (strlen(PyBytes_AS_STRING(temp_bytes)) >= (unsigned long) max_size) {
      Py_DECREF(temp_bytes);
      Py_err_handle("trace_path too long");
      exit(1);
    } else {
      strcpy(char_array, PyBytes_AS_STRING(temp_bytes));  // Borrowed pointer
      Py_DECREF(temp_bytes);
    }
  }
  return char_array;
}

#endif  // PYCOMMON_H



