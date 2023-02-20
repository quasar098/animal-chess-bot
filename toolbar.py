from board import *
from bot import Bot


class Toolbar:
    def __init__(self, game):
        self.game = game

        # https://onlineasciitools.com/generate-ascii-characters to find which ones are which
        self.medium_glyph = pygame.font.Font(join("assets", "chessglyph.ttf"), 25)
        self.big_glyph = pygame.font.Font(join("assets", "chessglyph.ttf"), 50)

        self.medium_font = pygame.font.SysFont("Arial", 20)
        self.medium_font_cache = {}

        # symbols
        dull_color = pygame.Color(220, 220, 220)
        self.rotate = self.big_glyph.render("\u0066", True, dull_color)
        self.hint = self.big_glyph.render("\u0067", True, dull_color)
        self.big_left = self.big_glyph.render("[", True, dull_color)
        self.big_right = self.big_glyph.render("]", True, dull_color)

    @property
    def rect(self):
        return pygame.Rect(BOARD_WIDTH * TILE_SIZE + 8, 8, SCREEN_WIDTH - (BOARD_WIDTH * TILE_SIZE) - 16,
                           BOARD_HEIGHT * TILE_SIZE - 16)

    @property
    def go_back_rect(self):
        return self.big_left.get_rect(topleft=self.rect.move(10, 10)[:2])

    @property
    def go_forward_rect(self):
        return self.big_left.get_rect(topright=self.rect.topright).move(-10, 10)

    @property
    def rotate_board_rect(self):
        return self.go_back_rect.move(0, self.go_back_rect.height + 10 + 8)

    @property
    def hint_rect(self):
        return self.go_forward_rect.move(0, self.go_forward_rect.height + 10 + 8)

    @property
    def who_is_winning_pos(self):
        return self.rect.move(0, 140).topleft

    @property
    def moves_rect(self):
        return self.rect.move(0, 170).inflate(-18, -18)

    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(
            screen, (32, 32, 32),
            self.go_back_rect.inflate(10, 10),
            border_radius=4
        )
        screen.blit(self.big_left, self.go_back_rect)

        pygame.draw.rect(
            screen, (32, 32, 32),
            self.go_forward_rect.inflate(10, 10),
            border_radius=4
        )
        screen.blit(self.big_right, self.big_right.get_rect(topright=self.go_forward_rect.topright))

        pygame.draw.rect(
            screen, (32, 32, 32),
            self.rotate_board_rect.inflate(10, 10),
            border_radius=4
        )
        screen.blit(self.rotate, self.rotate.get_rect(topright=self.rotate_board_rect.topright))

        pygame.draw.rect(
            screen, (32, 32, 32),
            self.hint_rect.inflate(10, 10),
            border_radius=4
        )
        screen.blit(self.hint, self.hint.get_rect(topright=self.hint_rect.topright))

        self.game.surface.blit(self.medium_font_text(self.get_win_diff()), self.who_is_winning_pos)

        moves = [hist.last_move_pair for hist in self.game.history if hist.last_move_pair is not None]
        pygame.draw.rect(self.game.surface, (60, 60, 63), self.moves_rect.inflate(8, 8), border_radius=4)
        for index, move in enumerate(moves.__reversed__()):
            alphabet = "abcdefghijklmnopqrstuvwxyz"
            text = f"{alphabet[move[0][0]]}{BOARD_HEIGHT - move[0][1]}" \
                   f"{alphabet[move[1][0]]}{BOARD_HEIGHT - move[1][1]}"

            text_pos = (
                self.moves_rect.x + (
                        ((self.moves_rect.y + index * 30) - self.moves_rect.top + 8) //
                        (SCREEN_HEIGHT - self.moves_rect.top)) * 60,
                (
                        ((self.moves_rect.y + index * 30) - self.moves_rect.top + 8)
                        % (SCREEN_HEIGHT - self.moves_rect.top) + self.moves_rect.top - 8
                )
            )

            if (((self.moves_rect.y + index * 30) - self.moves_rect.top + 8) //
                    (SCREEN_HEIGHT - self.moves_rect.top)) > 1:
                continue

            if -index + len(self.game.history) - 1 == self.game.history_index:
                pygame.draw.rect(self.game.surface, (70, 70, 73), self.medium_font_text(text).get_rect(
                    topleft=text_pos
                ).inflate(4, 4))
            self.game.surface.blit(self.medium_font_text(text), text_pos)

    def get_win_diff(self):
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
        for piece in self.game.board.pieces:
            scores[piece.team] += score_map[type(piece)]
        offset = scores[Team.BLUE] - scores[Team.RED]
        adds = (abs(offset) != 1) * "s"
        if offset > 200:
            return f"blue wins"
        elif offset < -200:
            return f"red wins"
        elif offset > 0:
            return f"blue up {offset} point{adds}"
        elif offset < 0:
            return f"red up {-offset} point{adds}"
        return "equal points"

    def medium_font_text(self, text: str):
        if text not in self.medium_font_cache:
            self.medium_font_cache[text] = self.medium_font.render(text, True, (255, 255, 255))
        return self.medium_font_cache[text]

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.go_back_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.history_index = clamp(self.game.history_index - 1, 0, len(self.game.history) - 1)
                if self.go_forward_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.history_index = clamp(self.game.history_index + 1, 0, len(self.game.history) - 1)
                if self.hint_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    Bot.make_best_move(self.game)
                if self.rotate_board_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.rotated = not self.game.rotated
