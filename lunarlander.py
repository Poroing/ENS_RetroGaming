# basic moving box

import engine
import turtle
import time
import numpy as np
import numpy.linalg as linalg
from enum import Enum
import operator
import copy

WIDTH = 640
HEIGHT = 480

class Direction(Enum):
    LEFT = 0
    RIGHT = 1
    TOP = 2
    BOTTOM = 3

def isFurther(direction, value1, value2):
    if isinstance(value1, Vec2D):
        return isFurther(
            direction,
            value1.getDirectionRelevantValue(direction),
            value2)
    if isinstance(value2, Vec2D):
        return isFurther(
            direction,
            value1.getDirectionRelevantValue(direction),
            value2)
    if isIncreasingDirection(direction):
        return value1 > value2
    return value1 < value2
        
def getOpposingDirection(direction):
    if direction is Direction.LEFT:
        return Direction.RIGHT
    if direction is Direction.RIGHT:
        return Direction.LEFT
    if direction is Direction.BOTTOM:
        return Direction.TOP
    if direction is Direction.TOP:
        return Direction.BOTTOM

def isIncreasingDirection(direction):
    return direction is Direction.TOP or direction is Direction.RIGHT

def isDirectionRelevantToX(direction):
    return direction is Direction.RIGHT or direction is Direction.LEFT


class Vec2D(object):

    def __init__(self, x, y=None):
        if y is None:
            self.vector = np.array(list(map(float, x)))
        else:
            self.vector = np.array([float(x), float(y)])

    def pointIsInDirection(self, direction, point):
        relative_distance_to_center = (
            point.getDirectionRelevantValue(direction) 
            - self.getDirectionRelevantValue(direction))

        if isIncreasingDirection(direction):
            return relative_distance_to_center > 0
        return relative_distance_to_center < 0

    def getDistanceSquaredToPoint(self, point):
        return (point - self).length_squared

    def getDistanceToPoint(self, point):
        return (point - self).length

    def __iter__(self):
        yield self.x
        yield self.y

    @property
    def length(self):
        return np.sqrt(self.length_squared)

    @property
    def length_squared(self):
        return self.x * self.x + self.y * self.y

    @property
    def x(self):
        return self.vector[0]

    @property
    def y(self):
        return self.vector[1]

    @x.setter
    def x(self, value):
        self.vector[0] = value

    @y.setter
    def y(self, value):
        self.vector[1] = value

    def getDirectionRelevantValue(self, direction):
        if isDirectionRelevantToX(direction):
            return self.x
        return self.y

    def setDirectionRelevantValue(self, direction, value):
        if isDirectionRelevantToX(direction):
            self.x = value
        else:
            self.y = value

    def __iadd__(self, other):
        self.vector += other.vector
        return self

    def __add__(self, other):
        return Vec2D(self.vector + self.vector)

    def __isub__(self, other):
        self.vector -= other.vector
        return self

    def __sub__(self, other):
        return Vec2D(self.vector - other.vector)

    def getRotatedVec2D(self, angle):
        angle = np.radians(angle)
        rotation_matrix = np.array([
            [ np.cos(angle), -np.sin(angle) ],
            [ np.sin(angle), np.cos(angle) ] ])
        return Vec2D(np.matmul(rotation_matrix, self.vector))

    def rotate(self, angle):
        self.vector = self.getRotatedVec2D(angle).vector

    def __imul__(self, scalar):
        self.vector *= scalar
        return self

    def __mul__(self, scalar):
        return Vec2D(self.vector * scalar)

    def __rmul__(self, scalar):
        return Vec2D(self.vector * scalar)

    def __eq__(self, other):
        return self.vector == other.vector

    def __repr__(self):
        return f'Vec2D({self.x}, {self.y})'

