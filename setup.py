#!/usr/bin/env python

from distutils.core import setup
import os

# read baseversion from file
base_version_filename = 'VERSION'
with open(base_version_filename) as fh:
    VERSION = fh.read().strip()

setup(name='tictoc',
      version=VERSION,
      description='''tictoc tool for nondeterministic program paths and memory
                     consumption''',
      author='Tobi Baumgartner',
      author_email='tobi@gmail.com',
      packages=['tictoc'],
     )
