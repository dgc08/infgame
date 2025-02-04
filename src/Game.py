import pgnull
from pgnull import utils

from pygame.math import Vector2

from .Player import Player

WIDTH, HEIGHT = utils.glob_singleton["window"]

class MainGame(pgnull.Scene):
    def __init__(self):
        super().__init__((0,0,0))

        player = Player()
        player.pos = (150,100)

        self.add_game_object(pgnull.Sprite("images/bg.png", scale=10))

        self.add_game_object(pgnull.Sprite("images/cook.png", pos=(150,200), scale=0.2))

        self.add_game_object(player)
