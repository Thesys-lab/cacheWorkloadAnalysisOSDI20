#!/usr/bin/env python3

from distutils.core import setup
from setuptools import setup, find_packages
from glob import glob
from JPlot import __version__


setup(name='JPlot',
      version=__version__,
      description='A Python library for generating publication ready figures',
      license='MIT',
      author='Juncheng Yang',
      author_email='juncheny@cs.cmu.edu',
      packages=["JPlot", "JPlot.const", "JPlot.styles"],
      # data_files=[('styles', glob('JPlot/styles/*', )), ],
      package_data={'JPlot': glob('JPlot/styles/*', )},
      include_package_data=True,
      url='https://github.com/1a1a11a/JPlot',
      keywords=['plot', 'easy', ],
      install_requires=['matplotlib', 'numpy', ],
      classifiers=[
          # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
      ],
      )


# rm -r dist; python3 setup.py sdist; twine upload dist/*
