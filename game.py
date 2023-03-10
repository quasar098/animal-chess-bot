import pygame
from board import *
from toolbar import Toolbar


class Game:
    def __init__(self):
        pygame.init()
        self.history = [Board(self)]
        self.history_index = 0
        self.toolbar: Optional[Toolbar] = None
        self.surface: Optional[pygame.Surface] = None
        self.rotated = False

    @property
    def board(self):
        return self.history[self.history_index]

    @board.setter
    def board(self, val: Board):
        self.history[self.history_index] = val

    def loop(self):
        pygame.init()
        self.surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption("Animal Chess")
        clock = pygame.time.Clock()
        init_assets()
        self.toolbar = Toolbar(self)

        running = True
        while running:
            self.surface.fill(BG_COLOR)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.toolbar.handle_events(event)
                old_board = self.board.copy()
                if self.board.handle_events(event):
                    self.history_index += 1
                    self.history.insert(self.history_index-1, old_board)
                    self.history = self.history[:self.history_index+1]

            # code here
            self.board.draw((0, 0))
            self.toolbar.draw(self.surface)

            pygame.display.flip()
            clock.tick(FRAMERATE)
        pygame.quit()
