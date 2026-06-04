import random
import pygame
from settings import (TILE_SIZE, MAP_COLS, MAP_ROWS,
                      COLOR_GRASS, COLOR_WATER, COLOR_ROAD,
                      COLOR_LOT_RES, COLOR_LOT_COM, COLOR_PLAZA,
                      COLOR_FOREST, COLOR_FARM)
from world.layout import (generate_lots, block_origin, plaza_bounds,
                          village_bounds, PLAZA_BLOCK, BLOCK_W, BLOCK_H,
                          LOTS_PER_ROW, LOTS_PER_COL, LOT_W, LOT_H)

# ── tile types ────────────────────────────────────────────────────────────────
GRASS   = 0
WATER   = 1
ROAD    = 2
LOT_RES = 3
LOT_COM = 4
PLAZA   = 5
FOREST  = 6
FARM    = 7

_BASE_COLORS = {
    GRASS:   COLOR_GRASS,
    WATER:   COLOR_WATER,
    ROAD:    COLOR_ROAD,
    LOT_RES: COLOR_LOT_RES,
    LOT_COM: COLOR_LOT_COM,
    PLAZA:   COLOR_PLAZA,
    FOREST:  COLOR_FOREST,
    FARM:    COLOR_FARM,
}
_TINT_TILES = {GRASS, FARM}   # natural surfaces receive season tint

# ── rural features (deterministic seed) ───────────────────────────────────────
_RURAL_START_COL = 335   # tiles, right edge of village road

_FOREST_CLUSTERS = [     # (center_row, center_col, radius)
    ( 55, 375, 15),
    ( 30, 535, 12),
    ( 40, 630, 10),
    ( 88, 690,  8),
    (128, 570, 12),
    (140, 650, 10),
]

_FARM_BOUNDS = (15, 385, 40, 120)   # (row, col, height, width) — fazenda inicial

_LAKE_CENTER = (152, 545)           # (row, col)
_LAKE_AXES   = (38, 24)             # (semi-major a, semi-minor b)

_RIVER_ROWS  = range(3, 8)          # top of map, rural side only


class GameMap:
    def __init__(self):
        self.cols = MAP_COLS
        self.rows = MAP_ROWS
        self.lots = generate_lots()
        self.tiles = self._generate()

    # ── generation ──────────────────────────────────────────────────────────

    def _generate(self) -> list[list[int]]:
        tiles = [[GRASS] * self.cols for _ in range(self.rows)]
        self._paint_village(tiles)
        self._paint_river(tiles)
        self._paint_farm(tiles)
        self._paint_forests(tiles)
        self._paint_lake(tiles)
        self._paint_roads(tiles)
        return tiles

    def _paint_village(self, tiles):
        vr, vc, vh, vw = village_bounds()
        # Fill entire village footprint with ROAD, then overwrite with blocks
        for r in range(vr, vr + vh):
            for c in range(vc, vc + vw):
                tiles[r][c] = ROAD

        for br in range(3):
            for bc in range(3):
                orig_r, orig_c = block_origin(br, bc)
                if (br, bc) == PLAZA_BLOCK:
                    for r in range(orig_r, orig_r + BLOCK_H):
                        for c in range(orig_c, orig_c + BLOCK_W):
                            tiles[r][c] = PLAZA
                else:
                    for lot in (l for l in self.lots
                                if orig_r <= l.row < orig_r + BLOCK_H
                                and orig_c <= l.col < orig_c + BLOCK_W):
                        tt = LOT_COM if lot.lot_type == "commercial" else LOT_RES
                        for r in range(lot.row, lot.row + lot.height):
                            for c in range(lot.col, lot.col + lot.width):
                                tiles[r][c] = tt

    def _paint_river(self, tiles):
        for r in _RIVER_ROWS:
            for c in range(_RURAL_START_COL, self.cols):
                tiles[r][c] = WATER
        # Short diagonal section upper-left of rural
        for i in range(8):
            r, c = 8 + i, _RURAL_START_COL + i
            if 0 <= r < self.rows and 0 <= c < self.cols:
                tiles[r][c] = WATER

    def _paint_farm(self, tiles):
        fr, fc, fh, fw = _FARM_BOUNDS
        for r in range(fr, fr + fh):
            for c in range(fc, fc + fw):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    tiles[r][c] = FARM

    def _paint_forests(self, tiles):
        for cr, cc, radius in _FOREST_CLUSTERS:
            rng = random.Random(cr * 997 + cc)
            for r in range(cr - radius, cr + radius + 1):
                for c in range(cc - radius, cc + radius + 1):
                    if 0 <= r < self.rows and 0 <= c < self.cols:
                        dist = ((r - cr) ** 2 + (c - cc) ** 2) ** 0.5
                        if dist <= radius * (0.65 + 0.35 * rng.random()):
                            tiles[r][c] = FOREST

    def _paint_lake(self, tiles):
        cr, cc = _LAKE_CENTER
        a, b   = _LAKE_AXES
        for r in range(cr - b - 1, cr + b + 2):
            for c in range(cc - a - 1, cc + a + 2):
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    if ((r - cr) / b) ** 2 + ((c - cc) / a) ** 2 <= 1.0:
                        tiles[r][c] = WATER

    def _paint_roads(self, tiles):
        # Vertical road: right edge of village / left edge of rural
        for r in range(self.rows):
            for c in range(330, _RURAL_START_COL):
                if tiles[r][c] == GRASS:
                    tiles[r][c] = ROAD
        # Horizontal road: bottom of rural area
        for r in range(188, 193):
            for c in range(_RURAL_START_COL, self.cols):
                tiles[r][c] = ROAD

    # ── rendering ────────────────────────────────────────────────────────────

    def _tile_color(self, tile: int, season_color: tuple) -> tuple:
        base = _BASE_COLORS.get(tile, COLOR_GRASS)
        if tile in _TINT_TILES:
            return (
                int(base[0] * 0.7 + season_color[0] * 0.3),
                int(base[1] * 0.7 + season_color[1] * 0.3),
                int(base[2] * 0.7 + season_color[2] * 0.3),
            )
        return base

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int,
             season_color: tuple) -> None:
        sw = surface.get_width()
        sh = surface.get_height()
        c_start = max(0, camera_x // TILE_SIZE)
        c_end   = min(self.cols, (camera_x + sw) // TILE_SIZE + 2)
        r_start = max(0, camera_y // TILE_SIZE)
        r_end   = min(self.rows, (camera_y + sh) // TILE_SIZE + 2)
        for r in range(r_start, r_end):
            for c in range(c_start, c_end):
                x = c * TILE_SIZE - camera_x
                y = r * TILE_SIZE - camera_y
                color = self._tile_color(self.tiles[r][c], season_color)
                pygame.draw.rect(surface, color, (x, y, TILE_SIZE - 1, TILE_SIZE - 1))
