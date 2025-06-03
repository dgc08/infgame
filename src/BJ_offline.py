from random import shuffle

import pgnull
from pgnull import utils

from pygame.math import Vector2

WIDTH, HEIGHT = utils.glob_singleton["window"]

class Card(pgnull.Sprite):
    def __init__(self, card_ident, **kwargs):
        super().__init__(f"images/cards/{card_ident}.png", scale=2.5, **kwargs)
        self.card_ident = card_ident

        
class SpawnedCardsScene(pgnull.GameObject):
    # i am to lazy to rewrite this with HorizontalPane
    def __init__(self):
        super().__init__()
        self.pos.y = 150
        self.cards = []

    def add_game_object(self, game_obj):
        if not isinstance(game_obj, Card):
            raise Exception("This should not happen; you can only add cards to the SpawnedCardsScene")
        super().add_game_object(game_obj)
        self.cards.append(game_obj.card_ident)

        # realign Cards
        total_amount = len(self.cards)
        for idx, g in enumerate(self.get_children()): # for every card, index
            g.x = (WIDTH - (g.width * total_amount)) / 2 + idx * g.width # we don't need a gap between the cards,
            # because the texture has a gap builtin

        # update display
        self.parent.point_display.update_display()

    def reset(self):
        self.cards = []
        for i in self.get_children():
            i.dequeue()

        # update display
        self.parent.point_display.update_display()


class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos = ((WIDTH-self.width)/2, ((HEIGHT-self.height)/2) + 30 )

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))
        #self.stack = ["clubs_02", "clubs_03", "clubs_A", "clubs_05"]

    def on_start(self):
        self.shuffle()

    def shuffle(self):
        shuffle(self.stack) # -> random.shuffle the stack of cards
        self.pointer = 0
        self.active = True # in case all cards have been drawn and the stack has been deactivated

    def on_click(self):
        self.draw_card()

    def draw_card(self):
        if self.pointer >= len(self.stack):
            return None

        draw = self.stack[self.pointer]

        self.parent.spawned_cards.reg_obj(
            Card(draw),
            None
        )

        self.pointer += 1

        if self.pointer == len(self.stack):
            # all cards have been drawn
            self.active = False

        return draw


class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-220, 50), fontsize=50,
                         font="PixelOperator8_Bold.ttf", text_color=(255, 255, 255))
        self.has_ace = False
        self.points = 0
        
    def update_display(self):
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

class BetChooser(pgnull.VPane):
    class Accept(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/place.png")
        def on_click(self):
            # TODO
            print("bet placed")
    class Clear(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/clear.png")
        def on_click(self):
            self.parent.parent.parent.bet_value = 0
            self.parent.parent.parent.display.update_display()


    class BetButton(pgnull.Sprite):
        def __init__(self, value):
            super().__init__(f"images/gui/bet_buttons/bet_{str(value)}.png")
            self.value = int(value)
            
        def on_click(self):
            self.parent.parent.parent.bet_value += self.value
            self.parent.parent.parent.display.update_display()

    class BetDisplay(pgnull.TextBox):
        def __init__(self):
            super().__init__("  Bet: 0", pos=(0,0), fontsize=50,
                         font="PixelOperator8_Bold.ttf", text_color=(255, 255, 255))

        def update_display(self):
            self.text = f"  Bet: {self.parent.bet_value}"
            
    def __init__(self):
        super().__init__(10)
        self.pos = (300, 300)

        self.bet_value = 0

    def on_start(self):
        self.display = BetChooser.BetDisplay() # can't use reg_obj for some reason (! dequeue wont work !)
        self.add_game_object(self.display)

        buttons = pgnull.VPane(10)
        buttons.reg_obj(
            BetChooser.BetButton("10"),
            "bet_10"
        )
        buttons.reg_obj(
            BetChooser.BetButton("50"),
            "bet_50"
        )
        buttons.reg_obj(
            BetChooser.BetButton("100"),
            "bet_100"
        )
        buttons.reg_obj(
            BetChooser.BetButton("500"),
            "bet_500"
        )

        confirm_buttons = pgnull.VPane(10)
        confirm_buttons.reg_obj(
            BetChooser.Accept(),
            None
        )
        confirm_buttons.reg_obj(
            BetChooser.Clear(),
            None
        )

        confirm_buttons.pos.y = ( buttons.height - confirm_buttons.height ) / 2
        
        hpane = pgnull.HPane(30)
        hpane.reg_obj(buttons, "buttons")
        hpane.reg_obj(confirm_buttons, "confirm")


        self.reg_obj(hpane, "hpane")

        self.display.pos.x = (hpane.width - self.display.width) / 2


class MainGame(pgnull.GameObject):
    def __init__(self):
        super().__init__()
        # self.bg_color = (18,112,58)

        self.reg_obj(pgnull.Sprite("images/bg.png"), "bg")
        self.bg.set_size(WIDTH, HEIGHT)
        self.bg.pos = (0, 0)

        self.reg_obj(SpawnedCardsScene(), "spawned_cards")

        self.point_display = PointDisplay()
        self.reg_obj(self.point_display, None)

        self.reg_obj(Stack(), "stack")

        self.reg_obj(BetChooser(), "bet_chooser")

    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.spawned_cards.reset()
            self.stack.shuffle()
