import pgnull

class SingleplayerGameState(pgnull.TextBox):
    # diese klasse soll gewinn/verlust usw. verwalten
    # zeigt balance, einsatz usw. an
    def __init__(self):
        super().__init__("Point Display", topleft=(0,0),
                         fontsize=15, font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255), line_gap=6)
        self.box_topleft = (1130, 275 )

        self.dealer_points = 0

        self.player_points = 0
        self.player_balance = 1000
        self.player_bet = 0

        self.reg_obj(pgnull.AudioPlayer("sounds/stand.wav"), "stand_sound")
        self.reg_obj(pgnull.AudioPlayer("sounds/win.wav"), "win_sound")
        self.reg_obj(pgnull.AudioPlayer("sounds/loose.wav"), "loose_sound")

        self.user_help_text = "" # text der dem spieler sagt was zu tun ist
                                 # tut mir leid ich bin kein frontend dev

        self.dealer_cards = [] # zwei startkarten vom dealer

    def on_update(self, ctx):
        self.player_balance = int(self.player_balance)
        self.text = f"{'Player':<8} {'Points':<8} {'Balance':<8} {'Bet':<8}\n\n" +\
                    f"{'Player':<8} {self.player_points:<8} {self.player_balance:<8} {self.player_bet:<8}\n" +\
                    f"{'Dealer':<8} {self.dealer_points:<8} {' ':<8} {' ':<8}\n" +\
                     "\n\n----\n" +\
                    self.user_help_text

    def on_start(self):
        # wird auch bei neuer runde aufgerufen
        self.parent.idle = 1 # sag main scene dass das spiel gerade läuft

        self.parent.stack.shuffle() # kartendeck mischen
        self.parent.spawned_cards.reset() # alle karten vom tisch entfernen

        self.player_points = 0
        self.player_bet = 0

        self.parent.bet_chooser.bet_value = 0
        self.parent.bet_chooser.display.update_display()
        self.user_help_text = "Choose a bet"
        self.parent.bet_chooser.can_choose = True

    def check_bet(self):
        # wird vom 'Place'-button aufgerufen
        if self.parent.bet_chooser.bet_value <= self.player_balance:
            # spieler hat genug geld
            self.parent.bet_chooser.can_choose = False
            self.user_help_text = "Bet placed"
            self.player_bet = self.parent.bet_chooser.bet_value

            self.player_balance -= self.player_bet

            pgnull.Game.get_game().clock.schedule(self.start_game, 1, 1) # spiel in 1 sekunde starten
        else:
            # konnte Einsatz nicht platzieren, spieler hat zu wenig geld
            self.parent.bet_chooser.bet_value = 0
            self.parent.bet_chooser.display.update_display()
            self.user_help_text = "You don't have enough money\nfor that"

    def start_game(self):
        # Starthand des dealers ziehen
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.dealer_points = self.parent.point_display.points

        self.dealer_cards = self.parent.spawned_cards.get_children() # starthand des dealers für später speichern
        self.parent.spawned_cards.reset()

        # eigene karten ziehen
        self.user_help_text = f"Dealer has drawn {self.dealer_points} on his \nstart hand\nIt's your turn"
        self.parent.stack.draw_card()
        self.parent.stack.draw_card()

        self.parent.stand_button.pressable = True
        self.parent.stack.can_draw = True

    def finish_player_turn(self):
        # wird aufgerufen wenn der spieler entweder auf Stand gegangen ist oder overshooted hat
        self.parent.stand_button.pressable = False
        self.stand_sound.play() # sound effekt für stand button
        self.parent.stack.can_draw = False
        self.player_points = self.parent.point_display.points
        self.user_help_text = f"Finished with {self.player_points}\nDealer is drawing..."

        pgnull.Game.get_game().clock.schedule(self.dealer_prepare, 2, 1) # 2 sekunden warten bis dealer beginnt

    def dealer_prepare(self):
        self.parent.spawned_cards.reset()

        # Starthand des dealers wieder auf den tisch legen
        for i in self.dealer_cards:
            self.parent.spawned_cards.add_game_object(i)

        pgnull.Game.get_game().clock.schedule(self.dealer_draw, 2, 1)

    def dealer_draw(self):
        if self.dealer_points < 17 and self.player_points <= 21:
            # bei 16 oder weniger noch eine karte ziehen, bei 17 oder mehr stehen
            # wenn spieler schon overshooted hat, direkt stehen
            self.parent.stack.draw_card()
            self.parent.stack.draw_sound.play() # in dieser game phase soll der dealer draw auch einen sound machen
            self.dealer_points = self.parent.point_display.points
            pgnull.Game.get_game().clock.schedule(self.dealer_draw, 1, 1)
        else:
            self.user_help_text = f"Dealer finished with {self.dealer_points}"
            self.finish_game()


    def finish_game(self):
        if (self.player_points > self.dealer_points and self.player_points <= 21) or (self.player_points <= 21 and self.dealer_points > 21):
            # spieler hat gewonnen
            self.win_sound.play()
            win = self.player_bet*2.5 # einsatz zurück + 150% des einsatzes auszahlen
            self.player_balance += win
            self.user_help_text += f"\n\nYou won ${win-self.player_bet}!\nPress 'c' or the stand button \nto play again."
        elif self.player_points == self.dealer_points and self.player_points <= 21:
            # unentschieden
            win = self.player_bet
            self.player_balance += win
            self.user_help_text += f"\n\nYou have tied with the Dealer.\nPress 'c' or the stand button \nto play again."
        else:
            # spieler hat verloren
            self.loose_sound.play()
            self.user_help_text += f"\n\nYou lost :((( \n\n(Don't be perturbed,\nthe gambling gods will answer you)"
            if self.player_balance < 5: # mindesteinsatz
                self.user_help_text += "\n\nOh No! \nIt looks like you went all in and \nwent out of funds. Very sad\n\nPress 'c' or the stand button \nto get back to the menu."
                self.parent.idle = -1 # main scene mitteilen, dass wir nicht weiterspielen können
                return
            else:
                self.user_help_text += "\nPress 'c' or the stand button\nto play again."

        self.player_bet = 0 # einsatzanzeige leeren
        # spiel mitteilen, dass wir gerade im leerlauf sind
        self.parent.idle = 0
