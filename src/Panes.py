from pgnull import GameObject

class VerticalPane(GameObject):
    def __init__(self, element_gap):
        super().__init__()
        self.element_gap = element_gap

    def add_game_object(self, game_obj):
        if len(self._game_objs) == 0:
            game_obj.y = 0
        else:
            game_obj.y = self._game_objs[-1].y + self._game_objs[-1].height
            game_obj.y += self.element_gap

        game_obj.x = 0
        super().add_game_object(game_obj)

    @property
    def height(self):
        if len(self._game_objs) == 0:
            return 0
        else:
            return self._game_objs[-1].y + self._game_objs[-1].height
    @property
    def width(self):
        if len(self._game_objs) == 0:
            return 0

        max_w = 0
        for g in self._game_objs:
            if g.width > max_w:
                max_w = g.width

        return max_w

# same code as above just y<->x and width <-> height
class HorizontalPane(GameObject):
    def __init__(self, element_gap):
        super().__init__()
        self.element_gap = element_gap

    def add_game_object(self, game_obj):
        if len(self._game_objs) == 0:
            game_obj.x = 0
        else:
            game_obj.x = self._game_objs[-1].y + self._game_objs[-1].width
            game_obj.x += self.element_gap

        game_obj.y = 0
        super().add_game_object(game_obj)

    @property
    def height(self):
        if len(self._game_objs) == 0:
            return 0

        max_w = 0
        for g in self._game_objs:
            if g.width > max_w:
                max_w = g.width

        return max_w
    @property
    def width(self):
        if len(self._game_objs) == 0:
            return 0
        else:
            return self._game_objs[-1].x + self._game_objs[-1].width
