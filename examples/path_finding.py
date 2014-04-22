#! /usr/bin/env python
#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
Pathfinding example using the A* algorithm.

"""

__docformat__ = 'restructuredtext'
__version__ = '1.0'
__author__ = 'Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyglet
import pyafai
from pyafai import shapes
import math
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import heapq


class Graph(object):
    def __init__(self):
        self._graph = {}

    def add_node(self, node, connections):
        self._graph[node] = connections

    def get_connections(self, node):
        return self._graph.get(node, [])

    def clear(self):
        self._graph = {}

    def get_nodes(self):
        return self._graph.keys()

    def __len__(self):
        return len(self._graph)

    def __iter__(self):
        return self._graph.__iter__()


class Node(object):
    def __init__(self, node, g, h, previous=None):
        self.node = node
        self.g = g
        self.h_g = h+g
        self.previous = previous

    def __hash__(self):
        return self.node.__hash__()

    def __eq__(self, other):
        return self.node == other.node

    def __ne__(self, other):
        return self.node != other.node

    def __gt__(self, other):
        return self.h_g > other.h_g

    def __ge__(self, other):
        return self.h_g >= other.h_g

    def __lt__(self, other):
        return self.h_g < other.h_g

    def __le__(self, other):
        return self.h_g <= other.h_g

    def __str__(self):
        return "(" + ",".join((str(self.node), str(self.g),
                               str(self.h_g))) + ")"

    def __repr__(self):
        return "Node(" + ",".join((repr(self.node), repr(self.g),
                                   repr(self.h_g - self.g),
                                   repr(self.previous))) + ")"


class Heuristic(object):
    def __init__(self, dest_node, world):
        self._dest = dest_node
        self._world = world
        self._x, self._y = world.get_location(dest_node)

    def calculate(self, node):
        x, y = self._world.get_location(node)
        return math.sqrt((x-self._x)**2 + (y - self._y)**2)


class AStar(object):
    def __init__(self, graph):
        self._graph = graph

    def _build_path(self, final_node):
        path = [final_node.node]
        prev = final_node.previous
        while prev is not None:
            path.insert(0, prev.node)
            prev = prev.previous

        path.pop(0)
        return path

    def execute(self, source, dest, hfunc):
        start_node = Node(source, 0, hfunc.calculate(source))
        openset = [start_node]
        heapq.heapify(openset)
        closedset = []

        while len(openset) > 0:
            cur = heapq.heappop(openset)

            if cur.node == dest:
                return self._build_path(cur)

            for conn in self._graph.get_connections(cur.node):
                next_node = Node(conn[0], cur.g + conn[1],
                                 hfunc.calculate(conn[0]), cur)
                if next_node not in closedset:
                    if next_node in openset:
                        cur_node = openset[openset.index(next_node)]
                        if next_node < cur_node:
                            openset.remove(cur_node)
                            heapq.heappush(openset, next_node)
                    else:
                        heapq.heappush(openset, next_node)

            heapq.heappush(closedset, cur)

        return None

class Wall(pyafai.Object):
    def __init__(self, x, y):
        super(Wall, self).__init__(x, y)

        self.add_shape(shapes.Rect(20, 20, color=('c3B',(255,255,255))))


class Mountain(pyafai.Object):
    def __init__(self, x, y, height):
        super(Mountain, self).__init__(x, y)

        self.height = height
        self.add_shape(shapes.Rect(20, 20, color=('c3B', (int(255*height),
                                                          int(255*height),
                                                          0))))


class Wanderer(pyafai.Agent):
    def __init__(self, x, y, size = 10):
        super(Wanderer, self).__init__()

        self.body = pyafai.Object(x, y)
        self.body.add_shape(shapes.Circle(size/2, color=('c3B',(200,0,0))))

        self._target = None
        self._path = None
        self._timestep = 0.2
        self._elapsedtime = 0

    def set_target(self, x, y):
        self._target = (x, y)

        #invalidate existing path, if any
        if self._path is not None:
            self._path = None

    def _think(self, delta):
        #If we are not already moving on a path
        if self._path is None:
            if self._target is not None:
                #calculate path using A*
                astar = AStar(self.world.graph)
                source = self.world.get_node_id(self.body.x, self.body.y)
                dest = self.world.get_node_id(self._target[0], self._target[1])
                self._path = astar.execute(source, dest, Heuristic(dest, self.world))
                self._target = None

        else:
            if len(self._path) > 0:
                self._elapsedtime += delta
                if self._elapsedtime >= self._timestep:
                    next_dest = self.world.get_location(self._path.pop(0))
                    self.body.move_to(*next_dest)
                    self._elapsedtime = 0
            else:
                self._path = None

        return []


class MyWorld(pyafai.World2DGrid):
    def __init__(self, width, height, cell):
        super(MyWorld, self).__init__(width, height, cell)

        self._nhood = pyafai.World2DGrid.von_neumann
        self._graph = Graph()
        self._gdisplay = GraphDisplay(self._graph, self, cell)
        self.showgraph = False

        self.player = Wanderer(10, 10, 15)
        self.add_agent(self.player)

        self.generate_graph()

    def draw(self):
        super(MyWorld, self).draw()
        if self.showgraph:
            self._gdisplay.draw()

    @property
    def graph(self):
        return self._graph

    def generate_graph(self):
        """
        Generate the graph structure for the current state of the environment.

        """
        self._graph.clear()
        for x in range(self._width):
            for y in range(self._height):

                #verify if current cell is a wall
                is_wall = self.has_object_type_at(x, y, Wall)

                #if it is not a wall, calculate connections and weights
                if not is_wall:
                    neighbours = self.get_neighbours(x, y)
                    connections = []
                    for dx,dy in self._nhood :
                        x1 = x + dx
                        y1 = y + dy
                        if 0 <= x1 < self._width and 0 <= y1 < self._height:
                            weight = math.sqrt((x1-x)**2 + (y1-y)**2)
                            for obj in neighbours:
                                if obj.x == x1 and obj.y == y1:
                                    if type(obj) == Wall:
                                        weight = 0
                                    if type(obj) == Mountain:
                                        weight = weight * 10 * obj.height

                            if weight != 0:
                                connections.append((y1*self._width + x1, weight))

                    self._graph.add_node(y * self._width + x, connections)

        self._gdisplay = GraphDisplay(self._graph, self, self.cell)

    def send_player_to(self, x, y):
        if not self.has_object_type_at(x, y, Wall):
            self.player.set_target(x, y)

    def get_location(self, node):
        x = node % self._width
        y = node // self._width
        return x, y

    def get_node_id(self, x, y):
        return y*self._width + x


class GraphDisplay(object):
    def __init__(self, graph, world, cell):
        self._batch = pyglet.graphics.Batch()
        self._node_shapes = [None] * (world.grid_width * world.grid_height)
        self._conn_shapes = []

        half_cell = cell/2
        color = ('c4B', (150,150,150,100))


        #create nodes
        for node in graph.get_nodes():
            x, y = world.get_location(node)
            shape = shapes.Circle(4, cell*x+half_cell, cell*y+half_cell,
                                  color = color)
            shape.add_to_batch(self._batch)
            self._node_shapes[node] = shape

        #create connections
        for node in graph.get_nodes():
            x1, y1 = world.get_location(node)
            for dest in graph.get_connections(node):
                x2, y2 = world.get_location(dest[0])
                shape = shapes.Line(cell*x1+half_cell, cell*y1+half_cell,
                                    cell*x2+half_cell, cell*y2+half_cell,
                                    color = color)
                shape.add_to_batch(self._batch)
                self._conn_shapes.append(shape)

    def draw(self):
        self._batch.draw()


class MyDisplay(pyafai.Display):

    def on_key_press(self, symbol, modifiers):
        super(MyDisplay, self).on_key_press(symbol, modifiers)

        if symbol == key.G:
            self.world.generate_graph()

        if symbol == key.D:
            self.world.showgraph = not self.world.showgraph

    def on_mouse_release(self, x, y, button, modifiers):
        super(MyDisplay, self).on_mouse_release(x, y, button, modifiers)

        if button == mouse.RIGHT:
            x1, y1 = self.world.get_cell(x, y)
            if not (modifiers & key.MOD_CTRL):
                wall = Wall(x1, y1)
                self.world.add_object(wall)
            else:
                mountain = Mountain(x1, y1, 0.3)
                self.world.add_object(mountain)
        elif button == mouse.LEFT:
            x1, y1 = self.world.get_cell(x, y)
            self.world.send_player_to(x1, y1)


def setup():
    world = MyWorld(20, 20, 20)
    display = MyDisplay(world)


if __name__ == '__main__':
    setup()
    pyafai.run()


