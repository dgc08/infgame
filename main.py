#!/usr/bin/env python3

from random import randint
from pygame.math import Vector2,clamp
import pgnull

WIDTH = 600
HEIGHT = 600

lobby = pgnull.Scene("dim grey")
main = pgnull.Scene("green")

### Lobby
game = pgnull.Game(WIDTH, HEIGHT, "some game")

box_w = Vector2(180, 150)

title_box= pgnull.TextBox((300,100), "Some random ass game")
lobby.add_game_object(title_box)

start_game_button = pgnull.Button(((WIDTH-box_w.x)/2, 160), "Start", box_w, "orange")
@start_game_button.event("on_click")
def on_click():
    game.load_scene(main)

lobby.add_game_object(start_game_button)

exit_button = pgnull.Button(((WIDTH-box_w.x)/2, start_game_button.y+start_game_button.width+5), "Quit", box_w, "orange")
@exit_button.event("on_click")
def on_click():
    game.quit()

lobby.add_game_object(exit_button)

#game.run_game(lobby)

### REAL GAME

player = pgnull.Sprite("images/player.png", scale=0.2, pos=(50,50))
coin = pgnull.Sprite("images/coin.png", scale=0.5)

main.add_game_object(player)
main.add_game_object(coin)

score = 0
game_over = False

def time_up():
    global game_over, player, coin

    game_over = True
    player.active = False
    coin.active = False

def place_coin_and_score(points=10):
    global score
    # why doesn't python have do-while?
    loop = 10
    while loop:
        coin.x = randint(0, WIDTH-coin.width)
        coin.y = randint(0, HEIGHT-coin.height)

        if player.colliderect(coin):
            if loop == 1:
                return
            loop -= 1
        else:
            break


    score += points

@main.event("on_predraw")
def predraw():
    if game_over:
        game.screen.fill("pink")
        game.screen.draw_text("Endstand: " + str(score), topleft=(10, 10), fontsize=60)
        game.screen.draw_text("Noch mal spielen? (j/n)", topleft=(10, 100), fontsize=40)
    else:
        game.screen.draw_text("Punkte: " + str(score), color="black", topleft=(10, 10))

        

@main.event("on_update")
def update(context):
    global score
    global game_over

    if game_over and context.keyboard.j:
        game_over = False
        player.active = True
        coin.active = True
        score = 0
    elif game_over and context.keyboard.n:
        game.quit()
    elif game_over:
        pass
    else:
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
            place_coin_and_score()
        
@main.event("on_start")
def on_start():
    place_coin_and_score(0)
    game.clock.schedule(time_up, 15.0)

game.run_game(lobby)
