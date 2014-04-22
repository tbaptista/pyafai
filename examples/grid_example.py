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

import pyafai
import pyglet.window.mouse as mouse

class MyDisplay(pyafai.Display):
    def on_mouse_release(self, x, y, button, modifiers):
        super(MyDisplay, self).on_mouse_release(x, y, button, modifiers)

        if button == mouse.LEFT:
            x1, y1 = self.world.get_cell(x, y)
            print(self.world.get_neighbours(x1, y1))


def main():
    world = pyafai.World2DGrid(10, 10, 30, True)
    display = MyDisplay(world)

    obj = pyafai.Object(20, 30)
    shape = pyafai.shapes.Circle(10, color=('c3B', (180, 0, 0)))
    obj.add_shape(shape)
    world.add_object(obj)

    pyafai.run()

if __name__ == '__main__':
    main()