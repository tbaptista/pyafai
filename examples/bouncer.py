#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Example implementation of an Object type that bounces on the limits of the world
"""

from __future__ import division

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyafai
from pyafai import shapes
from pyafai import objects

class BouncerObject(objects.SimplePhysicsObject):
    def __init__(self, w, h, x=0, y=0, angle=0):
        super(BouncerObject, self).__init__(x, y, angle)

        self._w = w
        self._h = h

    def update(self, delta):
        super(BouncerObject, self).update(delta)

        if self.x > self._w or self.x < 0:
            self.angle = self.angle + 180 - 2*self.angle

        if self.y > self._h or self.y < 0:
            self.angle = self.angle + 180 - 2*(self.angle-90)


if __name__ == '__main__':
    world = pyafai.World2D()
    display = pyafai.Display(world)

    obj = BouncerObject(world.width, world.height, 200, 200)
    shape = shapes.Circle(5)
    obj.add_shape(shape)
    world.add_object(obj)
    obj.velocity = 300
    obj.angle = 30

    pyafai.run()




