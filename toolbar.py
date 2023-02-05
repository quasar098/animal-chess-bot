from board import *
from bot import Bot


class Toolbar:
    def __init__(self, game):
        self.game = game

        # https://onlineasciitools.com/generate-ascii-characters to find which ones are which
        self.font = pygame.font.Font(join("assets", "chessglyph.ttf"), 25)
        self.big_font = pygame.font.Font(join("assets", "chessglyph.ttf"), 50)

        # symbols
        dull_color = pygame.Color(220, 220, 220)
        self.rotate = self.big_font.render("\u0066", True, dull_color)
        self.hint = self.big_font.render("\u0067", True, dull_color)
        self.big_left = self.big_font.render("[", True, dull_color)
        self.big_right = self.big_font.render("]", True, dull_color)

    @property
    def rect(self):
        return pygame.Rect(BOARD_WIDTH*TILE_SIZE+8, 8, SCREEN_WIDTH-(BOARD_WIDTH*TILE_SIZE)-16,
                           BOARD_HEIGHT*TILE_SIZE-16)

    @property
    def go_back_rect(self):
        return self.big_left.get_rect(topleft=self.rect.move(10, 10)[:2])

    @property
    def go_forward_rect(self):
        return self.big_left.get_rect(topright=self.rect.topright).move(-10, 10)

    @property
    def rotate_board_rect(self):
        return self.go_back_rect.move(0, self.go_back_rect.height+10+8)

    @property
    def hint_rect(self):
        return self.go_forward_rect.move(0, self.go_forward_rect.height+10+8)

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

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.go_back_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.history_index = clamp(self.game.history_index-1, 0, len(self.game.history)-1)
                if self.go_forward_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.history_index = clamp(self.game.history_index+1, 0, len(self.game.history)-1)
                if self.hint_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    Bot.make_best_move(self.game)
                if self.rotate_board_rect.inflate(10, 10).collidepoint(pygame.mouse.get_pos()):
                    self.game.rotated = not self.game.rotated
