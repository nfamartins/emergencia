"""
Full-screen map overview (toggle with M).
Pre-renders the tile grid as a 1-px-per-tile surface at init time;
scales it to fit the screen at draw time.
"""
import pygame
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, COLOR_PLAYER,
                      COLOR_GRASS, COLOR_WATER, COLOR_ROAD,
                      COLOR_LOT_RES, COLOR_LOT_COM, COLOR_PLAZA,
                      COLOR_FOREST, COLOR_FARM)
from world.map import GRASS, WATER, ROAD, LOT_RES, LOT_COM, PLAZA, FOREST, FARM

_TILE_COLORS = {
    GRASS:   COLOR_GRASS,
    WATER:   COLOR_WATER,
    ROAD:    COLOR_ROAD,
    LOT_RES: COLOR_LOT_RES,
    LOT_COM: COLOR_LOT_COM,
    PLAZA:   COLOR_PLAZA,
    FOREST:  COLOR_FOREST,
    FARM:    COLOR_FARM,
}

_MARGIN        = 20
_OVERLAY_ALPHA = 210
_BORDER_COLOR  = (200, 200, 200)
_LABEL_COLOR   = (180, 180, 180)


class Minimap:
    def __init__(self, game_map):
        self._cols = game_map.cols
        self._rows = game_map.rows
        self._base = self._render_base(game_map)
        self._font = pygame.font.SysFont("monospace", 13)

    # ── init ─────────────────────────────────────────────────────────────────

    def _render_base(self, game_map) -> pygame.Surface:
        surf = pygame.Surface((self._cols, self._rows))
        for r in range(self._rows):
            for c in range(self._cols):
                color = _TILE_COLORS.get(game_map.tiles[r][c], COLOR_GRASS)
                surf.set_at((c, r), color)
        return surf

    # ── drawing ───────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, player, village) -> None:
        sw, sh = SCREEN_WIDTH, SCREEN_HEIGHT

        # dark background overlay
        overlay = pygame.Surface((sw, sh), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, _OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        # compute scale and position
        scale = min((sw - 2 * _MARGIN) / self._cols,
                    (sh - 2 * _MARGIN) / self._rows)
        mw = int(self._cols * scale)
        mh = int(self._rows * scale)
        mx = (sw - mw) // 2
        my = (sh - mh) // 2

        scaled = pygame.transform.scale(self._base, (mw, mh))
        surface.blit(scaled, (mx, my))
        pygame.draw.rect(surface, _BORDER_COLOR, (mx, my, mw, mh), 1)

        # player dot
        px = mx + int(player.x / TILE_SIZE * scale)
        py = my + int(player.y / TILE_SIZE * scale)
        pygame.draw.circle(surface, COLOR_PLAYER, (px, py), max(3, int(4 * scale)))
        pygame.draw.circle(surface, (0, 0, 0),   (px, py), max(3, int(4 * scale)), 1)

        # agent dots
        for agent in village.agents:
            ax = mx + int(agent.col * scale)
            ay = my + int(agent.row * scale)
            r  = max(1, int(2 * scale))
            pygame.draw.circle(surface, agent.color, (ax, ay), r)

        # labels
        surface.blit(
            self._font.render("M · fechar mapa", True, _LABEL_COLOR),
            (mx, my + mh + 6),
        )
        surface.blit(
            self._font.render(
                f"vila: col 10–330  ·  rural: col 335–{self._cols}",
                True, _LABEL_COLOR,
            ),
            (mx + mw - 380, my + mh + 6),
        )
