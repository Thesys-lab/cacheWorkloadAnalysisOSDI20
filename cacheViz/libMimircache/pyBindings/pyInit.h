//
//  pyInit.h
//  create cache and reader
//
//  Created by Juncheng on 04/18/20.
//  Copyright © 2016-2020 Juncheng. All rights reserved.
//

#ifndef PYINIT_H
#define PYINIT_H

#include "pyUtils.h"


// #include "../libMimircache/libMimircache/include/mimircache.h"
// #include "../libMimircache/libMimircache/include/mimircache/plugin.h"

// static void py_close_reader(PyObject *py_reader) {
//   reader_t *reader;
//   if (!(reader = (reader_t *)PyCapsule_GetPointer(py_reader, NULL))) {
//     Py_err_handle("cannot get reader from capsule in py_close_reader\n");
//     return;
//   }
//   DEBUG("reader (%s) is closed\n", reader->base->trace_path);
//   close_reader(reader);
// }

// static void py_free_cache(PyObject *py_cache) {
//   cache_t *cache = (cache_t *)PyCapsule_GetPointer(py_cache, NULL);
//   DEBUG("free cache %s\n", cache->core->cache_name);
//   cache->core->cache_free(cache);
// }

// static PyObject *py_reset_reader(PyObject *self, PyObject *args,
//                                  PyObject *keywds) {
//   PyObject *po;
//   reader_t *reader;

//   // parse arguments
//   static char *kwlist[] = {"reader", NULL};
//   if (!PyArg_ParseTupleAndKeywords(args, keywds, "O", kwlist, &po)) {
//     return Py_err_handle("parsing argument failed in py_reset_reader\n");
//   }

//   if (!(reader = (reader_t *)PyCapsule_GetPointer(po, NULL))) {
//     return Py_err_handle("cannot get reader from capsule in py_reset_reader\n");
//   }

//   reset_reader(reader);
//   Py_RETURN_NONE;
// }

static cache_t *py_setup_cache(char* algorithm, PyObject *py_cache_params, reader_t *reader,
                               guint64 cache_size) {
  // char algorithm[128];
  cache_t *cache;
  void *cache_init_params = NULL;
  common_cache_params_t cc_params = {.cache_size=cache_size, .default_ttl=0}; 

  // py_str_cp_to_char_array(PyDict_GetItemString(py_cache_params, "algorithm"),
  //                         algorithm, 128);

  PyObject *py_cache_init_params = py_cache_params; 
  PyObject *o;


  if (py_cache_params != NULL && py_cache_params != Py_None && (o = PyDict_GetItemString(py_cache_params, "default_ttl")) != NULL){
    cc_params.default_ttl = PyLong_AsLong(o);
  } 

  // if (strcmp(algorithm, "Optimal") == 0) {
  //   Optimal_init_params_t *init_params = g_new(Optimal_init_params_t, 1);
  //   init_params->ts = 0;
  //   init_params->reader = reader;
  //   init_params->next_access = NULL;
  //   cache_init_params = init_params;
  // } else 
  if (strcmp(algorithm, "LRU") == 0) {
    cache_init_params = NULL;
  } else if (strcmp(algorithm, "FIFO") == 0) {
    cache_init_params = NULL;
  // } else if (strcmp(algorithm, "LRU_2") == 0) {
  //   LRU_K_init_params_t *init_params = g_new(LRU_K_init_params_t, 1);
  //   init_params->K = 2;
  //   init_params->maxK = 2;
  //   cache_init_params = init_params;
  // } else if (strcmp(algorithm, "LRU_K") == 0) {
  //   int K = (int)PyLong_AsLong(PyDict_GetItemString(py_cache_init_params, "K"));
  //   LRU_K_init_params_t *init_params = g_new(LRU_K_init_params_t, 1);
  //   init_params->K = K;
  //   init_params->maxK = K;
  //   cache_init_params = init_params;
  // } else if (strcmp(algorithm, "ARC") == 0) {
  //   ARC_init_params_t *init_params = g_new(ARC_init_params_t, 1);
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "ghost_list_factor")) !=
  //           NULL)
  //     init_params->ghost_list_factor = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->ghost_list_factor = 10;
  //   cache_init_params = init_params;
  // } else if (strcmp(algorithm, "SLRU") == 0) {
  //   SLRU_init_params_t *init_params = g_new(SLRU_init_params_t, 1);
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "n_seg")) != NULL)
  //     init_params->n_seg = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->n_seg = 2;
  //   cache_init_params = init_params;
  // } else if (strcmp(algorithm, "slabLRC") == 0) {
  //   slab_init_params_t *init_params = g_new0(slab_init_params_t, 1); 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "slab_size")) != NULL)
  //     init_params->slab_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->slab_size = 1024*1024; 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "per_obj_metadata_size")) != NULL)
  //     init_params->per_obj_metadata_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->per_obj_metadata_size = 0;
  //   // printf("slab %ld\n", init_params->slab_size); 
  //   cache_init_params = init_params; 
  // } else if (strcmp(algorithm, "slabLRU") == 0) {
  //   slab_init_params_t *init_params = g_new0(slab_init_params_t, 1); 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "slab_size")) != NULL)
  //     init_params->slab_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->slab_size = 1024*1024; 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "per_obj_metadata_size")) != NULL)
  //     init_params->per_obj_metadata_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->per_obj_metadata_size = 0;
  //   cache_init_params = init_params; 
  // } else if (strcmp(algorithm, "slabObjLRU") == 0) {
  //   slab_init_params_t *init_params = g_new0(slab_init_params_t, 1); 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "slab_size")) != NULL)
  //     init_params->slab_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->slab_size = 1024*1024; 
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "per_obj_metadata_size")) != NULL)
  //     init_params->per_obj_metadata_size = (gint)PyLong_AsLong(o);
  //   else
  //     init_params->per_obj_metadata_size = 0;
  //   if ((o = PyDict_GetItemString(py_cache_init_params, "slab_move_strategy")) != NULL){
  //     init_params->slab_move_strategy = (gint)PyLong_AsLong(o);
  //     DEBUG("slab auto move enabled %d\n", init_params->slab_move_strategy); 
  //   }
  //   else
  //     init_params->slab_move_strategy = 0;
  //   cache_init_params = init_params; 
  // } else if (strcmp(algorithm, "memcachedLRU") == 0) {
  //   cache_init_params = NULL;
  // } else if (strcmp(algorithm, "TTL_FIFO") == 0) {
  //   cache_init_params = NULL;
  // } else if (strcmp(algorithm, "PG") == 0 || strcmp(algorithm, "AMP") == 0 ||
  //            strcmp(algorithm, "Mithril") == 0) {
  //   ERROR("not suppoerted");
  //   return NULL;
  } else {
    PyErr_Format(PyExc_RuntimeError,
                 "does not support given cache replacement algorithm: %s\n",
                 algorithm);
    return NULL;
  }
  cache = create_cache(algorithm, cc_params, cache_init_params);

  return cache;
}

