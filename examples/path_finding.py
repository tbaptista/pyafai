#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Braitenberg vehicles simulation using the iia framework.
"""

__docformat__ = 'restructuredtext'
__version__ = '1.0'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyafai
from pyafai import influence
from pyafai import shapes
from pyafai import objects
import math
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import random


class Graph(object):
    def __init__(self):
        self._graph = {}

    def __init__(self, world):
        pass

    def add_node(self, node, neighbours):
        pass

    def get_neighbours(self, node):
        pass


class Wall(pyafai.Object):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y)

        self.add_shape(shapes.Rect(20,20, color=('c3B',(255,255,255))))


class Mountain(pyafai.Object):
    pass


class Wanderer(pyafai.Agent):
    def __init__(self, x, y, size = 10):
        super(Wanderer, self).__init__()

        self.body = pyafai.Object(x, y)
        self.body.add_shape(shapes.Circle(size/2, color=('c3B',(200,0,0))))


class MyDisplay(pyafai.Display):

    def on_mouse_release(self, x, y, button, modifiers):
        super(MyDisplay, self).on_mouse_release(x, y, button, modifiers)

        if button == mouse.RIGHT:
            x1, y1 = self.world.get_cell(x, y)
            wall = Wall(x1, y1)
            self.world.add_object(wall)
        elif button == mouse.LEFT:
            print(self.world.get_neighbours(*self.world.get_cell(x, y)))


def setup():
    world = pyafai.World2DGrid(25, 20, 20)
    display = MyDisplay(world)

    agent = Wanderer(10, 10, 15)
    world.add_agent(agent)


if __name__ == '__main__':
    setup()
    pyafai.run()


