#!/usr/bin/env python3

from distutils.core import setup

setup(name='Fetcht',
      version='0.4',
      description='Fetch torrents from various sources',
      author='Alessandro Rosetti',
      author_email='alessandro.rosetti@gmail.com',
      url='http://www.github.com/hexvar/fetcht',
      packages=['fetcht'],
      package_dir={'fetcht': 'src/fetcht'}
     )
