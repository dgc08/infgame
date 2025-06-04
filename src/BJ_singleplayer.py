import pgnull

class SingleplayerGameState(pgnull.TextBox):
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

        self.user_help_text = "" # text that is displayed to tell the user what to do
                                 # i don't know how to make good UIs sorry

        self.dealer_cards = [] # two starting cards of dealer

    def on_update(self, ctx):
        self.text = f"{'Player':<8} {'Points':<8} {'Balance':<8} {'Bet':<8}\n\n" +\
                    f"{'Player':<8} {self.player_points:<8} {self.player_balance:<8} {self.player_bet:<8}\n" +\
                    f"{'Dealer':<8} {self.dealer_points:<8} {' ':<8} {' ':<8}\n" +\
                     "\n\n----\n" +\
                    self.user_help_text

    def on_start(self):
        # on new round
        self.parent.idle = 1 # the game is currently running

        self.parent.stack.shuffle() # shuffle the card stack
        self.parent.spawned_cards.reset() # remove any cards on the table

        self.player_points = 0
        self.player_bet = 0

        self.parent.bet_chooser.bet_value = 0
        self.parent.bet_chooser.display.update_display()
        self.user_help_text = "Choose a bet"
        self.parent.bet_chooser.can_choose = True

    def check_bet(self):
        # called by the 'Place' button
        if self.parent.bet_chooser.bet_value <= self.player_balance:
            # the user has enough money
            self.parent.bet_chooser.can_choose = False
            self.user_help_text = "Bet placed"
            self.player_bet = self.parent.bet_chooser.bet_value

            self.player_balance -= self.player_bet

            pgnull.Game.get_game().clock.schedule(self.start_game, 1, 1) # start the game in 1 second
        else:
            # couldn't place bet and advance the game, the user has no money
            self.parent.bet_chooser.bet_value = 0
            self.parent.bet_chooser.display.update_display()
            self.user_help_text = "You don't have enough money\nfor that"

    def start_game(self):
        # draw dealer start hand
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.dealer_points = self.parent.point_display.points

        self.dealer_cards = self.parent.spawned_cards.get_children() # save dealer start hand for later
        self.parent.spawned_cards.reset()

        # draw own cards
        self.user_help_text = f"Dealer has drawn {self.dealer_points} on his \nstart hand\nIt's your turn"
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.parent.stand_button.pressable = True
        self.parent.stack.can_draw = True

    def finish_player_turn(self):
        # player either stands on his current score or overshot
        self.parent.stand_button.pressable = False
        self.parent.stack.can_draw = False
        self.player_points = self.parent.point_display.points
        self.user_help_text = f"Finished with {self.player_points}\nDealer is drawing..."

        pgnull.Game.get_game().clock.schedule(self.dealer_prepare, 2, 1) # wait 2 seconds until the dealer starts drawing

    def dealer_prepare(self):
        self.parent.spawned_cards.reset()

        # readd the dealer start hand
        for i in self.dealer_cards:
            self.parent.spawned_cards.add_game_object(i)

        pgnull.Game.get_game().clock.schedule(self.dealer_draw, 2, 1)

    def dealer_draw(self):
        if self.dealer_points < 17 and self.player_points <= 21:
            # draw a card on 16 or less, stand on 17 or more
            # if the player already overshot, stand automatically
            self.parent.stack.draw_card()
            self.dealer_points = self.parent.point_display.points
            pgnull.Game.get_game().clock.schedule(self.dealer_draw, 1, 1)
        else:
            self.user_help_text = f"Dealer finished with {self.dealer_points}"
            self.finish_game()


    def finish_game(self):
        if (self.player_points > self.dealer_points and self.player_points <= 21) or (self.player_points <= 21 and self.dealer_points > 21):
            # player won
            win = self.player_bet*2.5 # pay back the bet and 150% of the bet as win
            self.player_balance += win
            self.user_help_text += f"\n\nYou won ${win-self.player_bet}!\nPress 'c' or the stand button \nto play again."
        elif self.player_points == self.dealer_points and self.player_points <= 21:
            # tie
            win = self.player_bet
            self.player_balance += win
            self.user_help_text += f"\n\nYou have tied with the Dealer.\nPress 'c' or the stand button \nto play again."
        else:
            # player lost
            self.user_help_text += f"\n\nYou lost :((( \n\n(Don't be perturbed,\nthe gambling gods will answer you)"
            if self.player_balance < 5: # minimum bet
                self.user_help_text += "\n\nOh No! \nIt looks like you went all in and \nwent out of funds. Very tis\n\nPress 'c' or the stand button \nto get back to the menu."
                self.parent.idle = -1 # tell the game that we can't continue playing
                return
            else:
                self.user_help_text += "\nPress 'c' or the stand button\nto play again."

        self.player_bet = 0 # remove bet from the table display
        # tell the game that we are currently idle
        self.parent.idle = 0
