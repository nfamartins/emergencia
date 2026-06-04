import sys
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_TEXT

_HUD_HEIGHT  = 36
_FOOTER_H    = 24
_HINT_COLOR  = (180, 180, 180)
_VER_COLOR   = (120, 120, 120)
_MODAL_BG    = (30,  30,  30)
_MODAL_BORDER= (200, 200, 200)
_PROMPT_COLOR= (220, 220, 100)

_VERSION_INFO = f"pygame {pygame.version.ver}  ·  Python {sys.version.split()[0]}"


class HUD:
    def __init__(self):
        pygame.font.init()
        self.font_main  = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_hint  = pygame.font.SysFont("monospace", 13)
        self._top_bar   = pygame.Surface((SCREEN_WIDTH, _HUD_HEIGHT), pygame.SRCALPHA)
        self._top_bar.fill((0, 0, 0, 140))
        self._bot_bar   = pygame.Surface((SCREEN_WIDTH, _FOOTER_H), pygame.SRCALPHA)
        self._bot_bar.fill((0, 0, 0, 120))

    def draw(self, surface: pygame.Surface, time_system) -> None:
        # barra superior: data + hora
        surface.blit(self._top_bar, (0, 0))
        surface.blit(
            self.font_main.render(str(time_system), True, COLOR_TEXT),
            (12, 9),
        )

        # barra inferior: dica de controles (esq) + versão (dir)
        bot_y = SCREEN_HEIGHT - _FOOTER_H
        surface.blit(self._bot_bar, (0, bot_y))
        surface.blit(
            self.font_hint.render("WASD / setas: mover  |  TAB: modo sistema", True, _HINT_COLOR),
            (12, bot_y + 5),
        )
        ver_surf = self.font_hint.render(_VERSION_INFO, True, _VER_COLOR)
        surface.blit(ver_surf, (SCREEN_WIDTH - ver_surf.get_width() - 12, bot_y + 5))

    def draw_day_end_prompt(self, surface: pygame.Surface, time_system) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 520, 180
        box_x = (SCREEN_WIDTH  - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        pygame.draw.rect(surface, _MODAL_BG,     (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(surface, _MODAL_BORDER, (box_x, box_y, box_w, box_h), 2, border_radius=8)

        def centered(surf, y):
            surface.blit(surf, (box_x + (box_w - surf.get_width()) // 2, y))

        centered(self.font_main.render("Fim do Dia", True, COLOR_TEXT),          box_y + 30)
        centered(self.font_hint.render(str(time_system), True, _HINT_COLOR),     box_y + 80)
        centered(self.font_hint.render("ENTER para dormir e salvar", True, _PROMPT_COLOR), box_y + 120)
