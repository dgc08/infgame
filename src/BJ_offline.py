import pgnull
from random import shuffle
from pgnull import utils

from pygame.math import Vector2

from .Card import Card

WIDTH, HEIGHT = utils.glob_singleton["window"]

y_spawn = 110

def get_card_value():
    pass

class SpawnedCard(Card):
    spawned = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idx = SpawnedCard.spawned
        SpawnedCard.spawned+=1

    def update_x_pos(self):
        self.x = (WIDTH - (self.width * SpawnedCard.spawned)) / 2 + self.idx * self.width

class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-100,100), fontsize=50, font="PixelOperator8_Bold.ttf", text_color=(255,255,255))

class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos=((WIDTH-self.width)/2, (HEIGHT-self.height)/2)

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))

        self.drawn_cards = []

        self.shuffle()

    def shuffle(self):
        shuffle(self.stack)
        self.pointer = 0
        self.drawn_cards = []
        SpawnedCard.spawned = 0
        self.active = True

    def on_click(self):
        print(self.draw_card())

    def draw_card(self):
        if self.pointer >= len(self.stack):
            return None

        draw = self.stack[self.pointer]

        self.drawn_cards.append(SpawnedCard(draw, pos=(WIDTH/2, y_spawn)))
        
        self.pointer+=1

        return draw

    def draw(self):
        if self.pointer != len(self.stack):
            # if stack not empty, draw stack
            super().draw()

        # always draw already drawn cards
        for i in self.drawn_cards:
            i.update_x_pos()
            i.draw()
            
class MainGame(pgnull.Scene):
    def __init__(self):
        super().__init__((18,112,58))

        bg = pgnull.Sprite("images/bg.png")
        bg.set_size(WIDTH, HEIGHT)
        bg.pos=(0,0)
        self.add_game_object(bg)

        self.stack = Stack()
        self.add_game_object(self.stack)

        self.add_game_object(PointDisplay())

    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.stack.shuffle()
