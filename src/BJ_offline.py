import pgnull
from random import shuffle
from pgnull import utils

from pygame.math import Vector2

WIDTH, HEIGHT = utils.glob_singleton["window"]

y_spawn = 110

class Card(pgnull.Sprite):
    def __init__(self, card_ident, **kwargs):
        super().__init__(f"images/cards/{card_ident}.png", scale=2.5, **kwargs)
        self.card_ident = card_ident

class SpawnedCardsRenderer(pgnull.GameObject):
    cards = []

    @classmethod
    def add_card(cls, card):
        cls.cards.append(card)

    @classmethod
    def reset(cls):
        cls.cards = []

    def draw(self):
        for i in SpawnedCardsRenderer.cards:
            i.update_x_pos()
            i.draw()

    def update(self, ctx):
        # nur der vollständigkeit halber
        for i in SpawnedCardsRenderer.cards:
            i.update(ctx)

class SpawnedCard(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.idx = len(SpawnedCardsRenderer.cards)

    def update_x_pos(self):
        self.x = (WIDTH - (self.width * len(SpawnedCardsRenderer.cards))) / 2 + self.idx * self.width

class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-200,80), fontsize=50, font="PixelOperator8_Bold.ttf", text_color=(255,255,255))
        self.has_ace = False
        self.points = 0

    def update(self, ctx):
        self.points = 0
        self.has_ace = False
        for i in SpawnedCardsRenderer.cards:
            self.points += self.get_card_value(i.card_ident)

        if self.has_ace and self.points < 12:
            self.points += 10
            self.text =  str(self.points) + " / "  + str(self.points-10)
        else:
            self.text = str(self.points)

    def get_card_value(self, card_name):
        ident = card_name.split("_")[1]
        if ident.isdigit():
            return int(ident)
        elif ident == "A":
            self.has_ace = True
            return 1
        else:
            return 10

class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos=((WIDTH-self.width)/2, (HEIGHT-self.height)/2)

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))
        #self.stack = ["clubs_A", "clubs_Q", "clubs_05"]

        self.shuffle()

    def shuffle(self):
        shuffle(self.stack)
        self.pointer = 0
        SpawnedCardsRenderer.reset()
        self.active = True

    def on_click(self):
        self.draw_card()

    def draw_card(self):
        if self.pointer >= len(self.stack):
            return None

        draw = self.stack[self.pointer]

        SpawnedCardsRenderer.add_card(SpawnedCard(draw, pos=(WIDTH/2, y_spawn)))
        
        self.pointer+=1

        if self.pointer == len(self.stack):
            self.active = False

        return draw

class MainGame(pgnull.Scene):
    def __init__(self):
        super().__init__((18,112,58))

        bg = pgnull.Sprite("images/bg.png")
        bg.set_size(WIDTH, HEIGHT)
        bg.pos=(0,0)
        self.add_game_object(bg)

        self.stack = Stack()
        self.add_game_object(self.stack)

        self.add_game_object(SpawnedCardsRenderer())
        self.add_game_object(PointDisplay())

        self.stack.draw()
        self.stack.draw()

    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.stack.shuffle()
