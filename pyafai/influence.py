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

"""This module contains the implementation of influence maps, used mainly to
provide sensory fields (e.g. for light or sound)"""

from __future__ import division

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'


from . import shapes
import math
import pyglet


class Influence(object):
    """The abstract base class for influences to place in the influence map"""
    
    def update(self, delta):
        pass
    
    def get_value(self, x, y):
        return 0.0
    
    
class CircularInfluence(Influence):
    """A circular influence emitter to place in the influence map"""
    
    def __init__(self, x, y, strength = 1.0, radius = 100, degrade = 0.0,
                 limit = 0.001, static = True):
        self.x = x
        self.y = y
        self.strength = strength
        self.radius = radius
        self.r = radius/3
        self.diffuse = 1/radius
        self.static = static
        self.limit = limit

        if static and degrade != 0.0:
            print("A static influence can not have a degrade value different \
                  than 0! Value set to 0.")
            self.degrade = 0.0
        else:
            self.degrade = degrade

        self.func = CircularInfluence.linear_diffuse
        
    def update(self, delta):
        if self.degrade != 0 and self.strength > 0:
            self.strength -= self.degrade * delta
            if self.strength < self.limit:
                self.strength = 0
            return True

        return False
        
    def get_value(self, x, y):
        return self.func(self, x, y)

    def linear_diffuse(self, x, y):
        dist = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        return max(self.strength - (self.diffuse * dist), 0)

    def light_diffuse(self, x, y):
        dist = math.sqrt((x - self.x)**2 + (y - self.y)**2)
        att = 1 / ((dist/self.r + 1)**2)
        res = self.strength * att
        if res < self.limit:
            return 0
        return res


class InfluenceMap(object):
    """A 2D influence map.
    
    TODO: Verify that the total size is divisible by the sector size.
    """
    
    def __init__(self, width, height, sector, maximum = 1.0):
        self.width = width
        self.height = height
        self.map_width = int(width // sector)
        self.map_height = int(height // sector)
        self.sector = sector
        self.maximum = maximum
        self.dirty = True
        
        self._imap = [self.map_width * [0.0] for i in range(self.map_height)]
        self._ilist = []
        
    def place(self, influence, update=True):
        if 0 <= influence.x <= self.width and 0 <= influence.y <= self.height:
            self._ilist.append(influence)
            if update:
                self.update()
        else:
            print("Tying to place an influence outside the limits of the map")

    def get_value(self, x, y):
        if 0 < x < self.width and 0 < y < self.height:
            x = int(x // self.sector)
            y = int(y // self.sector)
            return self._imap[y][x]
        else:
            return 0.0

    def get_grid_value(self, x, y):
        return self._imap[y][x]
        
    def update_influences(self, delta):
        res = False
        for i in self._ilist:
            res = res or i.update(delta)

        self.dirty = res

    def update(self):
        for y in range(self.map_height):
            for x in range(self.map_width):
                a = 0
                for i in self._ilist:
                    a = a + i.get_value(x * self.sector + self.sector/2,
                                        y*self.sector + self.sector/2)
                if a > self.maximum:
                    a = self.maximum
                self._imap[y][x] = a

        self.dirty = True
            

class InfluenceMapDisplay(object):
    """This class is used to display the influence map on a 2D world"""

    def __init__(self, imap, color = ('c3B', (255,0,0))):
        self.batch = pyglet.graphics.Batch()
        self.imap = imap
        self.color = color
        self.vlists = []
        shape = shapes.Rect(imap.sector, imap.sector,
                            imap.sector/2, imap.sector/2, color)
        n = len(shape.vertices[1]) // 2
        t = imap.sector

        #create shape objects
        for y in range(imap.map_height):
            self.vlists.append([])
            for x in range(imap.map_width):
                #get influence value
                v = imap.get_grid_value(x, y)

                #normalize
                v = v / imap.maximum

                #change color
                new_color = (self.color[0], [int(c*v) for c in self.color[1]])

                #create shape in batch and save to list
                new_vertices = shape.translate(x*imap.sector, y*imap.sector)
                vlist = self.batch.add(n, shape.gl_type, None,
                                       ('v2f', new_vertices),
                                       (new_color[0], new_color[1]*n))
                self.vlists[y].append(vlist)



        imap.dirty = False

    def update(self):
        if (self.imap.dirty):
            for y in range(self.imap.map_height):
                for x in range(self.imap.map_width):
                    #get influence value
                    v = self.imap.get_grid_value(x, y)

                    #normalize
                    v = v / self.imap.maximum

                    #set color
                    vertexlist = self.vlists[y][x]
                    vertexlist.colors[:] = [int(c*v) for c in self.color[1]] * 4

            self.imap.dirty = False

    def draw(self):
        self.batch.draw()