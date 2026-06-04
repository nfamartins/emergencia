import os
import sys
from enum import Enum, auto
from pathlib import Path

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

sys.path.insert(0, str(Path(__file__).parent))

import pygame
from settings import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
                      SECONDS_PER_HOUR, MAP_COLS, MAP_ROWS, TILE_SIZE,
                      COLOR_TILE_BORDER)
from world.map import GameMap
from world.time_system import TimeSystem
from entities.player import Player
from ui.hud import HUD
from save import save_game, load_game


class GameState(Enum):
    PLAYING       = auto()
    DAY_END_PROMPT = auto()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_map    = GameMap()
    time_system = TimeSystem()
    player      = Player()
    hud         = HUD()
    state       = GameState.PLAYING

    load_game(time_system, player)

    map_pixel_w = MAP_COLS * TILE_SIZE
    map_pixel_h = MAP_ROWS * TILE_SIZE

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN and state == GameState.DAY_END_PROMPT:
                    save_game(time_system, player)
                    time_system.advance_to_next_day()
                    player.return_home()
                    state = GameState.PLAYING

        if state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            player.handle_input(keys)
            time_system.update(dt, SECONDS_PER_HOUR)
            if time_system.is_day_end_hour:
                state = GameState.DAY_END_PROMPT

        camera_x = max(0, min(player.x - SCREEN_WIDTH  // 2, map_pixel_w - SCREEN_WIDTH))
        camera_y = max(0, min(player.y - SCREEN_HEIGHT // 2, map_pixel_h - SCREEN_HEIGHT))

        screen.fill(COLOR_TILE_BORDER)
        game_map.draw(screen, camera_x, camera_y, time_system.season_color)
        player.draw(screen, camera_x, camera_y)
        hud.draw(screen, time_system)

        if state == GameState.DAY_END_PROMPT:
            hud.draw_day_end_prompt(screen, time_system)

        pygame.display.flip()


if __name__ == "__main__":
    main()
