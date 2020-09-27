# coding=utf-8
# from distutils.core import setup, Extension
from setuptools import find_packages, setup, Extension
from glob import glob
from distutils.command.build_ext import build_ext
from distutils.command.build_clib import build_clib
import distutils.sysconfig
import platform
import os
import sys
import shutil
import subprocess
import tempfile
import sysconfig
# from Cython.Build import cythonize

import numpy as np


_DEBUG = False

# --------------------- Initialization ------------------------------

extensions = []
extra_compile_args = ["-std=gnu99"]
extra_link_args = ["-lm"]
numpy_headers = []


if _DEBUG:
    extra_compile_args += ["-g", "-ggdb", "-O0", "-UNDEBUG", "-DMIMIR_LOGLEVEL=6"]
else:
    extra_compile_args += ["-O3", "-DMIMIR_LOGLEVEL=7"]

# print(sysconfig.get_config_var("CFLAGS").split())

def get_glib_flag():
    try:
        glib_cflag = subprocess.check_output(
            "pkg-config --cflags glib-2.0", shell=True).decode().strip()
        if not glib_cflag:
            raise RuntimeError("cannot find glib cflag")
        return glib_cflag.split()
    except Exception as e:
        print(e)


def get_glib_library():
    try:
        glib_lib = subprocess.check_output(
            "pkg-config --libs glib-2.0 --libs gthread-2.0", shell=True).decode().strip()
        if not glib_lib:
            raise RuntimeError("cannot find glib lib")
        return glib_lib.split()
    except Exception as e:
        print(e)


def set_platform_related_config():
    if sys.platform == "darwin":
        from distutils import sysconfig
        vars = sysconfig.get_config_vars()
        vars["LDSHARED"] = vars["LDSHARED"].replace("-bundle", "-dynamiclib")
        extra_link_args.append("-dynamiclib")
        # extra_compile_args.append("-dynamiclib")
        os.environ["CC"] = "clang"
        os.environ["CXX"] = "clang"

extra_compile_args.extend(get_glib_flag())
extra_link_args.extend(get_glib_library())

# TODO: need to make sure this is installed 
# extra_link_args.append("-ltcmalloc")
set_platform_related_config()


if _DEBUG:
    print("all compile flags: {}".format(extra_compile_args))
    print("all link flasgs: {}".format(extra_link_args))
    print("{}".format(extensions))


BASE_PATH = "libMimircache/libMimircache/libMimircache/"
PyBinding_PATH = "libMimircache/pyBindings/"
ALL_HEADERS = [BASE_PATH, BASE_PATH + "/include", BASE_PATH + "/include/mimircache",
               BASE_PATH + "/cache/include", BASE_PATH + "/cacheAlgo/include",
               BASE_PATH + "/traceReader/include", BASE_PATH + "/utils/include", 
               BASE_PATH + "/readerUtils/include", 
               BASE_PATH + "/dataStructure/include", BASE_PATH + "/profiler/include", PyBinding_PATH, np.get_include()]
ALL_SOURCES = glob(BASE_PATH + "/cache/*.c") + \
    glob(BASE_PATH + "/cacheAlgo/*.c") + \
    glob(BASE_PATH + "/traceReader/*.c") + \
    glob(BASE_PATH + "/readerUtils/*.c") + \
    glob(BASE_PATH + "/utils/*.c") + \
    glob(BASE_PATH + "/dataStructure/*.c") + \
    glob(BASE_PATH + "/profiler/*.c")

if _DEBUG:
    print("ALL HEADERS {}".format(ALL_HEADERS))
    print("ALL SOURCES {}".format(ALL_SOURCES))

ext_kwargs = {
    "sources": ALL_SOURCES + glob(PyBinding_PATH + "/*.c"),
    "include_dirs": ALL_HEADERS,
    "extra_compile_args": extra_compile_args,
    "extra_link_args": extra_link_args,
    "language": "c",
    "define_macros": [('NDEBUG', '1'), ('LOGLEVEL', '6')],
    "undef_macros": ['HAVE_FOO', 'HAVE_BAR'],
}


extensions.append(Extension("libMC", **ext_kwargs))


long_description = ""

setup(
    name="libMimircache",
    version="0.0.0",
    packages=["libMC", ],
    # modules =
    # package_data={"plain": ["libMimircache/data/trace.txt"],
    #               "csv": ["libMimircache/data/trace.csv"],
    #               "vscsi": ["libMimircache/data/trace.vscsi"],
    #               "conf": ["libMimircache/conf"]},
    # include_package_data=True,
    author="Juncheng Yang",
    author_email="peter.waynechina@gmail.com",
    description="cacheViz is a Python3 toolset for analyzing cache performance",
    license="GPLv3",
    keywords="cacheViz libMimircache mimircache cache LRU simulator",
    url="http://mimircache.info",

    ext_modules=extensions,
    install_requires=["heapdict", "mmh3", "matplotlib", "numpy"]
)


# CC="ccache gcc" CXX="ccache" python3 setup.py build_ext -i


# python3 setup.py sdist upload -r pypitest

# # Compile into .o files
# objects = c.compile(["a.c", "b.c"])

# # Create static or shared library
# c.create_static_lib(objects, "foo", output_dir=workdir)
# c.link_shared_lib(objects, "foo", output_dir=workdir)
