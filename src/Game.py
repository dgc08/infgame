import pgnull
from random import shuffle
from pgnull import utils

from pygame.math import Vector2

from .Card import Card

WIDTH, HEIGHT = utils.glob_singleton["window"]

y_spawn = 110
clear_board = False

class SpawnedCard(Card):
    spawned = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idx = SpawnedCard.spawned
        SpawnedCard.spawned+=1

    def update(self, ctx):
        self.x = (WIDTH - (self.width * SpawnedCard.spawned)) / 2 + self.idx * self.width
        if clear_board:
            SpawnedCard.spawned = 0
            self.dequeue()

class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos=((WIDTH-self.width)/2, (HEIGHT-self.height)/2)

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))

        self.shuffle()

    def shuffle(self):
        shuffle(self.stack)
        self.pointer = 0
        self.active = True

    def on_click(self):
        draw = self.stack[self.pointer]

        print(draw)

        utils.glob_singleton["game"].scene.add_game_object(SpawnedCard(draw, pos=(WIDTH/2, y_spawn)))

        self.pointer+=1

        if self.pointer == len(self.stack):
            self.active = False
            
class MainGame(pgnull.Scene):
    def __init__(self):
        super().__init__((18,112,58))

        bg = pgnull.Sprite("images/bg.png")
        bg.set_size(WIDTH, HEIGHT)
        bg.pos=(0,0)
        self.add_game_object(bg)

        self.stack = Stack()
        self.add_game_object(self.stack)

    def on_update(self, ctx):
        global clear_board
        if clear_board:
            clear_board = False
