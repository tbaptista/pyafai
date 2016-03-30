#! /usr/bin/env python
#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Braitenberg vehicles simulation using the pyafai framework. Implementation of
vehicles 2a, 2b, 3a, and 3b. There are also two extra vehicles that are not
in the original Valentino Braitenberg's vehicle definitions.

Usage:
Press the I key to toggle the display of the lights' influence map.
Use the left mouse button to add lights to the environment.
"""

import pyafai
from pyafai import influence
from pyafai import shapes
from pyafai import objects
import math
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import random

__docformat__ = 'restructuredtext'
__version__ = '1.0.0'
__author__ = 'Tiago Baptista'

RAD2DEG = 180.0 / math.pi
DEG2RAD = math.pi / 180


class LightSource(pyafai.Object):
    def __init__(self, x, y, radius=100):
        super(LightSource, self).__init__(x, y)
        
        self.inf = influence.CircularInfluence(x, y, radius=radius,
                                               limit=0.001)
        # use a quadratic diffuse function
        self.inf.func = influence.CircularInfluence.light_diffuse
        
        self.add_shape(shapes.Circle(4, color=('c3B', (210,210,0))))


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
        
        self.width = 20
        self.height = 10

        #the body shapes
        self.add_shape(shapes.Rect(self.width, self.height))
        self.add_shape(shapes.Rect(self.width * 0.3, self.height* 0.4,
                                   -self.width/2, -self.height/2))
        self.add_shape(shapes.Rect(self.width * 0.3, self.height* 0.4,
                                   -self.width/2, self.height/2))

        self._axle = self.height
        self._vel_wheelL = 0.0
        self._vel_wheelR = 0.0
        self._vel_max = 100.0

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
        self.add_shape(shapes.Triangle(x,y,x+3,y-2,x+3,y+2,
                                       color=('c3B',(220,0,0))))


class Vehicle(pyafai.Agent):
    def __init__(self, x, y):
        super(Vehicle, self).__init__()
        self.body = VehicleBody(x, y)
        self.add_light_sensor(self.body.width/2, self.body.height/2, "left")
        self.add_light_sensor(self.body.width/2, -self.body.height/2, "right")

    def add_light_sensor(self, x, y, name):
        light_sensor = Sensor(x, y, name)
        self.add_perception(light_sensor)
        self.body.add_sensor(x, y)

    def _think(self, delta):
        return []


class Vehicle2a(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (self._perceptions["left"].value, self._perceptions["right"].value)
        return []


class Vehicle2b(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (self._perceptions["right"].value, self._perceptions["left"].value)
        return []


class Vehicle3a(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (1-self._perceptions["left"].value, 1-self._perceptions["right"].value)
        return []


class Vehicle3b(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (1-self._perceptions["right"].value, 1-self._perceptions["left"].value)
        return []


class MyVehicle1a(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (self._perceptions["left"].value, 1-self._perceptions["right"].value)
        return []


class MyVehicle1b(Vehicle):
    def _think(self, delta):
        self.body.vel_wheels = (self._perceptions["right"].value, 1-self._perceptions["left"].value)
        return []


class MyVehicle2(Vehicle):
    def __init__(self, x, y):
        super(Vehicle, self).__init__()
        self.body = VehicleBody(x, y)
        self.add_light_sensor(0,7, "left")
        self.add_light_sensor(0,-7, "right")

    def _think(self, delta):
        self.body.vel_wheels = (self._perceptions["right"].value, 1-self._perceptions["left"].value)
        return []


class BraitenbergWorld(pyafai.World2D):
    def __init__(self, width=500, height=500, sector=10):
        super(BraitenbergWorld, self).__init__(width, height)

        self._imap = influence.InfluenceMap(width, height, sector)
        self._imap_display = influence.InfluenceMapDisplay(self._imap, color=('c3B', (200,200,0)))
        self.show_influence_map = False
        
    def add_light(self, light, update=True):
        self._imap.place(light.inf, update)
        self.add_object(light)
        if update:
            self._imap_display.update()


    def update(self, delta):
        super(BraitenbergWorld, self).update(delta)

        self._imap_display.update()

    def draw(self):
        super(BraitenbergWorld, self).draw()

        if self.show_influence_map:
            self._imap_display.draw()

    def get_light(self, x, y):
        return self._imap.get_value(x, y)


class BraitenbergDisplay(pyafai.Display):

    def on_key_press(self, symbol, modifiers):
        super(BraitenbergDisplay, self).on_key_press(symbol, modifiers)

        if symbol == key.L:
            self.world.show_influence_map = not(self.world.show_influence_map)

    def on_mouse_release(self, x, y, button, modifiers):
        super(BraitenbergDisplay, self).on_mouse_release(x, y, button, modifiers)

        if button == mouse.LEFT:
            light = LightSource(x, y)
            self.world.add_light(light)


def setup_random(world, n_lights, n_vehicles, vehicle_type):
    for i in range(n_vehicles):
        v = vehicle_type(random.randint(100, world.width - 100),
                      random.randint(100, world.height - 100))
        v.body.angle = random.randint(0,360)
        world.add_agent(v)

    for i in range(n_lights):
        l = LightSource(random.randint(50, world.width - 50),
                        random.randint(50, world.height - 50),
                        100)
        if i < n_lights - 1:
            world.add_light(l, False)
        else:
            world.add_light(l, True)


def setup_one(vehicle_type):

    v = vehicle_type(230,200)
    v.body.angle = 90
    world.add_agent(v)

    l = LightSource(250, 300, 500)
    world.add_light(l)


if __name__ == '__main__':
    world = BraitenbergWorld(500, 500, sector=5)
    world.paused = True
    display = BraitenbergDisplay(world)

    #create lights and vehicles at random locations
    setup_random(world, 5, 5, MyVehicle1a)
    #setup_one(Vehicle2b)

    pyafai.run()