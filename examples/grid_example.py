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

        elif button == mouse.RIGHT:
            x1, y1 = self.world.get_cell(x, y)
            obj_list = self.world.get_cell_contents(x1, y1)
            for obj in obj_list:
                if obj.is_body:
                    obj.agent.kill()


def main():
    world = pyafai.World2DGrid(10, 10, 30, True)
    display = MyDisplay(world)

    obj = pyafai.Object(20, 30)
    shape = pyafai.shapes.Circle(10, color=('c3B', (180, 0, 0)))
    obj.add_shape(shape)
    world.add_object(obj)

    obj = pyafai.Object(4, 8)
    shape = pyafai.shapes.Circle(10, color=('c3B', (180, 180, 0)))
    obj.add_shape(shape)
    agent = pyafai.Agent()
    agent.body = obj
    world.add_agent(agent)

    pyafai.run()

if __name__ == '__main__':
    main()