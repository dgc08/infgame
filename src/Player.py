import pgnull

from pygame import mouse
from pygame.math import Vector2

import math

from .Bullet import Bullet

SPEED = 2
BULLET_SPEED = 8

class Player(pgnull.Sprite):
    def __init__(self):
        super().__init__("images/player.png")
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

        # look at mouse
        mpos = Vector2(mouse.get_pos())

        angle = Vector2(0,0).angle_to(mpos-self.pos)
        self.rotation = (-1*angle)+180

        # shoot
        if ctx.keyboard.space:
            bullet = Bullet(Vector2(BULLET_SPEED).rotate(angle-45), self.pos)
            bullet.rotation = -(angle)-90
            pgnull.Game.get_game().scene.add_game_object(bullet)
