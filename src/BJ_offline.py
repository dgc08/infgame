from random import shuffle

import pgnull
from pgnull import utils

from pygame.math import Vector2

WIDTH, HEIGHT = utils.glob_singleton["window"]

from .Panes import VerticalPane

class Card(pgnull.Sprite):
    def __init__(self, card_ident, **kwargs):
        super().__init__(f"images/cards/{card_ident}.png", scale=2.5, **kwargs)
        self.card_ident = card_ident


class SpawnedCard(Card):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_card_number = -1

    def on_start(self):
        self.idx = len(self.parent.cards)
        print(self.idx)
        self.realign()

    def realign(self):
        self.last_card_number = len(self.parent.cards)
        self.x = (WIDTH - (self.width * self.last_card_number)) / 2 + self.idx * self.width

    def on_update(self, ctx):
        super().on_update(ctx)
        if self.last_card_number != len(self.parent.cards):
            # update position if a card got added
            self.realign()


class SpawnedCardsScene(pgnull.GameObject):
    # i am to lazy to rewrite this with HorizontalPane
    def __init__(self):
        super().__init__()
        self.pos.y = 150
        self.cards = []

    def add_game_object(self, game_obj):
        super().add_game_object(game_obj)
        if isinstance(game_obj, SpawnedCard):
            self.cards.append(game_obj.card_ident)

    def reset(self):
        self.cards = []
        for i in self._game_objs:
            i.dequeue()


class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos = ((WIDTH-self.width)/2, ((HEIGHT-self.height)/2) + 30 )

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))
        # self.stack = ["clubs_A", "clubs_Q", "clubs_05"]

    def on_start(self):
        self.shuffle()

    def shuffle(self):
        shuffle(self.stack)
        self.pointer = 0
        self.active = True

        #draw two cards
        self.draw_card()
        self.draw_card()

    def on_click(self):
        self.draw_card()

    def draw_card(self):
        if self.pointer >= len(self.stack):
            return None

        draw = self.stack[self.pointer]

        self.parent.spawned_cards.reg_obj(
            SpawnedCard(draw),
            None
        )

        self.pointer += 1

        if self.pointer == len(self.stack):
            self.active = False

        return draw


class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-200, 50), fontsize=50,
                         font="PixelOperator8_Bold.ttf", text_color=(255, 255, 255))
        self.has_ace = False
        self.points = 0

        self.last_card_number = -1

    def on_update(self, ctx):
        if self.last_card_number == len(self.parent.spawned_cards.cards):
            # no card got added, do nothing
            return
        # a card got added or removed

        self.last_card_number = len(self.parent.spawned_cards.cards)

        self.points = 0
        self.has_ace = False
        for i in self.parent.spawned_cards.cards:
            self.points += self.get_card_value(i)

        if self.has_ace and self.points < 12:
            self.points += 10
            self.text = str(self.points) + " / " + str(self.points-10)
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

class BetChooser(VerticalPane):
    class BetButton(pgnull.Sprite):
        def __init__(self, value):
            super().__init__(f"images/gui/bet_buttons/bet_{str(value)}.png")
            self.value = int(value)
            
        def on_click(self):
            self.parent.bet_value += self.value

    class BetDisplay(pgnull.TextBox):
        def __init__(self):
            super().__init__("Bet: 0", pos=(0,0), fontsize=50,
                         font="PixelOperator8_Bold.ttf", text_color=(255, 255, 255))
            self.displayed_bet = 0

        def on_start(self):
            self.center = (-50, self.center[1])

        def on_update(self, ctx):
            if self.displayed_bet != self.parent.bet_value:
                self.displayed_bet = self.parent.bet_value
                self.text = f"Bet: {self.parent.bet_value}"

    def __init__(self):
        super().__init__(10)
        self.pos = (470, 300)

        self.bet_value = 0

    def on_start(self):
        self.add_game_object(BetChooser.BetDisplay())

        # gap
        g = pgnull.GameObject()
        g.height = 50
        self.add_game_object(g)

        self.reg_obj(
            BetChooser.BetButton("10"),
            "bet_10"
        )
        self.reg_obj(
            BetChooser.BetButton("50"),
            "bet_50"
        )
        self.reg_obj(
            BetChooser.BetButton("100"),
            "bet_100"
        )
        self.reg_obj(
            BetChooser.BetButton("500"),
            "bet_500"
        )


class MainGame(pgnull.GameObject):
    def __init__(self):
        super().__init__()
        # self.bg_color = (18,112,58)

        self.reg_obj(pgnull.Sprite("images/bg.png"), "bg")
        self.bg.set_size(WIDTH, HEIGHT)
        self.bg.pos = (0, 0)

        self.reg_obj(SpawnedCardsScene(), "spawned_cards")

        self.points = PointDisplay()
        self.reg_obj(self.points, None)

        self.reg_obj(Stack(), "stack")

        self.reg_obj(BetChooser(), "bet_chooser")

    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.spawned_cards.reset()
            self.stack.shuffle()
