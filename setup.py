#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014-2016 Tiago Baptista
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

from setuptools import setup
from io import open

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

version = {}
with open('pyafai/__version__.py', encoding='utf-8') as f:
    exec(f.read(), version)

setup(
    name='pyafai',
    version=version['__version__'],
    description='Python Agent Framework for Artificial Intelligence',
    long_description = long_description,
    url='https://github.com/tbaptista/pyafai',
    author='Tiago Baptista',
    author_email='baptista@dei.uc.pt',
    license='Apache License 2.0',
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
        'Topic :: Education',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Artificial Life',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],

    packages=['pyafai'],
    install_requires = ['pyglet'],
)
