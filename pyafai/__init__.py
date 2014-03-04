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
__version__ = '1.0b3'
__author__ = 'Tiago Baptista'

#Try to import the pyglet package
try:
    import pyglet
    import pyglet.window.key as key
except ImportError:
    print("Please install the pyglet package!")
    exit(1)

#import core
from .core import *

            
def run():
    pyglet.app.run()