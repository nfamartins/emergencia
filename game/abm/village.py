import pygame
from mesa import Model
from abm.villager import Villager
from settings import MAP_ROWS, MAP_COLS, TILE_SIZE

_VILLAGE_HALF = 3   # vila ocupa ±3 tiles a partir do centro do mapa


class VillageModel(Model):
    def __init__(self, num_agents: int = 25):
        super().__init__()
        mid_r = MAP_ROWS // 2
        mid_c = MAP_COLS // 2
        self.village_tiles = [
            (r, c)
            for r in range(mid_r - _VILLAGE_HALF, mid_r + _VILLAGE_HALF + 1)
            for c in range(mid_c - _VILLAGE_HALF, mid_c + _VILLAGE_HALF + 1)
        ]
        self.village_tiles_set = set(self.village_tiles)
        for _ in range(num_agents):
            row, col = self.random.choice(self.village_tiles)
            Villager(self, row, col)

    def step(self) -> None:
        agent_list = list(self.agents)
        self.random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()
        for agent in list(self.agents):
            if not agent.alive or agent.migrated:
                agent.remove()

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
        half = TILE_SIZE // 2
        for agent in self.agents:
            x = agent.col * TILE_SIZE - camera_x + half
            y = agent.row * TILE_SIZE - camera_y + half
            pygame.draw.circle(surface, agent.color, (x, y), 5)
            pygame.draw.circle(surface, (0, 0, 0),   (x, y), 5, 1)
