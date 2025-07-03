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
            raise Exception("das sollte nicht passieren; du kannst nur cards zur SpawnedCardsScene hinzufügen")
        super().add_game_object(game_obj)
        self.cards.append(game_obj.card_ident)

        # karten neu ausrichten
        total_amount = len(self.cards)
        for idx, g in enumerate(self.get_children()): # für jede karte, index
            g.x = (WIDTH - (g.width * total_amount)) / 2 + idx * g.width # wir brauchen keinen abstand zwischen den karten,
            # weil die textur schon einen abstand eingebaut hat

        # Punkteanzeige aktualisieren, neue karte gezogen bedeutet punkte haben sich geändert
        self.parent.point_display.update_display()

    def reset(self):
        self.cards = []
        for i in self.get_children():
            i.dequeue()

        # Punkteanzeige sollte jetzt 0 anzeigen
        self.parent.point_display.update_display()


class Stack(Card):
    def __init__(self):
        super().__init__("back")
        self.pos = (696, 370)
        self.can_draw = False

        self.reg_obj(pgnull.AudioPlayer("sounds/draw.wav"), "draw_sound")
        self.reg_obj(pgnull.AudioPlayer("sounds/shuffle.wav"), "shuffle_sound")

        with open("src/cards_bj.txt") as f:
            self.stack = list(map(str.strip, f.readlines()))
        #self.stack = ["clubs_02", "clubs_03", "clubs_A", "clubs_05"] # zum debuggen

        self.pointer = 0 # behalte einen pointer auf die oberste karte, der beim ziehen erhöht wird
        # keine karten von self.stack entfernen, sonst müssten gezogene karten beim mischen wieder hinzugefügt werden

    def on_start(self):
        self.shuffle()

    def shuffle(self):
        shuffle(self.stack) # den stapel random.shuffle'n

        self.shuffle_sound.play()
        self.pointer = 0
        self.active = True # falls alle karten gezogen wurden und der stapel deaktiviert wurde

    def on_click(self):
        if self.can_draw:
            self.draw_card()
            # das wird nur ausgeführt wenn der spieler zieht, weil der dealer draw_card() direkt aufruft

            self.draw_sound.play()
            if self.parent.point_display.points > 21:
                self.parent.game_controller.finish_player_turn()

    def draw_card(self):
        if self.pointer >= len(self.stack):
            # wenn alle karten gezogen wurden
            return None

        draw = self.stack[self.pointer] # aktuelle oberste karte nehmen

        # ein Card-GameObject zum spawned_cards-Container hinzufügen
        self.parent.spawned_cards.reg_obj(
            Card(draw),
            None
        )

        self.pointer += 1

        if self.pointer == len(self.stack):
            # alle karten gezogen, deaktivier dich
            # (update und draw werden dann nicht mehr aufgerufen)
            self.active = False

        return draw


class PointDisplay(pgnull.TextBox):
    def __init__(self):
        super().__init__("0", pos=(WIDTH-220, 50), fontsize=50,
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))
        self.has_ace = False
        self.points = 0

    def update_display(self):
        # punktzahl aller karten in spawned_cards neu berechnen
        self.points = 0
        self.has_ace = False
        for i in self.parent.spawned_cards.cards:
            self.points += self.get_card_value(i)

        if self.has_ace and self.points < 12:
            # ein ass zählt entweder 1 oder 11 punkte, je nachdem ob man mit 11 über 21 gehen würde
            # get_card_value gibt für ein ass 1 zurück, aber hier werden die restlichen 10 hinzugefügt
            # wenn das aktuelle ergebnis mit 11 nicht über 21 geht
            self.points += 10
            # punktzahl anzeigen, ass als 1 oder 11, weil beim 'Stand' drücken der höhere wert zählt;
            # beim nochmal ziehen wird die punktzahl eh neu berechnet
            self.text = str(self.points) + " / " + str(self.points-10)
        else:
            self.text = str(self.points)

    def get_card_value(self, card_name):
        ident = card_name.split("_")[1]
        if ident.isdigit():
            return int(ident)
        elif ident == "A":
            # ass
            self.has_ace = True
            return 1
        else:
            # alles, was keine zahl oder ass ist, zählt 10 punkte
            return 10

