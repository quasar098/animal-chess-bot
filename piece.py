from utils import *


class Piece:
    image_id = None

    def __init__(self, x: int, y: int, team: Team):
        self.x = x
        self.y = y
        self.team: Optional[Team] = team

    def copy(self):
        return type(self)(self.x, self.y, self.team)

    @property
    def at_end(self):
        return self.team == Team.RED and self.y == 6 or self.team == Team.BLUE and self.y == 0

    def draw(self, screen: pygame.Surface, grabbed_piece, rotated: bool):
        bw, bh = BOARD_WIDTH*TILE_SIZE, BOARD_HEIGHT*TILE_SIZE
        if self == grabbed_piece:
            mp = pygame.mouse.get_pos()
            mp = clamp(mp[0], -50, bw), clamp(mp[1], -50, bh)
            screen.blit(images[(self.team, self.image_id)], (mp[0]-50, mp[1]-50))
            return
        pos = rotated_pos(self.pos, rotated)
        screen.blit(images[(self.team, self.image_id)], [po*TILE_SIZE for po in pos])
    
    @property
    def rect(self):
        return pygame.Rect(self.x*TILE_SIZE, self.y*TILE_SIZE, TILE_SIZE, TILE_SIZE)

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, val: tuple[int, int]):
        self.x, self.y = val

    @property
    def offsets(self):
        omod = (self.team == Team.RED)*2-1
        return [(go[0]*omod+self.x, go[1]*omod+self.y) for go in self._get_moveable_offsets()]

    def _get_moveable_offsets(self) -> Optional[list[tuple[int, int]]]:
        pass  # will be overridden


class Goose(Piece):
    image_id = ImageId.GOOSE

    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)

    def _get_moveable_offsets(self):
        return (0, 1), (0, 2)


class Knight(Piece):
    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)
        self.image_id = ImageId.KNIGHT

    def _get_moveable_offsets(self):
        return (2, 1), (1, 2), (-1, 2), (-2, 1), (1, -2), (2, -1), (-2, -1), (-1, -2)


class Monkey(Piece):
    image_id = ImageId.MONKEY

    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)

    def _get_moveable_offsets(self):
        return (2, 0), (1, 1), (0, 2), (-1, 1), (-2, 0), (-1, -1), (0, -2), (1, -1)


class Buffalo(Piece):
    image_id = ImageId.BUFFALO

    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)

    def _get_moveable_offsets(self):
        return (1, 1), (2, 1), (1, 2), (2, 2), (-2, 1), (-1, 1), (-1, 2), (-2, 2), (0, -1)


class Cobra(Piece):
    image_id = ImageId.COBRA

    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)

    def _get_moveable_offsets(self):
        return [(x, y) for x in range(-2, 3) for y in range(-2, 3) if max(abs(x), abs(y)) == 2]


class Pedestrian(Piece):
    image_id = ImageId.PEDESTRIAN

    def __init__(self, x: int, y: int, team: Team):
        super().__init__(x, y, team)

    def _get_moveable_offsets(self):
        return [(x, y) for x in range(-2, 3) for y in range(-2, 3) if max(abs(x), abs(y)) == 1]
