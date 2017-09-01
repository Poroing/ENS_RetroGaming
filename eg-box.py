# basic moving box

import engine

WIDTH = 640
HEIGHT = 480

class Box(engine.GameObject):

    def __init__(self):
        self.speed = 0
        super().__init__(0, 0, 0, 0, 'square', 'red')

    def move(self):
        print('Speed: {}'.format(self.speed))
        self.y += self.speed
        self.speed -= 0.02

def getKeyboardCallback(box):
    def keyboard_callback(key):
        if key == 'space':
            print('You pushed space')
            print('Changing speed: {}'.format(box.speed))
            box.speed += 0.3
    return keyboard_callback
        
        

if __name__ == '__main__':
    engine.init_screen(WIDTH, HEIGHT)
    engine.init_engine()
    box = Box()
    engine.add_obj(box)
    engine.set_keyboard_handler(getKeyboardCallback(box))
    engine.engine()
