import pyafai
from pyafai import shapes
from pyafai import objects

if __name__ == '__main__':
    world = pyafai.World()
    display = pyafai.Display(world)

    obj = pyafai.Object(200,200)
    shape = shapes.Circle(10)
    obj.add_shape(shape)
    world.add_object(obj)

    obj2 = objects.SimplePhysicsObject(150,150)
    shape = shapes.Triangle(0, -10, 20, 0, 0, 10)
    obj2.add_shape(shape)
    world.add_object(obj2)
    obj2.ang_velocity = 45
    obj2.velocity = 100

    pyafai.run()
