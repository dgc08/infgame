import pgnull
from pgnull import utils

from pygame.math import Vector2

from .Player import Player

WIDTH, HEIGHT = utils.glob_singleton["window"]

class MainGame(pgnull.Scene):
    def __init__(self):
        super().__init__((0,0,0))
        self.add_game_object(Player())
