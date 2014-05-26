#coding: utf-8
#-----------------------------------------------------------------------------
# Copyright (c) 2014 Alexandre Pinto and Tiago Baptista
# All rights reserved.
#-----------------------------------------------------------------------------

"""
KB agents

"""

__docformat__ = 'restructuredtext'
__version__ = '1.0'
__author__ = 'Alexandre Pinto, Tiago Baptista'

#Allow the import of the framework from one directory down the hierarchy
import sys
sys.path.insert(1,'..')

import pyafai
import pyglet
from pyafai import shapes
import pyglet.window.key as key
import pyglet.window.mouse as mouse
import math
import heapq
import random


class Literal(object):
    def __init__(self, lit_string = ""):
        self._lit_string = lit_string

    def is_neg(self):
        return (self._lit_string[:4] == "not ")

    def get_atom(self):
        if self._lit_string[:4] == "not ":
            atom = self._lit_string[4:]
        else:
            atom = self._lit_string
        return atom

    def __str__(self):
        return self._lit_string

    def __repr__(self):
        return "Literal(" + self._lit_string + ")"


class Rule(object):
    def __init__(self, line):
        rulecomponents = line.split(":-")
        self.head = rulecomponents[0]
        self.head = self.head.strip(" .\n")
        self.body = ""
        if len(rulecomponents) > 1:
            self.body = rulecomponents[1]       
            self.body = self.body.split(",")
            for i in range(len(self.body)):
                lit = self.body.pop(0)
                lit = lit.strip(" .\n")
                self.body.append(Literal(lit))
        else:
            self.body = []

    def is_fact(self):
        return len(self.body) == 0

    def verify(self, work_mem):
        for lit in self.body:
            if lit.is_neg():
                if lit.get_atom() in work_mem:
                    return False
            elif lit.get_atom() not in work_mem:
                return False

        return True

    def __str__(self):
        if self.is_fact():
            return self.head + "."
        else:
            return self.head + " :- " + ", ".join([str(lit) for lit in self.body]) + "."

    def __repr__(self):
        return "Rule(" + str(self) + ")"


class KB(object):
    def __init__(self,kbfile):
        self.rules = []
        self.facts = []
        with open(kbfile) as f:
            for line in f:
                if line != "\n":
                    new_rule = Rule(line) # create new logic rule from text line in the kbfile
                    if (new_rule.is_fact()):
                        self.facts.append(new_rule)
                    else:
                        self.rules.append(new_rule)

    def add_fact(self, fact):
        rule = Rule(fact + '.')
        self.facts.append(rule)

    def remove_fact(self, fact):
        for f in self.facts:
            if f.head == fact:
                self.facts.remove(f)

    def match(self, work_mem, rule_list):
        res = []
        for rule in rule_list:
            if rule.verify(work_mem):
                res.append(rule)

        return res

    def select(self, valid_rules, rule_list):
        rule = valid_rules[0]
        rule_list.remove(rule)
        return rule

    def infer(self, perceptions):
        work_mem = [fact.head for fact in self.facts]
        work_mem.extend(perceptions)
        rule_list = self.rules[:]
        end = False
        result = []

        while not end:
            valid_rules = self.match(work_mem, rule_list)
            if len(valid_rules) > 0:
                rule = self.select(valid_rules, rule_list)
                work_mem.append(rule.head)
                if self.is_action(rule.head):
                    result.append(rule.head)

            else:
                end = True

        return result

    def is_action(self, string):
        if "(" in string:
            return True
        else:
            return False

    def __str__(self):
        res = "Facts:\n"
        res += '\n'.join([str(fact) for fact in self.facts])
        res += "\n\nRules:\n"
        res += '\n'.join([str(rule) for rule in self.rules])
        return res


class ShapePerception(pyafai.Perception):
    def __init__(self):
        super(ShapePerception, self).__init__(str, 'shape')

    def update(self, agent):
        objs = agent.world.get_cell_contents(agent.body.x, agent.body.y)
        if len(objs) > 0 and type(objs[0]) == Resource:
            self.value = objs[0].shape
        else:
            self.value = ''


class ColorPerception(pyafai.Perception):
    def __init__(self):
        super(ColorPerception, self).__init__(str, 'color')

    def update(self, agent):
        objs = agent.world.get_cell_contents(agent.body.x, agent.body.y)
        if len(objs) > 0 and type(objs[0]) == Resource:
            self.value = objs[0].color
        else:
            self.value = ''


class Resource(pyafai.Object):
    colors = {'red' : ('c3B',(255,0,0)), 'green' : ('c3B', (0,255,0)),
              'blue' : ('c3B', (0,0,255))}

    shapes = {'rectangle' : 'pyafai.shapes.Rect(10,10)',
              'circle' : 'pyafai.shapes.Circle(5)'}

    def __init__(self, x, y, color, shape):
        super(Resource, self).__init__(x, y)
        s = eval(Resource.shapes[shape])
        s.color = Resource.colors[color]
        self.add_shape(s)
        self.shape = shape
        self.color = color
        self.label = ""


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