static reader_t *py_setup_reader(PyObject *py_reader_params) {
  reader_init_param_t init_params = {
      .real_time_field = 0,
      .obj_id_field = 0,
      .obj_size_field = 0,
      .op_field = 0,
      .ttl_field = 0,
      .has_header = FALSE,
      .delimiter = 0,
  };

  PyObject *py_obj;
  char *trace_path, *trace_type_str, *obj_id_type_str;
  trace_type_t trace_type;
  obj_id_type_t obj_id_type = OBJ_ID_STR;
  // void *init_params = NULL;

  if (!PyDict_Check(py_reader_params)) {
    Py_err_handle("reader_params is not a valid python dictionary\n");
    return NULL; 
  }

  trace_path = py_str_to_char_array(
      PyDict_GetItemString(py_reader_params, "trace_path"));
  trace_type_str = py_str_to_char_array(
      PyDict_GetItemString(py_reader_params, "trace_type"));
  obj_id_type_str = py_str_to_char_array(
      PyDict_GetItemString(py_reader_params, "obj_id_type"));

  if (obj_id_type_str[0] == 'c')
    obj_id_type = OBJ_ID_STR;
  else if (obj_id_type_str[0] == 'l')
    obj_id_type = OBJ_ID_NUM;
  else {
    Py_err_handle("unknown obj_id_type, supported obj_id types are c,l\n");
    return NULL; 
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "real_time_field")) !=
      NULL)
    init_params.real_time_field = (gint)PyLong_AsLong(py_obj);

  if ((py_obj = PyDict_GetItemString(py_reader_params, "obj_id_field")) !=
      NULL) {
    init_params.obj_id_field = (gint)PyLong_AsLong(py_obj);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "obj_size_field")) !=
      NULL) {
    init_params.obj_size_field = (gint)PyLong_AsLong(py_obj);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "op_field")) != NULL) {
    init_params.op_field = (gint)PyLong_AsLong(py_obj);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "ttl_field")) != NULL) {
    init_params.ttl_field = (gint)PyLong_AsLong(py_obj);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "fmt")) != NULL) {
    py_str_cp_to_char_array(py_obj, init_params.binary_fmt,
                            MAX_BIN_FMT_STR_LEN);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "has_header")) != NULL) {
    init_params.has_header = PyObject_IsTrue(py_obj);
  }

  if ((py_obj = PyDict_GetItemString(py_reader_params, "delimiter")) != NULL) {
    init_params.delimiter = *((unsigned char *)PyUnicode_AsUTF8(py_obj));
  }

  if (trace_type_str[0] == 'c') {
    trace_type = CSV_TRACE;
    DEBUG2("csv data has header %d, delimiter %d(%c)\n",
           init_params.has_header, init_params.delimiter,
           init_params.delimiter);

  } else if (trace_type_str[0] == 'b') {
    trace_type = BIN_TRACE;

  } else if (trace_type_str[0] == 'p') {
    trace_type = PLAIN_TXT_TRACE;

  } else if (trace_type_str[0] == 'v') {
    trace_type = VSCSI_TRACE;
  } else if (trace_type_str[0] == 't') {
    trace_type = TWR_TRACE;
    obj_id_type = OBJ_ID_NUM;
  } else {
    char err_str[128];
    sprintf(err_str, "unknown trace type %s\n", trace_type_str);
    g_free(trace_type_str);
    g_free(obj_id_type_str);
    Py_err_handle(err_str);
    return NULL;
  }

  reader_t *reader =
      setup_reader(trace_path, trace_type, obj_id_type, &init_params);

  g_free(trace_type_str);
  g_free(obj_id_type_str);
  g_free(trace_path);

  return reader;
}

#endif
