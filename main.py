#!/usr/bin/env python3
import pgnull
from pgnull import utils

from pygame.math import Vector2

WIDTH = 600*2.75
HEIGHT = 300*2.75

utils.glob_singleton["window"] = (WIDTH,  HEIGHT)

### LOAD FIRST SCENE ###

from src.Lobby import Lobby
from src.BJ_offline import MainGame

game = pgnull.Game(WIDTH, HEIGHT, "Blackjack with Pygame")

while True:
    game.run_game(Lobby()) # Uncomment for release / showcase, leave commented for debug