class KBAgent(pyafai.Agent):
    def __init__(self, x, y, size = 10, kbfile = 'kb.txt'):
        super(KBAgent, self).__init__()

        #body
        self.body = pyafai.Object(x, y)
        self.body.add_shape(shapes.Triangle(-size/2, -size/2, size/2, 0, -size/2, size/2, color=('c3B',(200,0,0))))

        #perceptions
        self.add_perception(ShapePerception())
        self.add_perception(ColorPerception())

        #pathfinding
        self._target = None
        self._path = None
        self._timestep = 0.1
        self._elapsedtime = 0

        #kb
        self._home = (x, y)
        self._kb = KB(kbfile)
        self._inventory = []

    def set_target(self, x, y):
        self._target = (x, y)

        #invalidate existing path, if any
        if self._path is not None:
            self._path = None

    def execute_actions(self, actions):
        for a in actions:
            name = a[:a.index('(')]
            content = a[a.index('(')+1:-1]

            if name == 'get':
                objs = self.world.get_cell_contents(self.body.x, self.body.y)
                if len(objs) > 0 and type(objs[0]) == Resource:
                    objs[0].label = content
                    self._inventory.append(objs[0])
                    self._kb.add_fact('has(' + content + ')')
                    self.world.remove_object(objs[0])

            elif name == 'go':
                if content == 'home':
                    self.set_target(*self._home)

            elif name == 'add':
                self._kb.add_fact(content)

            elif name == 'remove':
                self._kb.remove_fact(content)

    def _think(self, delta):
        actions = []
        #If we are not already moving on a path
        if self._path is None:
            if self._target is None:
                #Do reasoning on knowledge base
                perceptions = [str(p.value) for p in self._perceptions.values()]
                actions = self._kb.infer(perceptions)
                if len(actions) == 0:
                    self._target = self.world.get_resource_location()
                else:
                    actions = self.execute_actions(actions)
            else:
                #calculate path using A*
                astar = AStar(self.world.graph)
                source = self.world.get_node_id(self.body.x, self.body.y)
                dest = self.world.get_node_id(self._target[0], self._target[1])
                self._path = astar.execute(source, dest, Heuristic(dest, self.world))
                self._target = None

        #else continue on the current path
        else:
            if len(self._path) > 0:
                self._elapsedtime += delta
                if self._elapsedtime >= self._timestep:
                    next_dest = self.world.get_location(self._path.pop(0))
                    angle = math.atan2(next_dest[1] - self.body.y,
                                       next_dest[0] - self.body.x)
                    self.body.angle = math.degrees(angle)
                    self.body.move_to(*next_dest)
                    self._elapsedtime = 0
            else:
                self._path = None

        return actions


class MyWorld(pyafai.World2DGrid):
    def __init__(self, width, height, cell):
        super(MyWorld, self).__init__(width, height, cell)

        self._nhood = pyafai.World2DGrid.von_neumann
        self._graph = Graph()
        self._gdisplay = GraphDisplay(self._graph, self, cell)
        self.showgraph = False

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

    def get_location(self, node):
        x = node % self._width
        y = node // self._width
        return x, y

    def get_node_id(self, x, y):
        return y*self._width + x

    def empty_location(self, x, y):
        obj_list = self.get_cell_contents(x, y)
        for obj in obj_list:
            self.remove_object(obj)

    def create_wall(self, x, y):
        self.empty_location(x, y)

        #create the wall
        wall = Wall(x, y)
        self.add_object(wall)


    def create_mountain(self, x, y, height):
        self.empty_location(x, y)

        #create the mountain
        mountain = Mountain(x, y, height)
        self.add_object(mountain)

    def create_random_resource(self):
        color = random.choice(list(Resource.colors.keys()))
        shape = random.choice(list(Resource.shapes.keys()))
        x = random.randint(0, self.grid_width - 1)
        y = random.randint(0, self.grid_height - 1)
        while (len(self.get_cell_contents(x, y)) > 0):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
        res = Resource(x, y, color, shape)
        self.add_object(res)

    def get_resource_location(self):
        res_list = []
        for obj in self._objects:
            if type(obj) == Resource:
                res_list.append(obj)

        if len(res_list) > 0:
            sel = random.choice(res_list)
            return (sel.x, sel.y)
        else:
            return (0, 0)


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
            if modifiers & key.MOD_SHIFT:
                self.world.empty_location(x1, y1)
            elif not (modifiers & key.MOD_CTRL):
                self.world.create_wall(x1, y1)
            else:
                self.world.create_mountain(x1, y1, 0.3)


def setup():
    """
    Setup a world with three resource items, one of each type.

    """
    world = MyWorld(20, 20, 20)
    display = MyDisplay(world)

    #create resources
    meat = Resource(random.randint(0,19), random.randint(0,19), 'red', 'rectangle')
    world.add_object(meat)
    veg = Resource(random.randint(0,19), random.randint(0,19), 'green', 'circle')
    world.add_object(veg)
    venom = Resource(random.randint(0,19), random.randint(0,19), 'blue', 'rectangle')
    world.add_object(venom)

    #create agent
    agent = KBAgent(0, 0, 15)
    world.add_agent(agent)


def setup_random():
    """
    Setup a random world, with walls and resource items at random locations.
    Note that there is no check to make sure that the type of resources that
    the agent needs exist in the world.

    """
    world = MyWorld(20, 20, 20)
    display = MyDisplay(world)

    #create some walls
    for i in range(100):
        x = 0
        y = 0
        while (x == 0 and y == 0):
            x = random.randint(0, world.grid_width-1)
            y = random.randint(0, world.grid_height-1)
        world.create_wall(x, y)
    world.generate_graph()

    #create resources
    for i in range(20):
        world.create_random_resource()

    #create agent
    agent = KBAgent(0, 0, 15, 'kb.txt')
    world.add_agent(agent)

if __name__ == '__main__':
    setup_random()
    pyafai.run()

    #test only the KB
    #mykb = KB("kb.txt")
    #print(mykb.infer(["red", "rectangle"]))