class BetChooser(pgnull.VPane):
    class Accept(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/place.png")
            self.reg_obj(pgnull.AudioPlayer("sounds/place.wav"), "sound")
        def on_click(self):
            if self.parent.parent.parent.bet_value == 0 or not self.parent.parent.parent.can_choose:
                # wenn kein einsatz gewählt wurde oder der chooser nicht aktiv ist, nichts tun
                return
            # sonst, einsatz an game controller übergeben
            self.sound.play()
            pgnull.Game.get_game().scene.game_controller.check_bet()

    class Clear(pgnull.Sprite):
        def __init__(self):
            super().__init__("images/gui/bet_buttons/clear.png")
        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.parent.parent.parent.bet_value = 0
                self.parent.parent.parent.display.update_display() # einsatzanzeige aktualisieren


    class BetButton(pgnull.Sprite):
        def __init__(self, value):
            super().__init__(f"images/gui/bet_buttons/bet_{str(value)}.png") # textur mit gegebenem wert laden
            self.reg_obj(pgnull.AudioPlayer("sounds/money_button.wav"), "sound")
            self.value = int(value)

        def on_click(self):
            if self.parent.parent.parent.can_choose:
                self.sound.play() # sound abspielen
                self.parent.parent.parent.bet_value += self.value
                self.parent.parent.parent.display.update_display() # einsatzanzeige aktualisieren

    class BetDisplay(pgnull.TextBox):
        def __init__(self):
            super().__init__("  Bet: 0", pos=(0,0), fontsize=50,
                         font="PixelOperatorMono8-Bold.ttf", text_color=(255, 255, 255))

        def update_display(self):
            self.text = f"  Bet: {self.parent.bet_value}"

    def __init__(self):
        super().__init__(10) # 10 px abstand zwischen text und buttons
        self.pos = (300, 300)

        self.bet_value = 0
        self.can_choose = False

    def on_start(self):
        self.reg_obj(BetChooser.BetDisplay(), "display")

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

        hpane = pgnull.HPane(30) # beide button-spalten in ein horizontale pane legen
        hpane.reg_obj(buttons, None)
        hpane.reg_obj(confirm_buttons, None)

        self.reg_obj(hpane, None)

        # versuche, die einsatzanzeige über dem hpane zu zentrieren
        self.display.pos.x = (hpane.width - self.display.width) / 2

class StandButton(pgnull.Sprite):
    def __init__(self):
        self.pressable = False
        super().__init__("images/gui/stand_button.png", pos=(900, HEIGHT/2))

    def on_click(self):
        if self.pressable:
            self.parent.game_controller.finish_player_turn()
        self.parent.check_restart() # die main scene überprüfen lassen, ob sie neu starten muss

class MainGame(pgnull.GameObject):
    def __init__(self, state_object):
        super().__init__()
        # self.bg_color = (18,112,58)

        # tree befüllen
        self.reg_obj(pgnull.Sprite("images/bg.png"), "bg")
        self.bg.set_size(WIDTH, HEIGHT)
        self.bg.pos = (0, 0)

        self.reg_obj(SpawnedCardsScene(), "spawned_cards")

        self.point_display = PointDisplay()
        self.reg_obj(self.point_display, None)

        self.reg_obj(Stack(), "stack")
        self.reg_obj(BetChooser(), "bet_chooser")
        self.reg_obj(StandButton(), "stand_button")

        self.reg_obj(state_object, "game_controller") # steuert alle objekte auf dem bildschirm, unterscheidet sich bei single-/multiplayer


    def on_update(self, ctx):
        if ctx.keyboard.c:
            self.check_restart()

    def check_restart(self):
        if self.idle == 1:
            # nichts tun, spiel läuft aktuell
            pass
        elif self.idle == 0:
            # spiel beendet, wir können neu starten
            self.game_controller.on_start()
        elif self.idle == -1:
            # kein geld mehr übrig
            self.dequeue()
