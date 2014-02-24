#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

'''This module contains helper classes to draw basic shapes in pyglet'''

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

import pyglet
import math
from math import pi

class Shape:
    def __init__(self, color=('c3B', (255,255,255))):
        self.gl_type = None
        self.vertices = None
        self.color = color
        self.vertexlist = None

    def translate(self, tx, ty):
        res = [(v[0] + tx, v[1] + ty) for v in zip(self.vertices[1][::2], self.vertices[1][1::2])]
        res = [x for v in res for x in v]
        return res

    
class Rect(Shape):
    def __init__(self, w, h, x=0, y=0, color=('c3B', (255,255,255))):
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
    def __init__(self, x1, y1, x2, y2, color = ('c3B', (255,255,255))):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_LINES
        self.vertices = ('v2f', (x1, y1, x2, y2))
        

class Triangle(Shape):
    def __init__(self, x1, y1, x2, y2, x3, y3, color = ('c3B', (255,255,255))):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_TRIANGLES
        self.vertices = ('v2f', (x1, y1, x2, y2, x3, y3))
        

class Circle(Shape):
    def __init__(self, r, color = ('c3B', (255,255,255))):
        Shape.__init__(self, color)
        
        self.gl_type = pyglet.gl.GL_TRIANGLES
        sides = int(pi*r)
        dang = 2*pi / sides
        ang = 0
        x = math.cos(ang) * r
        y = math.sin(ang) * r        
        vertices = [0,0,r,0,x,y]
        for i in range(sides+1):
            x = math.cos(ang) * r
            y = math.sin(ang) * r
            vertices.extend([0,0,vertices[-2], vertices[-1],x,y])
            ang += dang
            
        #vertices.extend(vertices[-2:])
        self.vertices = ('v2f', vertices)
            
        
