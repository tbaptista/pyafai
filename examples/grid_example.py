#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Basic example of the use of the pyafai World2DGrid
"""

from __future__ import division

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyglet
import pyafai

def main():
    world = pyafai.World2DGrid(10, 10, 30, True)
    display = pyafai.Display(world)

    obj = pyafai.Object(20, 30)
    shape = pyafai.shapes.Circle(10, color=('c3B', (180, 0, 0)))
    obj.add_shape(shape)
    world.add_object(obj)

    pyafai.run()

if __name__ == '__main__':
    main()