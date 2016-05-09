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
An agent framework for the Introduction to Artificial Intelligence course.
"""

from __future__ import division
import pyglet
import pyglet.window.key as key
from . import shapes

__docformat__ = 'restructuredtext'
__author__ = 'Tiago Baptista'


class Object(object):
    """This class represents a generic object in the world"""

    def __init__(self, x=0, y=0, angle=0.0):
        self.x = x
        self.y = y
        self._angle = angle
        self._batch = pyglet.graphics.Batch()
        self._shapes = []
        self._is_body = False
        self._agent = None
        self.scale = 1.0

    def __repr__(self):
        return str(type(self).__name__) + "(" + ",".join((str(self.x),
                                                          str(self.y),
                                                          str(self.angle))) + ")"

    @property
    def is_body(self):
        return self._is_body

    @property
    def agent(self):
        return self._agent

    @agent.setter
    def agent(self, agent):
        if agent is None:
            self._is_body = False
            self._agent = None
        else:
            self._is_body = True
            self._agent = agent

    def add_shape(self, shape):
        shape.add_to_batch(self._batch)
        self._shapes.append(shape)

    def clear_shapes(self):
        self._shapes.clear()

    def draw(self):
        pyglet.gl.glPushMatrix()
        pyglet.gl.glTranslatef(self.x, self.y, 0)
        pyglet.gl.glRotatef(self.angle, 0, 0, 1)
        if self.scale != 1:
            pyglet.gl.glScalef(self.scale, self.scale, self.scale)
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
        # normalize
        while value > 360:
            value -= 360
        while value < 0:
            value += 360

        self._angle = value

    def update(self, delta):
        pass

    def check_point(self, x, y):
        # Not yet implemented
        raise NotImplementedError


class Agent(object):
    """This Class represents an agent in the world"""

    def __init__(self):
        self.keep_body_on_death = False
        self._body = None
        self._actions = {}
        self._perceptions = {}
        self.world = None
        self._dead = False

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value):
        self._body = value
        if value is not None:
            value.agent = self

    @property
    def is_dead(self):
        return self._dead

    def add_perception(self, perception):
        self._perceptions[perception.name] = perception

    def add_action(self, action):
        self._actions[action.name] = action

    def update(self, delta):
        self._update_perceptions()
        actions = self._think(delta)
        if actions:
            for action in actions:
                action.execute(self)

    def kill(self):
        if not self._dead:
            self._dead = True
        else:
            print("Warning: Trying to kill an already dead agent!")

    def _update_perceptions(self):
        for p in self._perceptions.values():
            p.update(self)

    def _think(self, delta):
        return []


class Perception(object):
    """A generic perception class."""

    def __init__(self, t=int, name="None"):
        self.value = t()
        self.type = t
        self.name = name

    def update(self, agent):
        pass

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class Action(object):
    """A generic action class."""

    def __init__(self, name="None"):
        self.name = name

    def execute(self, agent):
        pass

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name


class World(object):
    """The environment where to put our agents and objects"""

    def __init__(self):
        self._batch = pyglet.graphics.Batch()
        self._agents = []
        self._dead_agents = []
        self._objects = []
        self._shapes = []
        self.paused = True
        pyglet.clock.schedule_once(self._start_schedule, 0.5)

    def add_object(self, obj):
        if isinstance(obj, Object):
            self._objects.append(obj)
        else:
            print("Trying to add an object to the world that is not of type \
            Object!")

    def remove_object(self, obj):
        if not obj.is_body and obj in self._objects:
            self._objects.remove(obj)
        else:
            print("Trying to remove an object that is not present in the \
            world, or is the body of an agent!")

    def add_agent(self, agent):
        if isinstance(agent, Agent):
            agent.world = self
            self._agents.append(agent)
            if agent.body is not None:
                self.add_object(agent.body)
        else:
            print("Trying to add an agent to the world that is not of type \
            Agent!")

    def _remove_agent(self, agent):
        if agent in self._agents:
            agent.world = None
            self._agents.remove(agent)
        else:
            print("Warning: Trying to remove an agent that is not in the list.")

    def pause_toggle(self):
        self.paused = not self.paused

    def _start_schedule(self, delta):
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)

    def update(self, delta):
        if not self.paused:
            # process agents
            self.process_agents(delta)

            # update all objects
            for obj in self._objects:
                obj.update(delta)

            # remove dead agents
            self._remove_dead_agents()

    def process_agents(self, delta):
        for a in self._agents:
            if not a.is_dead:
                a.update(delta)
            else:
                self._dead_agents.append(a)

    def _remove_dead_agents(self):
        for a in self._dead_agents:
            self._remove_agent(a)
            body = a.body
            a.body = None
            body.agent = None
            if not a.keep_body_on_death:
                self.remove_object(body)

        self._dead_agents.clear()

    def draw(self):
        self._batch.draw()

    def draw_objects(self):
        for obj in self._objects:
            obj.draw()


class World2D(World):
    """A 2D continuous and closed world"""

    def __init__(self, width=500, height=500):
        World.__init__(self)
        self.width = width
        self.height = height

    def update(self, delta):
        if not self.paused:
            # process agents
            self.process_agents(delta)

            # update all objects
            for obj in self._objects:
                obj.update(delta)

                # check bounds
                if obj.x > self.width:
                    obj.x = self.width
                if obj.y > self.height:
                    obj.y = self.height
                if obj.x < 0:
                    obj.x = 0
                if obj.y < 0:
                    obj.y = 0

            # remove dead agents
            self._remove_dead_agents()

    def get_object_at(self, x, y):
        """Return the first object found at the screen's (x, y) position,
        if any.

        :param x: The x position
        :param y: The y position
        """

        for obj in self._objects:
            if obj.check_point(x, y):
                return obj

        return None


class World2DGrid(World):
    """A 2D Grid world, closed, and optionally toroidal"""

    moore = ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1),
             (1, 1))
    von_neumann = ((-1, 0), (0, -1), (1, 0), (0, 1))

    def __init__(self, width=25, height=25, cell=20, tor=False,
                 nhood=moore, grid=True):
        World.__init__(self)
        self._width = width
        self._height = height
        self.width = width * cell
        self.height = height * cell
        self.cell = cell
        self._half_cell = cell / 2
        self._tor = tor
        self._nhood = nhood
        self._grid = [[[] for c in range(width)] for l in range(height)]

        # visual grid
        if grid:
            shape = shapes.Grid(width * cell, height * cell, cell)
            shape.add_to_batch(self._batch)
            self._shapes.append(shape)

    def add_object(self, obj):
        # check bounds
        if not self._tor:
            if obj.x > self._width - 1:
                obj.x = self._width - 1
            if obj.y > self._height - 1:
                obj.y = self._height - 1
            if obj.x < 0:
                obj.x = 0
            if obj.y < 0:
                obj.y = 0
        else:
            if obj.x > self._width - 0.5 or obj.x < -0.5:
                obj.x = round(obj.x) % self._width
            if obj.y > self._height - 0.5 or obj.y < -0.5:
                obj.y = round(obj.y) % self._height

        World.add_object(self, obj)
        self._grid[round(obj.y)][round(obj.x)].append(obj)

    def remove_object(self, obj):
        World.remove_object(self, obj)
        if not obj.is_body:
            self._grid[round(obj.y)][round(obj.x)].remove(obj)

    def process_agents(self, delta):
        for a in self._agents:
            if not a.is_dead:
                # remove body from grid
                self._grid[round(a.body.y)][round(a.body.x)].remove(a.body)

                a.update(delta)

                # re-add to grid
                self._grid[round(a.body.y)][round(a.body.x)].append(a.body)

            if a.is_dead:
                self._dead_agents.append(a)

    def update(self, delta):
        if not self.paused:
            # process agents
            self.process_agents(delta)

            # update all objects
            for obj in self._objects:

                # remove from _grid
                self._grid[round(obj.y)][round(obj.x)].remove(obj)

                obj.update(delta)

                # check bounds
                if not self._tor:
                    if obj.x > self._width - 1:
                        obj.x = self._width - 1
                    if obj.y > self._height - 1:
                        obj.y = self._height - 1
                    if obj.x < 0:
                        obj.x = 0
                    if obj.y < 0:
                        obj.y = 0
                else:
                    if obj.x > self._width - 0.5 or obj.x < -0.5:
                        obj.x = round(obj.x) % self._width
                    if obj.y > self._height - 0.5 or obj.y < -0.5:
                        obj.y = round(obj.y) % self._height

                # re-add to _grid
                self._grid[round(obj.y)][round(obj.x)].append(obj)

            # remove dead agents
            self._remove_dead_agents()

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
        return len(self._grid[int(round(y))][int(round(x))]) == 0

    def has_object_type_at(self, x, y, objtype):
        if self._tor:
            x = round(x) % self._width
            y = round(y) % self._height
        for obj in self._grid[y][x]:
            if isinstance(obj, objtype):
                return True

        return False

    def get_cell(self, x, y):
        return x // self.cell, y // self.cell

    def get_cell_contents(self, x, y):
        return self._grid[round(y)][round(x)]

    def get_neighbours(self, x, y):
        """Returns a list of all the objects that are neighbours of the cell
        at (x, y). The neighbourhood used is defined in _nhood.

        :param x: The cell's x coordinate (column).
        :param y: The cell's y coordinate (line).
        :return: A list with the neighbour objects.
        """
        result = []
        x = round(x)
        y = round(y)
        for dx, dy in self._nhood:
            x1 = x + dx
            y1 = y + dy
            if not self._tor and 0 <= x1 < self._width and \
                                    0 <= y1 < self._height:
                result.extend(self._grid[y1][x1])
            elif self._tor:
                x1 %= self._width
                y1 %= self._height
                result.extend(self._grid[y1][x1])

        return result

    def get_neighbourhood(self, x, y):
        """Returns a list of all the neighbour cells of a given cell at (x, y).
        Uses the neighbourhood defined in _nhood.

        :param x: The cell's x coordinate (column).
        :param y: The cell's y coordinate (line).
        :return: A list of tuples with (x, y) coordinates of the neighbor cells.
        """

        result = []
        x = round(x)
        y = round(y)
        for dx, dy in self._nhood:
            x1 = x + dx
            y1 = y + dy
            if not self._tor and 0 <= x1 < self._width and \
                                    0 <= y1 < self._height:
                result.append((x1, y1))
            elif self._tor:
                x1 %= self._width
                y1 %= self._height
                result.append((x1, y1))

        return result


class Display(pyglet.window.Window):
    """Class used to display the world"""

    def __init__(self, world, multisampling=True):
        if multisampling:
            # Enable multismapling if available on the hardware
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

        # Get the width and height of the world
        if hasattr(world, 'width') and hasattr(world, 'height'):
            width = world.width
            height = world.height
        else:
            width = 500
            height = 500

        if multisampling:
            # Init the pyglet super class
            super(Display, self).__init__(width, height, caption='IIA',
                                          config=config)
        else:
            super(Display, self).__init__(width, height, caption='IIA')

        self.show_fps = False
        self.fps_display = pyglet.clock.ClockDisplay()

        self.world = world
        if self.world.paused:
            self.set_caption(self.caption + " (paused)")
        else:
            self.set_caption(self.caption.replace(" (paused)", ""))

    def on_draw(self):
        # clear window
        self.clear()

        # draw world
        self.world.draw()

        # draw objects
        self.world.draw_objects()

        # show fps
        if self.show_fps:
            self.fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        super(Display, self).on_key_press(symbol, modifiers)

        if symbol == key.F:
            self.show_fps = not (self.show_fps)
        elif symbol == key.SPACE:
            self.world.pause_toggle()
            if self.world.paused:
                self.set_caption(self.caption + " (paused)")
            else:
                self.set_caption(self.caption.replace(" (paused)", ""))

    def on_mouse_release(self, x, y, button, modifiers):
        pass
