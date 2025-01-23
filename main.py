#!/usr/bin/env python3

from random import randint
from pygame.math import Vector2,clamp
import pgnull

WIDTH = 600
HEIGHT = 600

game = pgnull.Game(WIDTH, HEIGHT, "some game")

#lobby = pgnull.Scene("dim grey")
#main = pgnull.Scene("green")

### Lobby

class Lobby(pgnull.Scene):
    box_w = Vector2(180, 150)

    title_box= pgnull.TextBox("Some random game", (300,100))
    start_game_button = pgnull.Button("Start", ((WIDTH-box_w.x)/2, 160), box_w, "orange")
    exit_button = pgnull.Button( "Quit", ((WIDTH-box_w.x)/2, start_game_button.y+start_game_button.width+5), box_w, "orange")

    @start_game_button.event("on_click")
    def on_click():
        game.load_scene(Main())

    @exit_button.event("on_click")
    def on_click():
        game.quit()

    def __init__(self):
        super().__init__("dim grey")
        self.add_game_object(Lobby.title_box)
        self.add_game_object(Lobby.start_game_button)
        self.add_game_object(Lobby.exit_button)



class GameOverScreen(pgnull.Scene):
    def __init__(self):
        super().__init__("pink")

        self._game_objs = [pgnull.TextBox("Endstand: " + str(Main.score), topleft=(10, 10), fontsize=60),
                           pgnull.TextBox("Noch mal spielen? (j/n)", topleft=(10, 100), fontsize=40)
                           ]

    @staticmethod
    def on_update(ctx):
        if ctx.keyboard.j:
            game.load_scene(Main())
        elif ctx.keyboard.n:
            game.quit()
        

### REAL GAME
class Main(pgnull.Scene):
    score = None

    player = pgnull.Sprite("images/player.png", scale=0.2, pos=(50,50))
    coin = pgnull.Sprite("images/coin.png", scale=0.5)

    score_label = pgnull.TextBox(topleft=(10, 10), text="Punkte: "+str(score), color="black")

    def __init__(self):
        super().__init__("green")

        self._game_objs = [Main.player,
                           Main.coin,
                           Main.score_label]
        Main.score = 0

    def time_up():
        game.load_scene(GameOverScreen())

    def place_coin_and_score(points=10):
        # why doesn't python have do-while?
        loop = 10
        while loop:
            Main.coin.x = randint(0, WIDTH-Main.coin.width)
            Main.coin.y = randint(0, HEIGHT-Main.coin.height)

            if Main.player.colliderect(Main.coin):
                if loop == 1:
                    return
                loop -= 1
            else:
                break


        Main.score += points

    @staticmethod
    def on_update(context):
        player = Main.player
        coin = Main.coin

        Main.score_label.text = "Punkte: "+str(Main.score)

        player.scale = Vector2(0.2)
        if context.keyboard.left:
            player.rotation += 5
            player.x = player.x - 2
        elif context.keyboard.right:
            player.rotation -= 5
            player.x = player.x + 2
        if context.keyboard.up:
            player.y = player.y - 2
            player.scale = Vector2(player.scale.x, 0.8)
        if context.keyboard.down:
            player.scale = Vector2(player.scale.x, 0.8)
            player.y = player.y + 2

        player.x = clamp(player.x, 0, WIDTH - player.width)
        player.y = clamp(player.y, 0, HEIGHT - player.height)


        if player.colliderect(coin):
            Main.place_coin_and_score()
    @staticmethod
    def on_start():
        Main.place_coin_and_score(0)
        game.clock.schedule(Main.time_up, 15.0)


game.run_game(Lobby())
