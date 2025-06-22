import pgnull
from pgnull import utils

from pygame.math import Vector2

from .BJ_common import MainGame

from .BJ_singleplayer import SingleplayerGameState

WIDTH, HEIGHT = utils.glob_singleton["window"]
box_w = Vector2(360, 80)

box_space = 100
y_box_1 = (HEIGHT - (box_w.y*2)) / 2

class StartButton(pgnull.Sprite):
    def __init__(self):
        super().__init__("images/gui/start_button.png", ((WIDTH-box_w.x)/2, y_box_1))

    def on_click(self):
        # parent = lobby object
        # parent.parent = game
        self.parent.parent.load_scene(MainGame(SingleplayerGameState())) # for now only singleplayer

class ExitButton(pgnull.Sprite):
    def __init__(self):
        super().__init__("images/gui/quit_button.png", ((WIDTH-box_w.x)/2, y_box_1+100))

    def on_click(self):
        self.parent.parent.quit()


# Szenen sind jetzt auch nur GameObjects
class Lobby(pgnull.GameObject):
    def __init__(self):
        super().__init__()
        bg = pgnull.Sprite("images/bg.png")
        bg.set_size(WIDTH, HEIGHT)
        bg.pos=(0,0)
        self.reg_obj(bg)

        self.reg_obj(StartButton())
        self.reg_obj(ExitButton())
