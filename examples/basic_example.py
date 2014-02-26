#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Basic example of the use of the pyafai framework
"""

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyafai
from pyafai import shapes
from pyafai import objects

if __name__ == '__main__':
    world = pyafai.World()
    display = pyafai.Display(world)

    obj = pyafai.Object(200,200)
    shape = shapes.Circle(10)
    obj.add_shape(shape)
    world.add_object(obj)

    obj2 = objects.SimplePhysicsObject(150,150)
    shape = shapes.Triangle(0, -10, 20, 0, 0, 10, color=('c3B', (200,0,0)))
    obj2.add_shape(shape)
    world.add_object(obj2)
    obj2.ang_velocity = 45
    obj2.velocity = 100

    pyafai.run()
