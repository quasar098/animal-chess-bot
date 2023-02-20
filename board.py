from piece import *
if TYPE_CHECKING:
    from game import Game


class Board:
    FONT = None

    def __init__(self, game):
        self.pieces: list[Piece] = []
        self.game: Game = game
        self.init_piece_locations()

        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890".lower()
        if Board.FONT is None:
            Board.FONT = pygame.font.SysFont("Segoe UI semibold", 20)
        self.dark_letters = {}
        self.light_letters = {}

        for _ in letters:
            self.dark_letters[_] = self.FONT.render(_, True, (141, 103, 94))
            self.light_letters[_] = self.FONT.render(_, True, (231, 205, 178))

        self.last_move_pair: Optional[tuple[tuple[int, int], tuple[int, int]]] = None
        self.grabbed_piece: Optional[Piece] = None
        self.last_grabbed_piece: Optional[Piece] = None
        self.first_piece_click = False
        self.whose_turn = Team.RED

    def __repr__(self):
        return f"<Board()>"

    def copy(self) -> "Board":
        new = Board(self.game)
        new.pieces = [piece.copy() for piece in self.pieces]
        new.last_move_pair = self.last_move_pair
        new.whose_turn = self.whose_turn
        return new

    def draw(self, position: tuple[int, int]) -> None:
        self.game.surface.blit(images[(Team.NOTEAM, ImageId.BOARD)], position)

        # draw letters
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()
        for _ in range(0, BOARD_WIDTH):
            pos = (6+_*TILE_SIZE+73, BOARD_WIDTH*TILE_SIZE-35)
            mod = _
            if self.game.rotated:
                mod = BOARD_WIDTH-_-1
            self.game.surface.blit((self.light_letters, self.dark_letters)[_ % 2][letters[mod]], pos)

        for _ in range(0, BOARD_HEIGHT):
            pos = (7, _*TILE_SIZE+7)
            mod = _+1
            if not self.game.rotated:
                mod = BOARD_HEIGHT-_
            self.game.surface.blit((self.light_letters, self.dark_letters)[_ % 2][str(mod)], pos)

        # more stuff
        if self.last_grabbed_piece:
            draw_highlight(self.game.surface, *rotated_pos((self.last_grabbed_piece.x, self.last_grabbed_piece.y),
                                                           self.game.rotated))

            # draw hints
            if self.last_grabbed_piece.team != self.whose_turn:
                comrade_positions = [piece.pos for piece in self.pieces if piece.team == self.last_grabbed_piece.team]
                enemy_positions = [piece.pos for piece in self.pieces if piece.team != self.last_grabbed_piece.team]
                for hint in self.last_grabbed_piece.offsets:
                    if not (BOARD_HEIGHT > hint[1] >= 0):
                        continue
                    if not (BOARD_WIDTH > hint[0] >= 0):
                        continue
                    if hint not in comrade_positions:
                        if hint in enemy_positions:
                            draw_capture_hint(self.game.surface, *rotated_pos((hint[0], hint[1]), self.game.rotated))
                        else:
                            draw_move_hint(self.game.surface, *rotated_pos((hint[0], hint[1]), self.game.rotated))

        if self.last_move_pair is not None:
            draw_highlight(self.game.surface, *rotated_pos(self.last_move_pair[0], self.game.rotated))
            draw_highlight(self.game.surface, *rotated_pos(self.last_move_pair[1], self.game.rotated))

        if self.grabbed_piece:
            draw_outline(self.game.surface, *rotated_big_pos((self.grabbed_piece.x, self.grabbed_piece.y),
                                                             self.game.rotated))

        for piece in self.pieces:
            piece.draw(self.game.surface, self.grabbed_piece, self.game.rotated)

    def flip_turn(self):
        self.whose_turn = Team.RED if self.whose_turn == Team.BLUE else Team.BLUE

    def moves(self) -> list["Board"]:
        moves: list["Board"] = []
        occupied = [piece.pos for piece in self.pieces if piece.team != self.whose_turn]
        for piece in self.pieces:
            if piece.team == self.whose_turn:
                continue
            movings = [o for o in piece.offsets
                       if 0 <= o[0] < BOARD_WIDTH and 0 <= o[1] < BOARD_HEIGHT and o not in occupied]
            for move in movings:
                new = self.make_copy_with_move(piece.pos, move)
                new.flip_turn()
                moves.append(new)
        moves = sorted(moves, key=Board.get_who_is_winning, reverse=self.whose_turn == Team.RED)
        return moves

    @property
    def finished(self):
        return len([piece for piece in self.pieces if isinstance(piece, Pedestrian)]) != 2

    def make_copy_with_move(self, origin, dest):
        copy = self.copy()
        original = [co for co in copy.pieces if co.pos == origin][0]
        copy.pieces = [piece for piece in copy.pieces if piece.pos != dest or piece.team != self.whose_turn]
        copy.last_move_pair = (original.pos, dest)
        original.pos = dest
        if original.at_end and isinstance(original, Goose):
            copy.pieces.remove(original)
            copy.pieces.append(Monkey(original.x, original.y, original.team))
        return copy

    def get_who_is_winning(self):
        """0 = red is winning, 100 = blue is winning"""
        # 0 = red, 100 = blue
        scores = {
            Team.BLUE: 0,
            Team.RED: 0
        }
        score_map = {
            Goose: 1,
            Knight: 3,
            Monkey: 3,
            Buffalo: 5,
            Cobra: 6,
            Pedestrian: 1000,
            Piece: -100
        }
        for piece in self.pieces:
            scores[piece.team] += score_map[type(piece)]
            if piece.team == Team.BLUE:
                scores[Team.BLUE] += (BOARD_HEIGHT-piece.y-1)*0.03
            if piece.team == Team.RED:
                scores[Team.RED] += piece.y*0.03
        whomst = 50
        whomst += scores[Team.BLUE]
        whomst -= scores[Team.RED]
        return int(clamp(whomst, 0, 100))

    def try_move(self, one_piece):
        comrade_positions = [piece.pos for piece in self.pieces if piece.team == one_piece.team]
        enemy_positions = {piece.pos: piece for piece in self.pieces if piece.team != one_piece.team}
        mp = pygame.mouse.get_pos()
        mp = clamp(mp[0]//100, 0, BOARD_WIDTH-1), clamp(mp[1]//100, 0, BOARD_HEIGHT-1)
        mp = rotated_pos(mp, self.game.rotated)
        if one_piece.team != self.whose_turn:
            for hint in one_piece.offsets:
                if hint != mp:
                    continue
                if hint not in comrade_positions:
                    # piece moves
                    if hint in enemy_positions:
                        self.pieces.remove(enemy_positions[hint])
                        if isinstance(enemy_positions[hint], Pedestrian):
                            play_sound(SoundId.GAME_OVER)
                            # game over
                        play_sound(SoundId.TAKE)
                        # takes
                    else:
                        play_sound(SoundId.MOVE)
                        # just moves
                    self.whose_turn = Team.RED if self.whose_turn == Team.BLUE else Team.BLUE
                    self.last_move_pair = one_piece.pos, mp
                    one_piece.pos = mp
                    self.first_piece_click = False
                    return True
        return False

    def handle_events(self, event: pygame.event.Event):
        bettermp = rotated_big_pos(pygame.mouse.get_pos(), self.game.rotated)

        # mouse down
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:

                # grab piece
                if self.last_grabbed_piece is not None:
                    if self.try_move(self.last_grabbed_piece):
                        if isinstance(self.last_grabbed_piece, Goose) and self.last_grabbed_piece.at_end:
                            self.pieces = [piece for piece in self.pieces if piece != self.last_grabbed_piece]
                            self.pieces.append(Monkey(
                                self.last_grabbed_piece.x, self.last_grabbed_piece.y, self.last_grabbed_piece.team
                            ))
                        self.grabbed_piece = None
                        self.last_grabbed_piece = None
                        return True

                for piece in self.pieces:
                    if piece.rect.collidepoint(bettermp):
                        self.grabbed_piece = piece
                        self.first_piece_click = piece == self.last_grabbed_piece
                        self.last_grabbed_piece = piece
                        return

                self.last_grabbed_piece = None

        # mouse up
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:

                # drop piece
                if self.grabbed_piece is None:
                    return

                if self.try_move(self.grabbed_piece):
                    if isinstance(self.last_grabbed_piece, Goose) and self.last_grabbed_piece.at_end:
                        self.pieces = [piece for piece in self.pieces if piece != self.last_grabbed_piece]
                        self.pieces.append(Monkey(
                            self.last_grabbed_piece.x, self.last_grabbed_piece.y, self.last_grabbed_piece.team
                        ))
                    self.grabbed_piece = None
                    self.last_grabbed_piece = None
                    return True

                self.grabbed_piece = None

                for piece in self.pieces:
                    if piece.rect.collidepoint(bettermp):
                        if self.last_grabbed_piece == piece and self.first_piece_click:
                            self.last_grabbed_piece = None
                            self.first_piece_click = False
                            return

    def init_piece_locations(self):
        if BOARD_WIDTH == BOARD_HEIGHT == 7:
            self.pieces = [
                Buffalo(0, 0, Team.RED),
                Knight(1, 0, Team.RED),
                Cobra(2, 0, Team.RED),
                Pedestrian(3, 0, Team.RED),
                Cobra(4, 0, Team.RED),
                Knight(5, 0, Team.RED),
                Buffalo(6, 0, Team.RED),
                Goose(0, 1, Team.RED),
                Goose(1, 1, Team.RED),
                Monkey(2, 1, Team.RED),
                Buffalo(3, 1, Team.RED),
                Monkey(4, 1, Team.RED),
                Goose(5, 1, Team.RED),
                Goose(6, 1, Team.RED),

                Buffalo(0, 6, Team.BLUE),
                Knight(1, 6, Team.BLUE),
                Cobra(2, 6, Team.BLUE),
                Pedestrian(3, 6, Team.BLUE),
                Cobra(4, 6, Team.BLUE),
                Knight(5, 6, Team.BLUE),
                Buffalo(6, 6, Team.BLUE),
                Goose(0, 5, Team.BLUE),
                Goose(1, 5, Team.BLUE),
                Monkey(2, 5, Team.BLUE),
                Buffalo(3, 5, Team.BLUE),
                Monkey(4, 5, Team.BLUE),
                Goose(5, 5, Team.BLUE),
                Goose(6, 5, Team.BLUE),
            ]
        if BOARD_WIDTH == BOARD_HEIGHT == 6:
            self.pieces = [
                Buffalo(0, 0, Team.RED),
                Knight(1, 0, Team.RED),
                Monkey(2, 0, Team.RED),
                Pedestrian(3, 0, Team.RED),
                Knight(4, 0, Team.RED),
                Buffalo(5, 0, Team.RED),
                Goose(0, 1, Team.RED),
                Goose(1, 1, Team.RED),
                Goose(2, 1, Team.RED),
                Monkey(3, 1, Team.RED),
                Goose(4, 1, Team.RED),
                Goose(5, 1, Team.RED),

                Buffalo(0, 5, Team.BLUE),
                Knight(1, 5, Team.BLUE),
                Monkey(3, 5, Team.BLUE),
                Pedestrian(2, 5, Team.BLUE),
                Knight(4, 5, Team.BLUE),
                Buffalo(5, 5, Team.BLUE),
                Goose(0, 4, Team.BLUE),
                Goose(1, 4, Team.BLUE),
                Monkey(2, 4, Team.BLUE),
                Goose(3, 4, Team.BLUE),
                Goose(4, 4, Team.BLUE),
                Goose(5, 4, Team.BLUE),
            ]
