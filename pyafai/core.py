#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
An agent framework for the Introduction to Artificial Intelligence course.
"""

from __future__ import division

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'

#Try to import the pyglet package
import pyglet
import pyglet.window.key as key
from . import shapes

class Object(object):
    """This class represents a generic object in the world"""
    
    def __init__(self, x = 0, y = 0, angle = 0.0):
        self.x = x
        self.y = y
        self._angle = angle
        self._batch = pyglet.graphics.Batch()
        self._shapes = []

    def __repr__(self):
        return str(type(self).__name__) + "(" + ",".join((str(self.x),
                                                 str(self.y),
                                                 str(self.angle))) + ")"
        
    def add_shape(self, shape):
        shape.add_to_batch(self._batch)
        self._shapes.append(shape)

        
    def draw(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.x, self.y, 0)
        pyglet.gl.glRotatef(self.angle, 0, 0, 1)
        self._batch.draw()
        pyglet.gl.glPopMatrix()
        
    def move_to(self, x, y):
        self.x = x
        self.y = y
        
    def translate(self, tx, ty):
        self.x += tx
        self.y += ty

    def rotate(self, angle):
        self.angle = self.angle + angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        #normalize
        while value > 360:
            value -= 360
        while value < 0:
            value += 360

        self._angle = value

    def update(self, delta):
        pass

    def check_point(self, x, y):
        #Not yet implemented
        return False


class Agent(object):
    """This Class represents an agent in the world"""
    def __init__(self):
        self.body = None
        self._actions = []
        self._perceptions = {}
        self.world = None

    def add_perception(self, perception):
        self._perceptions[perception.name] = perception
    
    def update(self, delta):
        self._update_perceptions()
        actions = self._think(delta)
        if actions:
            for action in actions:
                self.action()
        
    def _update_perceptions(self):
        for p in self._perceptions.values():
            p.update(self)
    
    def _think(self, delta):
        return []

class Perception(object):
    """A generic perception class."""

    def __init__(self, type = int, name = "None"):
        self.value = type()
        self.type = type
        self.name = name

    def update(self, agent):
        pass

    def __str__(self):
        return self.name

class World(object):
    """The environment where to put our agents and objects"""
    def __init__(self):
        self._batch = pyglet.graphics.Batch()
        self._agents = []
        self._objects = []
        self._shapes = []
        self.paused = False
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    
    def add_object(self, obj):
        if isinstance(obj, Object):
            self._objects.append(obj)
        else:
            print("Trying to add an object to the world that is not of type\
                  Object!")
        
    def add_agent(self, agent):
        if isinstance(agent, Agent):
            agent.world = self
            self._agents.append(agent)
            if agent.body != None:
                self.add_object(agent.body)
        else:
            print("Trying to add an agent to the world that is not of type\
                  Agent!")

    def pause_toggle(self):
        self.paused = not self.paused


    def update(self, delta):
        if not self.paused:
            #process agents
            self.process_agents(delta)

            #update all objects
            for obj in self._objects:
                obj.update(delta)

    def process_agents(self, delta):
        for a in self._agents:
            a.update(delta)
    
    def draw(self):
        self._batch.draw()
        
    def draw_objects(self):
        for obj in self._objects:
            obj.draw()

    def get_object_at(self, x, y):
        """Return the first object found at the position x, y, if any.

        :param x: The x position
        :param y: The y position
        """

        for obj in self._objects:
            if obj.check_point(x, y):
                return obj

        return None
            

class World2D(World):
    """A 2D continuous and closed world"""
    
    def __init__(self, width=500, height=500):
        World.__init__(self)
        self.width = width
        self.height = height

    def update(self, delta):
        if not self.paused:
            #process agents
            self.process_agents(delta)

            #update all objects
            for obj in self._objects:
                obj.update(delta)

                #check bounds
                if obj.x > self.width:
                    obj.x = self.width
                if obj.y > self.height:
                    obj.y = self.height
                if obj.x < 0:
                    obj.x = 0
                if obj.y < 0:
                    obj.y = 0
        
        
class World2DGrid(World):
    """A 2D Grid world, closed, and optionally toroidal"""

    moore = ((-1,-1), (0,-1), (1,-1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1))
    
    def __init__(self, width=25, height=25, cell=20, tor=False):
        World.__init__(self)
        self._width = width
        self._height = height
        self.width = width * cell
        self.height = height * cell
        self.cell = cell
        self._half_cell = cell / 2
        self._tor = tor
        self._grid = [[[] for c in range(width)] for l in range(height)]

        #visual grid
        shape = shapes.Grid(width*cell, height*cell, cell)
        shape.add_to_batch(self._batch)
        self._shapes.append(shape)

    def add_object(self, obj):
        #check bounds
        if not self._tor:
            if obj.x > self._width-1:
                obj.x = self._width-1
            if obj.y > self._height-1:
                obj.y = self._height-1
            if obj.x < 0:
                obj.x = 0
            if obj.y < 0:
                obj.y = 0
        else:
            if obj.x > self._width-1 or obj.x < 0:
                obj.x = obj.x % self._width
            if obj.y > self._height-1 or obj.y < 0:
                obj.y = obj.y % self._height

        World.add_object(self, obj)
        self._grid[obj.y][obj.x].append(obj)

    def update(self, delta):
        if not self.paused:
            #process agents
            self.process_agents(delta)

            #update all objects
            for obj in self._objects:
                #remove from _grid
                #self._grid[obj.y][obj.x].remove(obj)

                obj.update(delta)

                #check bounds
                if not self._tor:
                    if obj.x > self._width-1:
                        obj.x = self._width-1
                    if obj.y > self._height-1:
                        obj.y = self._height-1
                    if obj.x < 0:
                        obj.x = 0
                    if obj.y < 0:
                        obj.y = 0
                else:
                    if obj.x > self._width-1 or obj.x < 0:
                        obj.x = obj.x % self._width
                    if obj.y > self._height-1 or obj.y < 0:
                        obj.y = obj.y % self._height

                #re-add to _grid
                #self._grid[obj.y][obj.x].append(obj)

    def draw_objects(self):
        for obj in self._objects:
            x = obj.x
            y = obj.y
            obj.x = x * self.cell + self._half_cell
            obj.y = y * self.cell + self._half_cell
            obj.draw()
            obj.x = x
            obj.y = y

    @property
    def grid_width(self):
        return self._width

    @property
    def grid_height(self):
        return self._height

    def is_empty(self, x, y):
        return len(self._grid[y][x]) == 0

    def get_cell(self, x, y):
        return (x // self.cell, y // self.cell)

    def get_cell_contents(self, x, y):
        return self._grid[y][x]

    def get_neighbours(self, x, y):
        result = []
        for dx,dy in World2DGrid.moore:
            x1 = x + dx
            y1 = y + dy
            if 0 <= x1 < self._width and 0 <= y1 < self._height:
                result.extend(self._grid[y1][x1])

        return result



class Display(pyglet.window.Window):
    """Class used to display the world"""

    def __init__(self, world, multisampling = True):
        if multisampling:
            #Enable multismapling if available on the hardware
            platform = pyglet.window.get_platform()
            display = platform.get_default_display()
            screen = display.get_default_screen()
            template = pyglet.gl.Config(sample_buffers=1, samples=4,
                                        double_buffer=True)
            try:
                config = screen.get_best_config(template)
            except pyglet.window.NoSuchConfigException:
                template = pyglet.gl.Config()
                config = screen.get_best_config(template)

        #get the width and height of the world
        if hasattr(world, 'width') and hasattr(world, 'height'):
            width = world.width
            height = world.height
        else:
            width = 500
            height = 500

        if multisampling:
            #Init the pyglet super class
            super(Display, self).__init__(width, height, caption = 'IIA',
                                          config=config)
        else:
            super(Display, self).__init__(width, height, caption = 'IIA')

        self.show_fps = False
        self.fps_display = pyglet.clock.ClockDisplay()

        self.world = world

    def on_draw(self):
        #clear window
        self.clear()
        
        #draw world
        self.world.draw()
        
        #draw objects
        self.world.draw_objects()
                
        #show fps
        if self.show_fps:
            self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        super(Display, self).on_key_press(symbol, modifiers)

        if symbol == key.F:
            self.show_fps = not(self.show_fps)
        elif symbol == key.P:
            self.world.pause_toggle()
            if self.world.paused:
                self.set_caption(self.caption + " (paused)")
            else:
                self.set_caption(self.caption.replace(" (paused)", ""))

    def on_mouse_release(self, x, y, button, modifiers):
        pass