class Positionable(object):

    def __init__(self, position):
        self.position = position

    @property
    def x(self):
        return self.position.x

    @x.setter
    def x(self, value):
        print(f'Setting x: {value}')
        self.position.x = value

    @property
    def y(self):
        return self.position.y

    @y.setter
    def y(self, value):
        print(f'Setting y: {value}')
        self.position.y = value

class Circle(Positionable):

    def __init__(self, position, radius):
        super().__init__(position)
        self.radius = radius

    def overlapCircle(self, circle):
        return (self.position.getDistanceToPoint(circle.position)
            < self.radius + circle.radius)

class Rectangle(Positionable):

    def __init__(self, position, height, width):
        super().__init__(position)
        self.height = height
        self.width = width

    def pointIsInDirection(self, direction, point):
        return isFurther(direction, point, self.getDirectionPosition(direction))

    @property
    def left_position(self):
        return self.position.x

    @property
    def right_position(self):
        return self.position.x + self.width

    @property
    def top_position(self):
        return self.position.y + self.height

    @property
    def bottom_position(self):
        return self.position.y

    @property
    def center(self):
        return self.position + Vec2D(self.width / 2, self.height / 2)

    def pointIsInside(self, point):
        return self.getPointDirection(point) is None

    def getPointDirection(self, point):
        for direction in Direction:
            if self.pointIsInDirection(direction, point):
                return direction
        return None

    def getDirectionPosition(self, direction):
        if direction is Direction.LEFT:
            return self.left_position
        if direction is Direction.RIGHT:
            return self.right_position
        if direction is Direction.TOP:
            return self.top_position
        if direction is Direction.BOTTOM:
            return self.bottom_position

class Screen(Rectangle, engine.GameObject):

    def __init__(self, width, height):
        super().__init__(Vec2D(0, 0), width, height)
        engine.GameObject.__init__(
            self,
            -self.width / 2, 
            -self.height / 2,
            0,
            0,
            'nothing',
            'white')

    def convertIntoEngineCoordinate(self, point):
        return point - self.center

    def convertFromEngineCoordinate(self, point):
        return point + self.center

    def getWarpingPoint(self, point):
        if self.pointIsInside(point):
            return point
        warping_point = copy.deepcopy(point)
        point_direction = self.getPointDirection(point)
        warping_point.setDirectionRelevantValue(
            point_direction,
            self.getDirectionPosition(getOpposingDirection(point_direction)))
        return warping_point

    def isoob(self):
        return False



GRAVITY = Vec2D(0, 0)

def banner(s):
	turtle.home()
	turtle.color('red')
	turtle.write(s, True, align='center', font=('Arial', 48, 'italic'))
	time.sleep(3)
	turtle.undo()

def isOut(x, y):
    return abs(x) > WIDTH / 2 or abs(y) > HEIGHT / 2

class LunarLander(Circle, engine.GameObject):
    MOTOR_ACCELERATION = Vec2D(0.1, 0)
    TURN_STEP = 10
    SLOWING_FACTOR = 0.95
    RADIUS = 30

    def __init__(self):
        self.angle = 90
        super().__init__(Vec2D(0, 0), LunarLander.RADIUS)
        engine.GameObject.__init__(self, 0, 0, 0, 0, 'lunar_lander', 'black')
        self.speed = Vec2D(0, 0)
        self.motor_enable = False

    def heading(self):
        return self.angle

    def move(self):
        global GRAVITY

        print(self.speed)

        self.speed += GRAVITY
        self.speed *= LunarLander.SLOWING_FACTOR

        if self.motor_enable:
            self.speed += (
                LunarLander.MOTOR_ACCELERATION.getRotatedVec2D(self.heading()))
        
        self.position += self.speed

    def isoob(self):
        return False

    def turnLeft(self):
        self.angle += LunarLander.TURN_STEP
    
    def turnRight(self):
        self.angle -= LunarLander.TURN_STEP

    def toggleMotor(self):
        self.motor_enable = not self.motor_enable

