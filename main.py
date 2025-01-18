#!/usr/bin/env python3

from random import randint
import pgnull

game = pgnull.Game()

WIDTH = 400
HEIGHT = 400

game.open_screen(WIDTH, HEIGHT)

fox = pgnull.Sprite("fox", scale=(0.2,0.2))
fox.pos = 100, 100

coin = pgnull.Sprite("coin")

score = 0
game_over = False

def time_up():
    global game_over
    game_over = True

def place_coin():
    coin.x = randint(20, (WIDTH-20))
    coin.y = randint(20, (HEIGHT-20))

def draw():
    game.screen.fill(pgnull.Colors.GREEN)
    game.screen.draw_text("Punkte: " + str(score), color="black", topleft=(10, 10))

    coin.draw()
    fox.draw()

    if game_over:
        game.screen.fill("pink")
        game.screen.draw_text("Endstand: " + str(score), topleft=(10, 10), fontsize=60)
        game.screen.draw_text("Noch mal spielen? (j/n)", topleft=(10, 100), fontsize=40)

def update(context):
    global score
    global game_over

    if context.keyboard.left:
        fox.x = fox.x - 2
    elif context.keyboard.right:
        fox.x = fox.x + 2
    if context.keyboard.up:
        fox.y = fox.y - 2
    elif context.keyboard.down:
        fox.y = fox.y + 2

    coin_collected = fox.colliderect(coin)
    if coin_collected:
        score += 10
        place_coin()

    if game_over and context.keyboard.j:
        game_over = False
        score = 0

    if game_over and context.keyboard.n:
        game.quit()

    draw()

def on_exit():
    print("i am closnngig")

place_coin()
game.clock.schedule(time_up, 15.0)
game.register_event("on_close", on_exit)

game.run_game(update)
