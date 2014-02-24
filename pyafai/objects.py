#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""This module contains implementations of some specific objects for use in
simulations."""

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

from pyafai import Object
import math

DEG2RAD = math.pi / 180

class SimplePhysicsObject(Object):
    """A simple physics object that can move in 2D space."""

    def __init__(self, x=0, y=0, angle=0):
        super(SimplePhysicsObject, self).__init__(x, y, angle)

        self._vel = 0.0
        self._velx = 0.0
        self._vely = 0.0
        self._ang_vel = 0.0

    @property
    def velocity(self):
        return self._vel

    @velocity.setter
    def velocity(self, v):
        self._velx = v * math.cos(self.angle*DEG2RAD)
        self._vely = v * math.sin(self.angle*DEG2RAD)
        self._vel = v

    @property
    def ang_velocity(self):
        return self._ang_vel

    @ang_velocity.setter
    def ang_velocity(self, v):
        self._ang_vel = v

    def update(self, delta):
        if self._ang_vel != 0:
            self.angle = self._angle + self._ang_vel * delta
        self.x += self._velx * delta
        self.y += self._vely * delta

    @Object.angle.setter
    def angle(self, value):
        self._angle = value
        self.velocity = self._vel

