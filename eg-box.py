# basic moving box

import engine
import turtle
import time

WIDTH = 640
HEIGHT = 480

class Vec2D(turtle.Vec2D):

    @property
    def x(self):
        x, y = self
        return x

    @property
    def y(self):
        x, y = self
        return y

    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)

    def rotate(self, angle):
        x, y = super().rotate(angle)
        return Vec2D(x, y)

GRAVITY = Vec2D(0, -0.05)

def banner(s):
	turtle.home()
	turtle.color('red')
	turtle.write(s, True, align='center', font=('Arial', 48, 'italic'))
	time.sleep(3)
	turtle.undo()

class LunarLander(engine.GameObject):
    MOTOR_ACCELERATION = Vec2D(0.10, 0)

    def __init__(self):
        super().__init__(0, 0, 0, 0, 'lunar_lander', 'black')
        self.speed = Vec2D(0, 0)
        self.motor_enable = False

    @property
    def position(self):
        return Vec2D(self.x, self.y)

    @position.setter
    def position(self, value):
        self.x = value.x
        self.y = value.y

    def heading(self):
        return 90

    def move(self):
        global GRAVITY
        self.speed = self.speed + GRAVITY

        if self.motor_enable:
            self.speed = self.speed + LunarLander.MOTOR_ACCELERATION.rotate(self.heading())
        
        self.position = self.position + self.speed

        if self.y > HEIGHT / 2 - 50:
            banner('Aaaaaah')
            engine.exit_engine()

        if self.y < -HEIGHT / 2 + 30:
            if abs(self.speed.y) > 2:
                banner('Yo Dead')
            else:
                banner('Landed')
            engine.exit_engine()

    def toggleMotor(self):
        self.motor_enable = not self.motor_enable

class Sun(engine.GameObject):

    def __init__(self):
        super().__init__(0, HEIGHT / 2 - 2, 0, 0, 'sun', 'yellow')

class Ground(engine.GameObject):

    def __init__(self):
        super().__init__(0, - HEIGHT / 2 , 0, 0, 'ground', 'black')

    def heading(self):
        return 90

def getCircle(n, radius):
    turtle.begin_poly()
    vertice = Vec2D(radius, 0)
    for i in range(n):
        vertice = vertice.rotate(i * 360 / n)
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

def addSunToEngine():
    turtle.register_shape('sun', getCircle(100, 50))

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

def getLunarLanderKeyboardCallback(lunar_lander):
    def keyboard_callback(key):
        if key == 'space':
            lunar_lander.toggleMotor()
    return keyboard_callback

if __name__ == '__main__':
    engine.init_screen(WIDTH, HEIGHT)
    engine.init_engine()

    addLunarLanderToEngine()
    addSunToEngine()
    addGroundToEngine()

    lander = LunarLander()
    engine.add_obj(lander)
    engine.add_obj(Sun())
    engine.add_obj(Ground())
    engine.set_keyboard_handler(getLunarLanderKeyboardCallback(lander))
    engine.engine()
