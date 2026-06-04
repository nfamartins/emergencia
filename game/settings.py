SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "Emergência"

TILE_SIZE = 32
MAP_COLS = 40
MAP_ROWS = 30

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

COLOR_GRASS       = ( 86, 130,  46)
COLOR_DIRT        = (139,  90,  43)
COLOR_WATER       = ( 64, 164, 223)
COLOR_VILLAGE     = (180, 160, 120)
COLOR_PLAYER      = (255, 220, 100)
COLOR_TEXT        = (255, 255, 255)
COLOR_TILE_BORDER = (160, 160, 160)  # cinza suave entre tiles
