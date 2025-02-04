import pgnull

from pygame.math import Vector2

class Bullet(pgnull.Sprite):
    def __init__(self, direction, pos):
        super().__init__("images/bullet.png")
        self.direction = direction
        self.pos = pos

    def update(self, ctx):
        self.pos += self.direction

        if self.pos.x > 20000 or self.pos.y > 20000:
            self.dequeue()
