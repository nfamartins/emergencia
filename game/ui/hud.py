import pygame
from settings import SCREEN_WIDTH, COLOR_TEXT

_HUD_HEIGHT = 36
_HINT_COLOR = (180, 180, 180)


class HUD:
    def __init__(self):
        pygame.font.init()
        self.font_main  = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_hint  = pygame.font.SysFont("monospace", 14)
        self._bar = pygame.Surface((SCREEN_WIDTH, _HUD_HEIGHT), pygame.SRCALPHA)
        self._bar.fill((0, 0, 0, 140))

    def draw(self, surface: pygame.Surface, time_system):
        surface.blit(self._bar, (0, 0))
        surface.blit(
            self.font_main.render(str(time_system), True, COLOR_TEXT),
            (12, 9),
        )
        surface.blit(
            self.font_hint.render("WASD / setas: mover  |  TAB: modo sistema", True, _HINT_COLOR),
            (12, surface.get_height() - 22),
        )
