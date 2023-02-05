from piece import *
if TYPE_CHECKING:
    from game import Game


class Board:
    def __init__(self, game):
        self.pieces: list[Piece] = []
        self.game: Game = game
        self.init_piece_locations()
        self.turns_passed = 0

        self.last_move_pair: Optional[tuple[tuple[int, int], tuple[int, int]]] = None
        self.grabbed_piece: Optional[Piece] = None
        self.last_grabbed_piece: Optional[Piece] = None
        self.first_piece_click = False
        self.whose_turn = Team.RED

    def __repr__(self):
        return f"<Board(turns={self.turns_passed})>"

    def copy(self, moreturns=False):
        new = Board(self.game)
        new.pieces = [piece.copy() for piece in self.pieces]
        new.last_move_pair = self.last_move_pair
        new.turns_passed = self.turns_passed+int(moreturns)
        new.whose_turn = self.whose_turn
        return new

    def draw(self, position: tuple[int, int]) -> None:
        self.game.surface.blit(images[(Team.NOTEAM, ImageId.BOARD)], position)

        if self.last_grabbed_piece:
            draw_highlight(self.game.surface, self.last_grabbed_piece.x, self.last_grabbed_piece.y)

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
                            draw_capture_hint(self.game.surface, hint[0], hint[1])
                        else:
                            draw_move_hint(self.game.surface, hint[0], hint[1])

        if self.last_move_pair is not None:
            draw_highlight(self.game.surface, *self.last_move_pair[0])
            draw_highlight(self.game.surface, *self.last_move_pair[1])

        if self.grabbed_piece:
            draw_outline(self.game.surface, self.grabbed_piece.x, self.grabbed_piece.y)

        for piece in self.pieces:
            piece.draw(self.game.surface, self.grabbed_piece)

    def try_move(self, one_piece):
        comrade_positions = [piece.pos for piece in self.pieces if piece.team == one_piece.team]
        enemy_positions = {piece.pos: piece for piece in self.pieces if piece.team != one_piece.team}
        mp = pygame.mouse.get_pos()
        mp = clamp(mp[0]//100, 0, BOARD_WIDTH-1), clamp(mp[1]//100, 0, BOARD_HEIGHT-1)
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
                    if piece.rect.collidepoint(pygame.mouse.get_pos()):
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
                    if piece.rect.collidepoint(pygame.mouse.get_pos()):
                        if self.last_grabbed_piece == piece and self.first_piece_click:
                            self.last_grabbed_piece = None
                            self.first_piece_click = False
                            return

    def init_piece_locations(self):
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