class Sun(Circle, engine.GameObject):
    RADIUS = 50

    def __init__(self):
        super().__init__(Vec2D(HEIGHT / 2 - 2, 0), Sun.RADIUS)
        engine.GameObject.__init__(self,
            0,
            HEIGHT / 2 - 2,
            0,
            0,
            'sun',
            'yellow')

class Ground(engine.GameObject):

    def __init__(self):
        super().__init__(0, - HEIGHT / 2 , 0, 0, 'ground', 'black')

    def heading(self):
        return 90


#========
# Shapes
#=======

def getCircle(n, radius):
    turtle.begin_poly()
    vertice = Vec2D(radius, 0)
    for i in range(n):
        vertice.rotate(i * 360 / n)
        turtle.goto(vertice)
    turtle.end_poly()
    return turtle.get_poly()

def addGroundToEngine():
    rectange = turtle.Shape('compound')
    rectange_vertices = [
        (-WIDTH / 2, 0),
        (WIDTH / 2, 0),
        (WIDTH / 2, 30),
        (-WIDTH / 2, 30) ]
    rectange.addcomponent(rectange_vertices, 'black', 'black')
    turtle.register_shape('ground', rectange)

def addNothingToEngine():
    turtle.begin_poly()
    turtle.end_poly()
    turtle.register_shape('nothing', turtle.get_poly())

def addSunToEngine():
    turtle.register_shape('sun', getCircle(100, Sun.RADIUS))

def addLunarLanderToEngine():
    turtle.begin_poly()
    turtle.goto(-15, 10)
    turtle.goto(0, 20)
    turtle.goto(15, 10)
    turtle.goto(15, 0)
    turtle.goto(11, 0)
    turtle.goto(11, 8)
    turtle.goto(7, 6)
    turtle.goto(-7, 6)
    turtle.goto(-11, 8)
    turtle.goto(-11, 0)
    turtle.end_poly()
    lunar_lander_poly = turtle.get_poly()
    turtle.register_shape('lunar_lander', lunar_lander_poly)

def addShapesToEngine():
    addLunarLanderToEngine()
    addSunToEngine()
    addGroundToEngine()
    addNothingToEngine()

#===========
# Collision
#===========

def registerCollisionCallback(Class1, Class2, callback):
    engine.register_collision(Class1, Class2, callback)
    engine.register_collision(
        Class2,
        Class1,
        lambda instance2, instance1: callback(instance1, instance2))

def collision_callback_screen_lander(screen, lander):
    print(f'Position: {lander.position}')
    lander_screen_position = screen.convertFromEngineCoordinate(lander.position)
    if not screen.pointIsInside(lander_screen_position):
        warping_point = screen.getWarpingPoint(lander_screen_position)
        lander.position = screen.convertIntoEngineCoordinate(warping_point)

def collision_cb_SL(sun, lander):
    if sun.overlapCircle(lander):
        banner('You are burning')
    
def registerCollisionCallbacks():
    registerCollisionCallback(Sun, LunarLander, collision_cb_SL)
    registerCollisionCallback(Screen, LunarLander, collision_callback_screen_lander)

#==========
# Keyboard
#==========

def getLunarLanderKeyboardCallback(lunar_lander):
    def keyboard_callback(key):
        if key == 'space':
            lunar_lander.toggleMotor()
        if key == 'h':
            lunar_lander.turnLeft()
        if key == 'l':
            lunar_lander.turnRight()
        
    return keyboard_callback

        
if __name__ == '__main__':
    engine.init_screen(WIDTH, HEIGHT)
    engine.init_engine()

    addShapesToEngine()

    screen = Screen(WIDTH, HEIGHT)
    engine.add_obj(screen)

    lander = LunarLander()
    engine.add_obj(lander)

    engine.add_obj(Sun())
    engine.add_obj(Ground())

    registerCollisionCallbacks()

    engine.set_keyboard_handler(getLunarLanderKeyboardCallback(lander))
    engine.engine()
