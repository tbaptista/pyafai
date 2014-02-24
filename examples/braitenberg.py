#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Braitenberg vehicles simulation using the iia framework.
"""

__docformat__ = 'restructuredtext'
__version__ = '1.0b'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyafai
from pyafai import influence
from pyafai import shapes
from pyafai import objects
import math

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180


class LightSource(pyafai.Object):
    def __init__(self, x, y, diffuse=0.004):
        super(LightSource, self).__init__(x, y)
        
        self.inf = influence.CircularInfluence(x, y, diffuse = diffuse)
        
        self.add_shape(shapes.Circle(4, ('c3B', (210,210,0))))


class Sensor(pyafai.Perception):
    def __init__(self, x, y, name):
        super(Sensor, self).__init__(float, name)
        self._x = x
        self._y = y

    def update(self, agent):
        s = math.sin(agent.body.angle * DEG2RAD)
        c = math.cos(agent.body.angle * DEG2RAD)
        x = agent.body.x + c * self._x - s * self._y
        y = agent.body.y + s * self._x + c * self._y
        self.value = agent.world.get_light(x, y)
        

class VehicleBody(objects.SimplePhysicsObject):
    def __init__(self, x, y):
        super(VehicleBody, self).__init__(x, y)
        
        #the body shapes
        self.add_shape(shapes.Rect(20, 10))
        self.add_shape(shapes.Rect(6, 4, -10, -5))
        self.add_shape(shapes.Rect(6, 4, -10, 5))

        self._axle = 10
        self._vel_wheelL = 0.0
        self._vel_wheelR = 0.0
        self._vel_max = 30.0

    @property
    def vel_wheels(self):
        return self._vel_wheelL,self._vel_wheelR

    @vel_wheels.setter
    def vel_wheels(self, v):
        self._vel_wheelL = v[0] * self._vel_max
        self._vel_wheelR = v[1] * self._vel_max

        #set linear and angular velocity based on wheel velocity
        self.velocity = (self._vel_wheelL + self._vel_wheelR) / 2
        self.ang_velocity = (self._vel_wheelR - self._vel_wheelL) / self._axle * RAD2DEG

    def add_sensor(self, x, y):
        pass


        
class Vehicle(pyafai.Agent):
    def __init__(self, x, y):
        super(Vehicle, self).__init__()
        self.body = VehicleBody(x, y)
        self.add_light_sensor(10,5, "left")
        self.add_light_sensor(10,-5, "right")

    def add_light_sensor(self, x, y, name):
        light_sensor = Sensor(x, y, name)
        self.add_perception(light_sensor)
        self.body.add_sensor(x, y)

    def _think(self):
        #vehicle 2a
        #self.body.vel_wheels = (self._perceptions["left"].value, self._perceptions["right"].value)

        #vehicle 2b
        self.body.vel_wheels = (self._perceptions["right"].value, self._perceptions["left"].value)

        #vehicle 3a
        #self.body.vel_wheels = (1-self._perceptions["left"].value, 1-self._perceptions["right"].value)

        #vehicle 3b
        #self.body.vel_wheels = (1-self._perceptions["right"].value, 1-self._perceptions["left"].value)
        return []

        


class BraitenbergWorld(pyafai.World2D):
    def __init__(self, width=500, height=500, sector=10):
        super(BraitenbergWorld, self).__init__(width, height)
        
        #make influence map bigger than world by 100 pixels all around
        self._imap = influence.InfluenceMap(width, height, sector)
        self._imap_display = influence.InfluenceMapDisplay(self._imap, color=('c3B', (200,200,0)))
        self.show_influence_map = False
        
    def add_light(self, light):
        self._imap.place(light.inf)
        self.add_object(light)

    def draw(self):
        super(BraitenbergWorld, self).draw()

        if self.show_influence_map:
            self._imap_display.update()
            self._imap_display.batch.draw()


    def get_light(self, x, y):
        return self._imap.get_value(x, y)
        


if __name__ == '__main__':
    world = BraitenbergWorld(sector = 5)
    #world.show_influence_map = True
    display = pyafai.Display(world)
    #display.show_fps = True
    v = Vehicle(250,100)
    v.body.angle = 90
    world.add_agent(v)
    l = LightSource(100,200, diffuse=0.004)
    world.add_light(l)
    #l = LightSource(300,300, diffuse=0.01)
    #world.add_light(l)
    #l = LightSource(150,300, diffuse=0.01)
    #world.add_light(l)
    pyafai.run()

