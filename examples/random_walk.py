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
import random
import bouncer


class RandomWalker(pyafai.Agent):
    def __init__(self, x=0, y=0, vel=50, color=('c3B',(200,0,0))):
        super(RandomWalker, self).__init__()

        obj = bouncer.BouncerObject(500, 500, x, y)
        shape = shapes.Triangle(0, -10, 20, 0, 0, 10, color=color)
        obj.add_shape(shape)
        obj.velocity = vel
        self.body = obj
        self._last_think = 0.0

    def _think(self, delta):
        self._last_think += delta
        if self._last_think >= 0.2:
            self._last_think = 0
            rotate = random.choice((-180,0,180))
            self.body.ang_velocity = rotate

        return []

if __name__ == '__main__':
    world = pyafai.World2D()
    display = pyafai.Display(world)

    for i in range(30):
        walker = RandomWalker(random.randint(10,490), random.randint(10,490),
                              random.randint(50,200),
                              color = ('c3B', (random.randint(0,255),
                                               random.randint(0,255),
                                               random.randint(0,255))))
        walker.body.angle = random.randint(0,359)
        world.add_agent(walker)

    pyafai.run()