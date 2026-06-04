import pygame
from settings import TILE_SIZE, MAP_COLS, MAP_ROWS, COLOR_PLAYER, PLAYER_HOME_COL, PLAYER_HOME_ROW

SPEED          = 3
_SIZE          = TILE_SIZE // 2   # 0.5 × 0.5 tiles
_OUTLINE_COLOR = (180, 140, 40)


class Player:
    def __init__(self):
        self._home_x = PLAYER_HOME_COL * TILE_SIZE
        self._home_y = PLAYER_HOME_ROW * TILE_SIZE
        self.x = self._home_x
        self.y = self._home_y

    def return_home(self) -> None:
        self.x = self._home_x
        self.y = self._home_y

    def handle_input(self, keys) -> None:
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += SPEED

        self.x = max(0, min(self.x, (MAP_COLS - 1) * TILE_SIZE))
        self.y = max(0, min(self.y, (MAP_ROWS - 1) * TILE_SIZE))

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
        sx   = self.x - camera_x
        sy   = self.y - camera_y
        rect = (sx, sy, _SIZE, _SIZE)
        pygame.draw.rect(surface, COLOR_PLAYER, rect)
        pygame.draw.rect(surface, _OUTLINE_COLOR, rect, 2)
