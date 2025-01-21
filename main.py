#!/usr/bin/env python3

from random import randint
from pygame.math import Vector2,clamp
import pgnull

### Lobby
lobby = pgnull.Game()

WIDTH = 600
HEIGHT = 600

lobby.open_screen(WIDTH, HEIGHT)

@lobby.event("on_update")
def update(context):
    lobby.screen.fill("dim grey")
    lobby.screen.draw_rect(main_box, "sky blue")
    lobby.screen.draw_rect(timer_box, "sky blue")
    lobby.screen.draw_textbox("69", timer_box, fontsize=45)
    for box in answer_boxes:
        lobby.screen.draw_rect(box, "orange")

@lobby.event("on_mouse_down")
def on_mouse_down(pos, button):
    if button ==  1:
        for i, box in enumerate(answer_boxes):
            if box.collidepoint(pos):
                print("clicked ans", i)
                if i==2:
                    lobby.quit()

main_box = pgnull.Box(50, 40, 820, 240)
timer_box = pgnull.Box(990, 40, 240, 240)
answer_box1 = pgnull.Box(50, 358, 495, 165)
answer_box2 = pgnull.Box(735, 358, 495, 165)
answer_box3 = pgnull.Box(50, 538, 495, 165)
answer_box4 = pgnull.Box(735, 538, 495, 165)

answer_boxes = [answer_box1, answer_box2, answer_box3, answer_box4]

lobby.run_game()
print("running another")

### REAL GAME
game = pgnull.Game(lobby)

player = pgnull.Sprite("images/player.png", scale=0.2, pos=(50,50))
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
    loop = 10
    while loop:
        coin.x = randint(0, WIDTH-coin.width)
        coin.y = randint(0, HEIGHT-coin.height)

        if player.colliderect(coin):
            loop -= 1
        else:
            loop = 0

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
        player.queue()
        coin.queue()
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
            score += 10
            place_coin()


place_coin()
game.clock.schedule(time_up, 15.0)

game.run_game()
