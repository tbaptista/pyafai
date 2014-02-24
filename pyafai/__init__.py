#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
An agent framework for the Introduction to Artificial Intelligence course.
"""

__docformat__ = 'restructuredtext'
__version__ = '1.0b'
__author__ = 'Tiago Baptista'

#Try to import the pyglet package
try:
    import pyglet
except:
    print("Please install the pyglet package!")
    exit(1)
    
from . import shapes
    
    
class Object:
    """This class represents a generic object in the world"""
    
    def __init__(self, x = 0, y = 0, angle = 0.0):
        self.x = x
        self.y = y
        self._angle = angle
        self._batch = pyglet.graphics.Batch()
        self._shapes = []
        
    def add_shape(self, shape):
        n = len(shape.vertices[1]) // 2
        shape.vertexlist = self._batch.add(n, shape.gl_type, None, shape.vertices,
                                     (shape.color[0], shape.color[1] * n))
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
        self._angle = value

    def update(self, delta):
        pass


class Agent:
    """This Class represents an agent in the world"""
    def __init__(self):
        self.body = None
        self._actions = []
        self._perceptions = {}
        self.world = None

    def add_perception(self, perception):
        self._perceptions[perception.name] = perception
    
    def update(self, delta):
        if self.body != None:
            self.body.update(delta)
        
        self._update_perceptions()
        actions = self._think()
        for action in actions:
            self.action()
        
    def _update_perceptions(self):
        for p in self._perceptions.values():
            p.update(self)
    
    def _think(self):
        pass

class Perception:
    """A generic perception class."""

    def __init__(self, type = int, name = "None"):
        self.value = type()
        self.type = type
        self.name = name

    def update(self, agent):
        pass

    def __str__(self):
        return self.name

class World:
    """The environment where to put our agents and objects"""
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        self._agents = []
        self._objects = []
        pyglet.clock.schedule_interval(self.update, 1/60.0)

    
    def add_object(self, obj):
        self._objects.append(obj)
        
    def add_agent(self, agent):
        agent.world = self
        self._agents.append(agent)
        if agent.body != None:
            self._objects.append(agent.body)
        
    def update(self, delta):
        #update all objects
        for obj in self._objects:
            obj.update(delta)

        #process agents
        self.process_agents(delta)

    def process_agents(self, delta):
        for a in self._agents:
            a.update(delta)
    
    def draw(self):
        if self.batch == None:
            print("Pyglet batch needs to be set before call to draw.")
            return
        
    def draw_objects(self):
        for obj in self._objects:
            obj.draw()
            

class World2D(World):
    """A 2D continuous world"""
    
    def __init__(self, width=500, height=500):
        World.__init__(self)
        self.width = width
        self.height = height
        
        
class World2DGrid(World):
    """A 2D Grid world"""
    
    def __init__(self, width=50, height=50, cell=10, tor=False):
        World.__init__(self)
        self.width = width
        self.height = height
        self.tor = tor
        


class Display(pyglet.window.Window):
    '''Class used to display the world'''
    def __init__(self, world):
        #Init the pyglet super class
        super(Display, self).__init__(500, 500, caption = 'IIA')

        #Set wait for vertical sync to True
        self.set_vsync(True)
        
        self.show_fps = False
        self.fps_display = pyglet.clock.ClockDisplay()

        self.world = world
        
        
    #Events
    def on_draw(self):
        #clear window
        self.clear()
        
        #draw world to batch
        self.world.draw()
        
        #draw objects to batch
        self.world.draw_objects()
                
        #show fps
        if self.show_fps:
            self.fps_display.draw()
            
            
def run():
    pyglet.app.run()