import pygame
from settings import TILE_SIZE, MAP_COLS, MAP_ROWS, COLOR_PLAYER

SPEED = 3
_OUTLINE_COLOR = (180, 140, 40)


class Player:
    def __init__(self):
        self.x = (MAP_COLS // 2) * TILE_SIZE
        self.y = (MAP_ROWS // 2 + 6) * TILE_SIZE
        self.size = TILE_SIZE - 4

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += SPEED
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= SPEED
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += SPEED

        self.x = max(0, min(self.x, (MAP_COLS - 1) * TILE_SIZE))
        self.y = max(0, min(self.y, (MAP_ROWS - 1) * TILE_SIZE))

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        sx = self.x - camera_x
        sy = self.y - camera_y
        rect = (sx, sy, self.size, self.size)
        pygame.draw.rect(surface, COLOR_PLAYER, rect)
        pygame.draw.rect(surface, _OUTLINE_COLOR, rect, 2)
