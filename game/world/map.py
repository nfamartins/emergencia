import pygame
from settings import (TILE_SIZE, MAP_COLS, MAP_ROWS,
                      COLOR_GRASS, COLOR_DIRT, COLOR_WATER, COLOR_VILLAGE)

GRASS   = 0
DIRT    = 1
WATER   = 2
VILLAGE = 3

_TINT_TILES = {GRASS, DIRT}
_BASE_COLORS = {
    GRASS:   COLOR_GRASS,
    DIRT:    COLOR_DIRT,
    WATER:   COLOR_WATER,
    VILLAGE: COLOR_VILLAGE,
}


class GameMap:
    def __init__(self):
        self.cols = MAP_COLS
        self.rows = MAP_ROWS
        self.tiles = self._generate()

    def _generate(self) -> list[list[int]]:
        tiles = [[GRASS] * self.cols for _ in range(self.rows)]

        for r in range(self.rows):
            for c in range(self.cols):
                if r == 0 or r == self.rows - 1 or c == 0 or c == self.cols - 1:
                    tiles[r][c] = WATER

        mid_r, mid_c = self.rows // 2, self.cols // 2

        for r in range(mid_r - 3, mid_r + 4):
            for c in range(mid_c - 3, mid_c + 4):
                tiles[r][c] = VILLAGE

        for r in range(mid_r + 5, mid_r + 10):
            for c in range(mid_c - 4, mid_c + 5):
                if 0 < r < self.rows - 1 and 0 < c < self.cols - 1:
                    tiles[r][c] = DIRT

        return tiles

    def _tile_color(self, tile: int, season_color: tuple) -> tuple:
        base = _BASE_COLORS[tile]
        if tile in _TINT_TILES:
            return (
                int(base[0] * 0.7 + season_color[0] * 0.3),
                int(base[1] * 0.7 + season_color[1] * 0.3),
                int(base[2] * 0.7 + season_color[2] * 0.3),
            )
        return base

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int, season_color: tuple):
        sw, sh = surface.get_width(), surface.get_height()
        for r in range(self.rows):
            for c in range(self.cols):
                x = c * TILE_SIZE - camera_x
                y = r * TILE_SIZE - camera_y
                if -TILE_SIZE < x < sw + TILE_SIZE and -TILE_SIZE < y < sh + TILE_SIZE:
                    color = self._tile_color(self.tiles[r][c], season_color)
                    pygame.draw.rect(surface, color, (x, y, TILE_SIZE - 1, TILE_SIZE - 1))
