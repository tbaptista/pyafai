#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Copyright (c) 2014-2015 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

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
    url='none',
    author='Tiago Baptista',
    author_email='baptista@dei.uc.pt',
    packages=['pyafai'],
    install_requires = ['pyglet'],
    license='LICENSE.txt'
)
