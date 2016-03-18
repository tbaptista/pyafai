# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014-2016 Tiago Baptista
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

"""
This module contains helper classes to draw basic shapes in pyglet.
"""

from __future__ import division
import pyglet
import math
from math import pi

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'


class Shape(object):
    def __init__(self, color=('c3B', (255,255,255))):
        self.gl_type = None
        self.vertices = None
        self.indices = None
        self._color = color
        self.vertexlist = None

    def __del__(self):
        if self.vertexlist != None:
            self.vertexlist.delete()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        if self.vertexlist is not None:
            # This will only work if the color is using the same number of
            # components
            self.vertexlist.colors[:] = value[1] * self.vertexlist.get_size()

        self._color = value

    def add_to_batch(self, batch: pyglet.graphics.Batch):
        if self.vertexlist is None:
            n = len(self.vertices[1]) // 2
            if self.indices is None:
                self.vertexlist = batch.add(n, self.gl_type, None, self.vertices,
                                            (self.color[0], self.color[1] * n))
            else:
                self.vertexlist = batch.add_indexed(n, self.gl_type, None,
                                                    self.indices, self.vertices,
                                                    (self.color[0], self.color[1] * n))
            return self.vertexlist
        else:
            print("This shape was already added to a Batch, please do not \
                    reuse.")

    def translate(self, tx, ty):
        res = [(v[0] + tx, v[1] + ty) for v in zip(self.vertices[1][::2],
                                                   self.vertices[1][1::2])]
        res = [x for v in res for x in v]
        return res


class Rect(Shape):
    def __init__(self, w, h, x=0, y=0, color=('c3B', (255, 255, 255))):
        Shape.__init__(self, color)
        
        w = w/2
        h = h/2
        x1 = x - w
        y1 = y + h
        x2 = x + w
        y2 = y - h
        
        self.gl_type = pyglet.gl.GL_QUADS
        self.vertices = ('v2f', (x1, y1, x2, y1, x2, y2, x1, y2))


class Line(Shape):
    def __init__(self, x1, y1, x2, y2, color=('c3B', (255, 255, 255))):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_LINES
        self.vertices = ('v2f', (x1, y1, x2, y2))
        

class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3, color=('c3B', (255, 255, 255))):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_TRIANGLES
        self.vertices = ('v2f', (x1, y1, x2, y2, x3, y3))
        

class Circle(Shape):
    def __init__(self, r, cx=0, cy=0, color=('c3B', (255, 255, 255)),
                 res=1):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_TRIANGLES
        sides = int(pi*r*res)
        dang = 2*pi / sides
        ang = 0
        x = math.cos(ang) * r
        y = math.sin(ang) * r
        vertices = [0, 0, r, 0, x, y]
        for i in range(sides+1):
            x = math.cos(ang) * r
            y = math.sin(ang) * r
            vertices.extend([0, 0, vertices[-2], vertices[-1], x, y])
            ang += dang

        self.vertices = ('v2f', vertices)
        vertices = self.translate(cx, cy)
        self.vertices = ('v2f', vertices)


class Pointer(Shape):
    def __init__(self, size, x=0, y=0, color=('c3B', (255, 255, 255))):
        super(Pointer, self).__init__(color)

        self.gl_type = pyglet.gl.GL_TRIANGLES
        hsize = size / 2
        self.vertices = ('v2f', (x, y,
                                 x - hsize, y - hsize,
                                 x + size, 0,
                                 -hsize, hsize))
        self.indices = [0, 1, 2,
                        0, 2, 3]


class Grid(Shape):
    def __init__(self, width, height, cell, color=('c3B', (200, 200, 200))):
        Shape.__init__(self, color)

        vertices = []
        lines = width//cell + height // cell + 2
        self.gl_type = pyglet.gl.GL_LINES

        # vertical lines
        for i in range(width//cell + 1):
            vertices.extend([i*cell, 0, i*cell, height])

        # horizontal lines
        for i in range(height//cell + 1):
            vertices.extend([0, i*cell, width, i*cell])

        self.vertices = ('v2f', tuple(vertices))


class Sprite(Shape):
    def __init__(self, filename, cx=0, cy=0):
        Shape.__init__(self)
        image = pyglet.image.load(filename)
        image.anchor_x = image.width // 2
        image.anchor_y = image.height // 2
        self._sprite = pyglet.sprite.Sprite(image, cx, cy)

    def add_to_batch(self, batch):
        self._sprite.batch = batch

