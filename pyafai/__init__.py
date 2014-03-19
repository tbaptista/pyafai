#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
An agent framework for the Introduction to Artificial Intelligence course.
"""

from __future__ import division

__docformat__ = 'restructuredtext'
__version__ = '1.0b6'
__author__ = 'Tiago Baptista'

#Try to import the pyglet package
try:
    import pyglet
except ImportError:
    print("Please install the pyglet package!")
    exit(1)

#import sub-modules
from .core import *
from . import core
from . import shapes
from . import objects
from . import shapes

            
def run():
    pyglet.app.run()