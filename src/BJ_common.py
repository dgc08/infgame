from random import shuffle

import pgnull
from pgnull import utils

from pygame.math import Vector2

WIDTH, HEIGHT = utils.glob_singleton["window"]

class Card(pgnull.Sprite):
    def __init__(self, card_ident, **kwargs):
        super().__init__(f"images/cards/{card_ident}.png", scale=2.5, **kwargs)
        self.card_ident = card_ident # card name, e.g. clubs_04, hearts_A, ... (-> cards_bj.txt)

class SpawnedCardsScene(pgnull.GameObject):
    # i am to lazy to rewrite this using HorizontalPane
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

        # update point display, new card drawn means points changed
        self.parent.point_display.update_display()

    def reset(self):
        self.cards = []
        for i in self.get_children():
            i.dequeue()

        # point display should show 0 now
        self.parent.point_display.update_display()


class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos = (696, 370)
        print(self.pos)
        self.can_draw = False

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))
        #self.stack = ["clubs_02", "clubs_03", "clubs_A", "clubs_05"] # for debugging

        self.pointer = 0 # keep a pointer to the top of the stack which is advanced on draw,
        # do not pop off cards because then the drawn cards will have to be readded to the list on shuffle

    def on_start(self):
        self.shuffle()

    def shuffle(self):
        shuffle(self.stack) # random.shuffle the stack of cards
        self.pointer = 0
        self.active = True # in case all cards have been drawn and the stack has been deactivated

    def on_click(self):
        if self.can_draw:
            self.draw_card()
            # this will only be executed on player draw, because the dealer calls draw_card() directly
            if self.parent.point_display.points > 21:
                self.parent.game_controller.finish_player_turn()

    def draw_card(self):
        if self.pointer >= len(self.stack):
            # if all cards have been drawn
            return None

        draw = self.stack[self.pointer] # take current top card

        #add a card game object to the spawned cards container
        self.parent.spawned_cards.reg_obj(
            Card(draw),
            None
        )

        self.pointer += 1

        if self.pointer == len(self.stack):
            # all cards have been drawn, deactivate yourself
            # (update and draw are not going to be called)
            self.active = False

        return draw


class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-220, 50), fontsize=50,
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))
        self.has_ace = False
        self.points = 0

    def update_display(self):
        # recalculate point value of all the cards in spawned_cards
        self.points = 0
        self.has_ace = False
        for i in self.parent.spawned_cards.cards:
            self.points += self.get_card_value(i)

        if self.has_ace and self.points < 12:
            # an ace is either 1 or 11 points worth, depending on if 11 would bring you over 21
            # get_card_value returns 1 for an ace, but this makes sure that the remaining 10 are added if the current score doesn't go over 21 with that
            self.points += 10
            # display the score with the ace as 1 or 11, because if you stand now the higher value will be counted, if you draw again the point values will be recalculated in case the ace has to be 1
            self.text = str(self.points) + " / " + str(self.points-10)
        else:
            self.text = str(self.points)

    def get_card_value(self, card_name):
        ident = card_name.split("_")[1]
        if ident.isdigit():
            return int(ident)
        elif ident == "A":
            # ace
            self.has_ace = True
            return 1
        else:
            # everything that is not a number or an ace is worth 10 points
            return 10

class BetChooser(pgnull.VPane):
    class Accept(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/place.png")
        def on_click(self):
            if self.parent.parent.parent.bet_value == 0 or not self.parent.parent.parent.can_choose:
                # if no bet has been chosen or the chooser is not active do nothing
                return
            # else, give the bet value to the game controller
            pgnull.Game.get_game().scene.game_controller.check_bet()
    class Clear(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/clear.png")
        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.parent.parent.parent.bet_value = 0
                self.parent.parent.parent.display.update_display() # bet display update text


    class BetButton(pgnull.Sprite):
        def __init__(self, value):
            super().__init__(f"images/gui/bet_buttons/bet_{str(value)}.png") # load the texture with the given button value
            self.value = int(value)

        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.parent.parent.parent.bet_value += self.value
                self.parent.parent.parent.display.update_display() # bet display update text

    class BetDisplay(pgnull.TextBox):
        def __init__(self):
            super().__init__("  Bet: 0", pos=(0,0), fontsize=50,
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))

        def update_display(self):
            self.text = f"  Bet: {self.parent.bet_value}"

    def __init__(self):
        super().__init__(10) # 10 px is the gap between the text and the buttons
        self.pos = (300, 300)

        self.bet_value = 0
        self.can_choose = False

    def on_start(self):
        self.display = BetChooser.BetDisplay() # can't use reg_obj for some reason (! dequeue wont work !) # TODO (for pgnull in the long run)
        self.add_game_object(self.display)

        buttons = pgnull.VPane(10)
        buttons.reg_obj(
            BetChooser.BetButton("10"),
            None
        )
        buttons.reg_obj(
            BetChooser.BetButton("50"),
            None
        )
        buttons.reg_obj(
            BetChooser.BetButton("100"),
            None
        )
        buttons.reg_obj(
            BetChooser.BetButton("500"),
            None
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

        hpane = pgnull.HPane(30) # place both columns of buttons in a horizontal pane
        hpane.reg_obj(buttons, None)
        hpane.reg_obj(confirm_buttons, None)

        self.reg_obj(hpane, None)

        # try to center the bet display above the hpane
        self.display.pos.x = (hpane.width - self.display.width) / 2

class StandButton(pgnull.Sprite):
    def __init__(self):
        self.pressable = False
        super().__init__("images/gui/stand_button.png", pos=(900, HEIGHT/2))

    def on_click(self):
        if self.pressable:
            self.parent.game_controller.finish_player_turn()
        self.parent.check_restart() # let the Main Game Scene check if may need to restart

class MainGame(pgnull.GameObject):
    def __init__(self, state_object):
        super().__init__()
        # self.bg_color = (18,112,58)

        # populate the tree
        self.reg_obj(pgnull.Sprite("images/bg.png"), "bg")
        self.bg.set_size(WIDTH, HEIGHT)
        self.bg.pos = (0, 0)

        self.reg_obj(SpawnedCardsScene(), "spawned_cards")

        self.point_display = PointDisplay()
        self.reg_obj(self.point_display, None)

        self.reg_obj(Stack(), "stack")
        self.reg_obj(BetChooser(), "bet_chooser")
        self.reg_obj(StandButton(), "stand_button")

        self.reg_obj(state_object, "game_controller") # this controls all the objects on the screen, differs between singe/multiplayer


    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.check_restart()

    def check_restart(self):
        if self.idle == 1:
            # do nothing, the game is currently on
            pass
        elif self.idle == 0:
            # game finished and we can restart
            self.game_controller.on_start()
        elif self.idle == -1:
            # we ran out of funds
            self.dequeue()
