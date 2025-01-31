#!/usr/bin/env python3
import pgnull
from pgnull import utils

from pygame.math import Vector2

WIDTH = 640*2
HEIGHT = 480*2

utils.glob_singleton["window"] = (WIDTH,  HEIGHT)

from src.Lobby import Lobby

game = pgnull.Game(WIDTH, HEIGHT)

game.run_game(Lobby())
