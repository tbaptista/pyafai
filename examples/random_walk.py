# coding: utf-8
# -----------------------------------------------------------------------------
# Copyright (c) 2014-2016 Tiago Baptista
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Small example of the implemenation of an agent that randomly moves on the world.
Uses as body the bouncer object from another example to bounce on the world
edges.
"""

from __future__ import division

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

import pyafai
from pyafai import shapes
import random
import bouncer

WORLD_WIDTH = 800
WORLD_HEIGHT = 600


class RandomWalker(pyafai.Agent):
    def __init__(self, x=0, y=0, vel=50, color=('c3B',(200,0,0))):
        super(RandomWalker, self).__init__()

        obj = bouncer.BouncerObject(WORLD_WIDTH, WORLD_HEIGHT, x, y)
        shape = shapes.Pointer(10, color=color)
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
    world = pyafai.World2D(WORLD_WIDTH, WORLD_HEIGHT)
    display = pyafai.Display(world)

    for i in range(30):
        walker = RandomWalker(random.randint(10, WORLD_WIDTH-10),
                              random.randint(10, WORLD_HEIGHT-10),
                              random.randint(50,200),
                              ('c3B', (random.randint(0,255),
                                    random.randint(0,255),
                                    random.randint(0,255))))
        walker.body.angle = random.randint(0,359)
        world.add_agent(walker)

    pyafai.run()
