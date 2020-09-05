//
//  lirMCMain.c
//  libMimircache binding main func
//
//  Created by Juncheng on 04/18/20.
//  Copyright © 2016-2020 Juncheng. All rights reserved.
//

#include "pyUtils.h"
#include "pyDist.h"
#include "pySim.h"
#include "pyHeatmap.h"
#include "pyTraceUtils.h"

static PyMethodDef libMC_funcs[] = {
    {"get_miss_ratio_curve", (PyCFunction)Py_sim_get_mrc,
     METH_VARARGS | METH_KEYWORDS,
     "evalute a cache replacement algorithm with the given trace and obtain "
     "miss ratio/count/byte at different cache sizes"},

    {"get_stack_dist", (PyCFunction)Py_dist_get_stack_dist,
     METH_VARARGS | METH_KEYWORDS, "get stack distance in a numpy array"},

    {"get_future_stack_dist", (PyCFunction)Py_dist_get_future_stack_dist,
     METH_VARARGS | METH_KEYWORDS, "get future stack distance in a numpy array"},

    {"get_last_access_dist", (PyCFunction)Py_dist_get_last_access_dist,
     METH_VARARGS | METH_KEYWORDS, "get distance to last access in a numpy array"},

    {"get_next_access_dist", (PyCFunction)Py_dist_get_next_access_dist,
     METH_VARARGS | METH_KEYWORDS, "get distance to next access in a numpy array"},

    // {"get_stack_byte", (PyCFunction)Py_dist_get_stack_byte,
    //  METH_VARARGS | METH_KEYWORDS, "get stack distance in bytes in a numpy array"},

    {"get_reuse_time", (PyCFunction)Py_dist_get_reuse_time,
     METH_VARARGS | METH_KEYWORDS, "get time to last access in a numpy array"},

    {"get_stack_dist_heatmap", (PyCFunction)Py_heatmap_get_stack_dist_heatmap,
     METH_VARARGS | METH_KEYWORDS, "get stack distance distribution plot data"},

    {"get_last_access_dist_heatmap", (PyCFunction)Py_heatmap_get_last_access_dist_heatmap,
     METH_VARARGS | METH_KEYWORDS, "get access distance distribution plot data"},

    {"get_reuse_time_heatmap", (PyCFunction)Py_heatmap_get_reuse_time_heatmap,
     METH_VARARGS | METH_KEYWORDS, "get resue time distribution plot data"},


    {"get_last_access_dist_cnt", (PyCFunction)Py_dist_get_last_access_dist_cnt,
     METH_VARARGS | METH_KEYWORDS, "get the count of distance to last access in a numpy array"},

    {"get_first_access_dist_cnt", (PyCFunction)Py_dist_get_first_access_dist_cnt,
     METH_VARARGS | METH_KEYWORDS, "get the count of distance to first access in a numpy array"},

    {"get_reuse_time_cnt", (PyCFunction)Py_dist_get_reuse_time_cnt,
     METH_VARARGS | METH_KEYWORDS, "get the count of reuse time in a numpy array"},


    // {"get_num_of_req", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},
    // {"get_num_of_obj", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},

    // {"get_obj_size_cnt_dict", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},
    // {"get_req_size_cnt_dict", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},

    // {"gen_trace_stat", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},

    // {"get_working_set_size", (PyCFunction)Py_libMC_get_eviction_age,
    //  METH_VARARGS | METH_KEYWORDS, "get eviction age as a numpy array"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef libMC_definition = {
    PyModuleDef_HEAD_INIT, "libMC",
    "A Python module uses libMimircache for high-performance simulation and "
    "computation",
    -1, libMC_funcs};

PyMODINIT_FUNC PyInit_libMC(void) {
  Py_Initialize();
  import_array();
  return PyModule_Create(&libMC_definition);
}

