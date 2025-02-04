import pgnull

from pygame import mouse
from pygame.math import Vector2

import math

from .Bullet import Bullet

SPEED = 2
BULLET_SPEED = 8

screen_size = Vector2(pgnull.utils.glob_singleton["window"])

class Player(pgnull.Sprite):
    def __init__(self):
        super().__init__("images/player.png", pivot=(0,0))
        self.rotation = 90

    def update(self, ctx):
        # movement
        if ctx.keyboard.left or ctx.keyboard.a:
            self.x = self.x - SPEED
        elif ctx.keyboard.right or ctx.keyboard.d:
            self.x = self.x + SPEED
        if ctx.keyboard.up or ctx.keyboard.w:
            self.y = self.y - SPEED
        if ctx.keyboard.down or ctx.keyboard.s:
            self.y = self.y + SPEED

        pgnull.Game.get_game().scene.camera = self.center - screen_size/2

        if ctx.keyboard.e:
            self.rotation -= 1
        if ctx.keyboard.q:
            self.rotation += 1

        # look at mouse
        mpos = Vector2(mouse.get_pos())

        angle = Vector2(0,0).angle_to(mpos-self.pos + pgnull.Game.get_game().scene.camera)
        self.rotation = (-1*angle)+180

        # shoot
        if ctx.keyboard.space:
            bullet = Bullet(Vector2(BULLET_SPEED).rotate(angle-45), self.center)
            bullet.rotation = -(angle)-90
            pgnull.Game.get_game().scene.add_game_object(bullet)
