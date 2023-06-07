#!/usr/bin/env python

from distutils.core import setup
import os

# read baseversion from file
base_version_filename = 'VERSION'
with open(base_version_filename) as fh:
    VERSION = fh.read().strip()

lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = lib_folder + '/requirements.txt'
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(name='tictoc',
      version=VERSION,
      install_requires=install_requires,
      url='https://github.com/tobibaum/tictoc',
      description='''tictoc tool for nondeterministic program paths and memory
                     consumption''',
      author='Tobi Baumgartner',
      author_email='tobi@gmail.com',
      packages=['tictoc'],
     )
