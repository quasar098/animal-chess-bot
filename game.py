import pygame
from board import *
from toolbar import Toolbar


class Game:
    def __init__(self):
        self.history = [Board(self)]
        self.history_index = 0
        self.toolbar: Optional[Toolbar] = None
        self.surface: Optional[pygame.Surface] = None

    @property
    def board(self):
        return self.history[self.history_index]

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
                bc = self.board.copy()
                if self.board.handle_events(event):
                    self.history_index += 1
                    self.history.insert(self.history_index-1, bc)
                    self.board.turns_passed += 1

            # code here
            self.board.draw((0, 0))
            self.toolbar.draw(self.surface)

            pygame.display.flip()
            clock.tick(FRAMERATE)
        pygame.quit()
