SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Emergência"

TILE_SIZE = 32
MAP_COLS  = 750   # ~320 village + ~420 rural (1 tile = 1 m)
MAP_ROWS  = 200

HOURS_PER_DAY    = 24
SECONDS_PER_HOUR = 1.0   # 1 segundo real = 1 hora de jogo
DAY_START_HOUR   = 6
DAY_END_HOUR     = 22

DAYS_PER_MONTH  = 30
MONTHS_PER_YEAR = 12

# Meses 0-indexados: 0-2 Verão | 3-5 Outono | 6-8 Inverno | 9-11 Primavera
SEASONS = {
    "Verão":     {"months": [0, 1, 2],   "color": (210, 180, 100)},
    "Outono":    {"months": [3, 4, 5],   "color": (180, 130,  70)},
    "Inverno":   {"months": [6, 7, 8],   "color": (160, 180, 200)},
    "Primavera": {"months": [9, 10, 11], "color": (120, 180, 100)},
}

# ── tile colors (paleta terrosa, sem cores puras RGB) ─────────────────────────
COLOR_GRASS        = ( 86, 130,  46)   # campo aberto
COLOR_WATER        = ( 64, 164, 223)   # rio, lagoa
COLOR_ROAD         = (130, 100,  60)   # estrada de terra / rua
COLOR_LOT_RES      = (190, 170, 140)   # lote residencial
COLOR_LOT_COM      = (155, 175, 185)   # lote comercial / institucional
COLOR_PLAZA        = (205, 195, 165)   # praça central
COLOR_FOREST       = ( 35,  90,  30)   # mata
COLOR_FARM         = (160, 135,  65)   # terra agrícola

# ── other colors ──────────────────────────────────────────────────────────────
COLOR_PLAYER       = (255, 220, 100)
COLOR_TEXT         = (255, 255, 255)
COLOR_TILE_BORDER  = (160, 160, 160)   # cinza suave entre tiles

# ── player (farm) home position in tiles ─────────────────────────────────────
PLAYER_HOME_COL = 440
PLAYER_HOME_ROW =  35
