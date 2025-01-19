#!/usr/bin/env python3

from random import randint
from pygame.math import Vector2,clamp
import pgnull

game = pgnull.Game()

WIDTH = 600
HEIGHT = 600

game.open_screen(WIDTH, HEIGHT)

player = pgnull.Sprite("images/player.png", scale=(0.2,0.2), pos=(50,50))
coin = pgnull.Sprite("images/coin.png", scale=0.5)

score = 0
game_over = False

def time_up():
    global game_over, player, coin
    
    game_over = True
    player.dequeue()
    coin.dequeue()

def place_coin():
    # why doesn't python have do-while?
    loop = True
    while loop:
        coin.x = randint(20, (WIDTH-20))
        coin.y = randint(20, (HEIGHT-20))
        loop = player.colliderect(coin)

@game.event("on_draw")
def draw():
    if game_over:
        game.screen.fill("pink")
        game.screen.draw_text("Endstand: " + str(score), topleft=(10, 10), fontsize=60)
        game.screen.draw_text("Noch mal spielen? (j/n)", topleft=(10, 100), fontsize=40)
    else:
        game.screen.fill(pgnull.Colors.GREEN)
        game.screen.draw_text("Punkte: " + str(score), color="black", topleft=(10, 10))

        

@game.event("update")
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
        player.scale = Vector2(0.2, 0.2)
        if context.keyboard.left:
            player.rotation += 5
            player.x = player.x - 2
        elif context.keyboard.right:
            player.rotation -= 5
            player.x = player.x + 2
        if context.keyboard.up:
            player.y = player.y - 2
            player.scale = Vector2(player.scale.x, 0.4)
        if context.keyboard.down:
            player.scale = Vector2(player.scale.x, 0.1)
            player.y = player.y + 2

        player.x = clamp(player.x, 0, WIDTH - player.width)
        player.y = clamp(player.y, 0, HEIGHT - player.height)


        if player.colliderect(coin):
            score += 10
            place_coin()


place_coin()
game.clock.schedule(time_up, 15.0)

game.run_game()
