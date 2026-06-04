"""
Village spatial layout — block positions, lot positions and types.
All coordinates are in tiles (1 tile = 1 m²).

Village structure (3×3 block grid, center = plaza):
    [NW][N ][NE]
    [W ][Pz][E ]
    [SW][S ][SE]

Block: 100 × 50 tiles  (4 lots wide × 2 lots tall)
Lot:    25 × 25 tiles
Street:  5 tiles wide
Margin: 10 tiles from map edge
"""
from dataclasses import dataclass, field
from typing import Literal, Optional

# ── geometry constants ───────────────────────────────────────────────────────

MARGIN       = 10   # tiles from map edge to first street
STREET_W     = 5    # street / sidewalk width in tiles
BLOCK_W      = 100  # block width  (E–W)
BLOCK_H      = 50   # block height (N–S)
LOT_W        = 25   # lot width
LOT_H        = 25   # lot height
LOTS_PER_ROW = 4    # lots along block width
LOTS_PER_COL = 2    # lots along block height

PLAZA_BLOCK  = (1, 1)   # (block_row, block_col) of the central plaza


# ── data classes ─────────────────────────────────────────────────────────────

@dataclass
class Lot:
    id:        int
    row:       int
    col:       int
    width:     int = LOT_W
    height:    int = LOT_H
    lot_type:  Literal["residential", "commercial"] = "residential"
    family_id: Optional[int] = None

    @property
    def center_row(self) -> int:
        return self.row + self.height // 2

    @property
    def center_col(self) -> int:
        return self.col + self.width // 2


# ── helpers ──────────────────────────────────────────────────────────────────

def block_origin(block_row: int, block_col: int) -> tuple[int, int]:
    """Top-left tile (row, col) of a block in the 3×3 grid."""
    r = MARGIN + STREET_W + block_row * (BLOCK_H + STREET_W)
    c = MARGIN + STREET_W + block_col * (BLOCK_W + STREET_W)
    return r, c


def _is_commercial(block_row: int, block_col: int,
                   lot_row: int, lot_col: int) -> bool:
    """True for the 12 lots that face the central plaza."""
    # North block  (0,1) — bottom lot row
    if (block_row, block_col) == (0, 1) and lot_row == LOTS_PER_COL - 1:
        return True
    # South block  (2,1) — top lot row
    if (block_row, block_col) == (2, 1) and lot_row == 0:
        return True
    # West block   (1,0) — rightmost lot column
    if (block_row, block_col) == (1, 0) and lot_col == LOTS_PER_ROW - 1:
        return True
    # East block   (1,2) — leftmost lot column
    if (block_row, block_col) == (1, 2) and lot_col == 0:
        return True
    return False


# ── public API ───────────────────────────────────────────────────────────────

def generate_lots() -> list[Lot]:
    """Return all 64 lots (12 commercial, 52 residential)."""
    lots: list[Lot] = []
    lot_id = 0
    for br in range(3):
        for bc in range(3):
            if (br, bc) == PLAZA_BLOCK:
                continue
            orig_r, orig_c = block_origin(br, bc)
            for lr in range(LOTS_PER_COL):
                for lc in range(LOTS_PER_ROW):
                    r = orig_r + lr * LOT_H
                    c = orig_c + lc * LOT_W
                    lt = "commercial" if _is_commercial(br, bc, lr, lc) else "residential"
                    lots.append(Lot(id=lot_id, row=r, col=c, lot_type=lt))
                    lot_id += 1
    return lots


def plaza_bounds() -> tuple[int, int, int, int]:
    """(row, col, height, width) of the central plaza tile area."""
    r, c = block_origin(*PLAZA_BLOCK)
    return r, c, BLOCK_H, BLOCK_W


def village_bounds() -> tuple[int, int, int, int]:
    """(row, col, height, width) of the full village footprint (including streets)."""
    h = STREET_W + 3 * BLOCK_H + 2 * STREET_W + STREET_W
    w = STREET_W + 3 * BLOCK_W + 2 * STREET_W + STREET_W
    return MARGIN, MARGIN, h, w
