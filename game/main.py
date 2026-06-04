import sys
import pygame

sys.path.insert(0, str(__file__).replace("main.py", ""))

from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, SECONDS_PER_DAY
from world.map import GameMap
from world.time_system import TimeSystem
from entities.player import Player
from ui.hud import HUD


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game_map    = GameMap()
    time_system = TimeSystem()
    player      = Player()
    hud         = HUD()

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
                if event.key == pygame.K_TAB:
                    print("[TODO] Modo Sistema — Fase 4")

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        time_system.update(dt, SECONDS_PER_DAY)

        camera_x = player.x - SCREEN_WIDTH  // 2
        camera_y = player.y - SCREEN_HEIGHT // 2

        screen.fill((20, 20, 20))
        game_map.draw(screen, camera_x, camera_y, time_system.season_color)
        player.draw(screen, camera_x, camera_y)
        hud.draw(screen, time_system)

        pygame.display.flip()


if __name__ == "__main__":
    main()
