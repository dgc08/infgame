#!/usr/bin/env python3

from random import randint
from pygame.math import Vector2
import pgnull

game = pgnull.Game()

WIDTH = 400
HEIGHT = 400

game.open_screen(WIDTH, HEIGHT)

fox = pgnull.Sprite("images/fox.png", scale=(0.2,0.2), pos=(50,50))
#fox.pos = (50,50)

coin = pgnull.Sprite("images/coin.png", scale=(0.2,0.2))

score = 0
game_over = False

def time_up():
    global game_over, fox, coin
    
    game_over = True
    del fox
    del coin

def place_coin():
    # why doesn't python has do-while?
    loop = True
    while loop:
        coin.x = randint(20, (WIDTH-20))
        coin.y = randint(20, (HEIGHT-20))
        loop = fox.colliderect(coin)

def draw():
    if game_over:
        game.screen.fill("pink")
        game.screen.draw_text("Endstand: " + str(score), topleft=(10, 10), fontsize=60)
        game.screen.draw_text("Noch mal spielen? (j/n)", topleft=(10, 100), fontsize=40)
    else:
        game.screen.fill(pgnull.Colors.GREEN)
        game.screen.draw_text("Punkte: " + str(score), color="black", topleft=(10, 10))

        coin.draw()
        fox.draw()

def update(context):
    global score
    global game_over

    if game_over and context.keyboard.j:
        game_over = False
        score = 0
    elif game_over and context.keyboard.n:
        game.quit()
    elif game_over:
        pass
    else:
        fox.scale = Vector2(0.2, 0.2)
        if context.keyboard.left:
            fox.rotation += 5
            fox.x = fox.x - 2
        elif context.keyboard.right:
            fox.rotation -= 5
            fox.x = fox.x + 2
        if context.keyboard.up:
            fox.y = fox.y - 2
            fox.scale = Vector2(fox.scale.x, 0.4)
        if context.keyboard.down:
            fox.scale = Vector2(fox.scale.x, 0.1)
            fox.y = fox.y + 2


        if fox.colliderect(coin):
            score += 10
            print(fox.pos)
            place_coin()

    draw()

place_coin()
game.clock.schedule(time_up, 15.0)

game.run_game(update)
