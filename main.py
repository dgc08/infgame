#!/usr/bin/env python3
import pgnull
from pgnull import utils

# Diese Datei initalisiert pygame bzw pgnull un lädt die erste Szene
# diese datei ist extra kurz gehalten, sodass man das spiel zwar einfach aus dem haupt directory starten kann aber der meiste quellcode trotzdem in src/ liegt

# 600x300 ist die größe des hintergrunds, das wird dann noch um irgendeinen faktor vergrößert und dann als fenstergröße genommen
WIDTH = 600*2.75
HEIGHT = 300*2.75

utils.glob_singleton["window"] = (WIDTH,  HEIGHT)

game = pgnull.Game(WIDTH, HEIGHT, "Blackjack with Pygame")

### LOAD FIRST SCENE ###
from src.Lobby import Lobby

while True:
    # die lobby-szene ist in einer eigenen Klasse und
    game.run_game(Lobby())
