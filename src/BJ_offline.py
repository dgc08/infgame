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
        self.pos = (696, 370)
        print(self.pos)
        self.can_draw = False

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
        if self.can_draw:
            self.draw_card() # this will always be drawn by player
            if self.parent.point_display.points > 21:
                self.parent.state.finish_player_turn()

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
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))
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
            if self.parent.parent.parent.bet_value == 0 or not self.parent.parent.parent.can_choose:
                return
            pgnull.Game.get_game().scene.state.check_bet()
    class Clear(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/clear.png")
        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.parent.parent.parent.bet_value = 0
                self.parent.parent.parent.display.update_display()


    class BetButton(pgnull.Sprite):
        def __init__(self, value):
            super().__init__(f"images/gui/bet_buttons/bet_{str(value)}.png")
            self.value = int(value)
            
        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.parent.parent.parent.bet_value += self.value
                self.parent.parent.parent.display.update_display()

    class BetDisplay(pgnull.TextBox):
        def __init__(self):
            super().__init__("  Bet: 0", pos=(0,0), fontsize=50,
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))

        def update_display(self):
            self.text = f"  Bet: {self.parent.bet_value}"
            
    def __init__(self):
        super().__init__(10)
        self.pos = (300, 300)

        self.bet_value = 0
        self.can_choose = False

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

class StandButton(pgnull.Sprite):
    def __init__(self):
        self.pressable = False
        super().__init__("images/gui/stand_button.png", pos=(900, HEIGHT/2))

    def on_click(self):
        if self.pressable:
            self.parent.state.finish_player_turn()
        self.parent.check_restart()

class GameState(pgnull.TextBox):
    # this should be the class managing win / lose etc
    # this displays balance, bet etc
    def __init__(self):
        super().__init__("Point Display", topleft=(0,0),
                         fontsize=15, font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255), line_gap=6)
        self.box_topleft = (1130, 275 )

        self.dealer_points = 0

        self.player_points = 0
        self.player_balance = 1000
        self.player_bet = 0

        self.user_help_text = ""

        self.dealer_cards = [] # two starting cards of dealer

    def on_update(self, ctx):
        self.text = f"{'Player':<8} {'Points':<8} {'Balance':<8} {'Bet':<8}\n\n" +\
                    f"{'Dealer':<8} {self.dealer_points:<8} {'/':<8} {'/':<8}\n" +\
                    f"{'Player':<8} {self.player_points:<8} {self.player_balance:<8} {self.player_bet:<8}\n\n\n" +\
                     "----\n" +\
                    self.user_help_text

    def on_start(self):
        # on new round
        self.parent.idle = 1

        self.parent.stack.shuffle()
        self.parent.spawned_cards.reset()

        self.player_points = 0
        self.player_bet = 0

        self.parent.bet_chooser.bet_value = 0
        self.parent.bet_chooser.display.update_display()
        self.user_help_text = "Choose a bet"
        self.parent.bet_chooser.can_choose = True

    def check_bet(self):
        if self.parent.bet_chooser.bet_value <= self.player_balance:
            self.parent.bet_chooser.can_choose = False
            self.user_help_text = "Bet placed"
            self.player_bet = self.parent.bet_chooser.bet_value

            self.player_balance -= self.player_bet

            pgnull.Game.get_game().clock.schedule(self.start_game, 1, 1)
        else:
            self.parent.bet_chooser.bet_value = 0
            self.parent.bet_chooser.display.update_display()
            self.user_help_text = "You don't have enough money\nfor that"

    def start_game(self):
        # draw dealer cards
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.dealer_points = self.parent.point_display.points

        self.dealer_cards = self.parent.spawned_cards.get_children()

        self.user_help_text = f"Dealer has drawn {self.dealer_points} on his \nstart hand\nIt's your turn"
        self.parent.spawned_cards.reset()

        # draw own cards
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.parent.stand_button.pressable = True
        self.parent.stack.can_draw = True

    def finish_player_turn(self):
        self.parent.stand_button.pressable = False
        self.parent.stack.can_draw = False
        self.player_points = self.parent.point_display.points
        self.user_help_text = f"Finished with {self.player_points}\nDealer is drawing..."

        pgnull.Game.get_game().clock.schedule(self.dealer_prepare, 2, 1)

    def dealer_prepare(self):
        self.parent.spawned_cards.reset()

        for i in self.dealer_cards:
            self.parent.spawned_cards.add_game_object(i)

        pgnull.Game.get_game().clock.schedule(self.dealer_draw, 2, 1)

    def dealer_draw(self):
        if self.dealer_points < 17 and self.player_points <= 21:
            # draw a card under 17
            self.parent.stack.draw_card()
            self.dealer_points = self.parent.point_display.points
            pgnull.Game.get_game().clock.schedule(self.dealer_draw, 1, 1)
        else:
            self.user_help_text = f"Dealer finished with {self.dealer_points}"
            self.finish_game()


    def finish_game(self):
        if (self.player_points > self.dealer_points and self.player_points <= 21) or (self.player_points <= 21 and self.dealer_points > 21):
            win = self.player_bet*2.5
            self.player_balance += win
            self.user_help_text += f"\n\nYou won ${win}!\nPress 'c' or the stand button \nto play again."
        elif self.player_points == self.dealer_points and self.player_points <= 21:
            win = self.player_bet
            self.player_balance += win
            self.user_help_text += f"\n\nYou have tied with the Dealer.\nPress 'c' or the stand button \nto play again."
        else:
            self.user_help_text += f"\n\nYou lost :((( \n\n(Don't be perturbed,\nthe gambling gods will answer you)"
            if self.player_balance < 5: # minimum bet
                self.user_help_text += "\n\nOh No! \nIt looks like you went all in and \nwent out of funds. Very tis\n\nPress 'c' or the stand button \nto get back to the menu."
                self.parent.idle = -1
                return
            else:
                self.user_help_text += "\nPress 'c' or the stand button\nto play again."
        self.parent.idle = 0


class MainGame(pgnull.GameObject):
    def __init__(self):
        super().__init__()
        # self.bg_color = (18,112,58)

        self.idle = 1 # look at on_update

        self.reg_obj(pgnull.Sprite("images/bg.png"), "bg")
        self.bg.set_size(WIDTH, HEIGHT)
        self.bg.pos = (0, 0)

        self.reg_obj(SpawnedCardsScene(), "spawned_cards")

        self.point_display = PointDisplay()
        self.reg_obj(self.point_display, None)

        self.reg_obj(Stack(), "stack")

        self.reg_obj(BetChooser(), "bet_chooser")

        self.reg_obj(GameState(), "state")

        self.reg_obj(StandButton(), "stand_button")

    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.check_restart()

    def check_restart(self):
        if self.idle == 1:
            # do nothing, the game is currently on
            pass
        elif self.idle == 0:
            # game finished and we can restart
            self.state.on_start()
        elif self.idle == -1:
            # we ran out of funds
            self.dequeue()
