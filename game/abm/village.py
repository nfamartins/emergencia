import pygame
from mesa import Model
from abm.villager import Villager, Role
from world.layout import Lot
from world import distributions
from settings import TILE_SIZE

_AGENT_RADIUS = 4   # px — 0.5 tile at TILE_SIZE=32 → 16px diameter, dot = 4px radius


class VillageModel(Model):
    def __init__(self, lots: list[Lot], num_families: int = 30):
        super().__init__()

        self.lot_by_id: dict[int, Lot] = {l.id: l for l in lots}

        res_lots = [l for l in lots if l.lot_type == "residential"]
        selected = self.random.sample(res_lots, min(num_families, len(res_lots)))

        for family_id, lot in enumerate(selected):
            self._spawn_family(family_id, lot)

    # ── family generation ─────────────────────────────────────────────────────

    def _spawn_family(self, family_id: int, lot: Lot) -> None:
        ftype = distributions.family_type(self.random)
        r, c  = lot.center_row, lot.center_col

        if ftype == "single":
            self._make_adult(r, c, family_id, lot.id)

        elif ftype == "couple":
            a, b = self._make_couple(r, c, family_id, lot.id)

        elif ftype == "couple_children":
            a, b = self._make_couple(r, c, family_id, lot.id)
            youngest_parent = min(a.age, b.age)
            n = distributions.num_children(ftype, self.random)
            for _ in range(n):
                child = self._make_child(r, c, family_id, lot.id, youngest_parent)
                child.parent_ids = [a.unique_id, b.unique_id]
                a.child_ids.append(child.unique_id)
                b.child_ids.append(child.unique_id)

        elif ftype == "single_parent":
            parent = self._make_adult(r, c, family_id, lot.id)
            n = distributions.num_children(ftype, self.random)
            for _ in range(n):
                child = self._make_child(r, c, family_id, lot.id, parent.age)
                child.parent_ids = [parent.unique_id]
                parent.child_ids.append(child.unique_id)

    def _make_adult(self, r: int, c: int, family_id: int, lot_id: int) -> Villager:
        return Villager(self, r, c,
                        age=distributions.adult_age(self.random),
                        gender=distributions.random_gender(self.random),
                        role=Role.ADULT,
                        family_id=family_id, lot_id=lot_id)

    def _make_couple(self, r: int, c: int,
                     family_id: int, lot_id: int) -> tuple[Villager, Villager]:
        age_a = distributions.adult_age(self.random)
        age_b = distributions.partner_age(age_a, self.random)
        a = Villager(self, r, c, age=age_a,
                     gender=distributions.random_gender(self.random),
                     role=Role.ADULT, family_id=family_id, lot_id=lot_id)
        b = Villager(self, r, c, age=age_b,
                     gender=distributions.random_gender(self.random),
                     role=Role.ADULT, family_id=family_id, lot_id=lot_id)
        a.partner_id = b.unique_id
        b.partner_id = a.unique_id
        return a, b

    def _make_child(self, r: int, c: int, family_id: int,
                    lot_id: int, parent_age: int) -> Villager:
        return Villager(self, r, c,
                        age=distributions.child_age(parent_age, self.random),
                        gender=distributions.random_gender(self.random),
                        role=Role.CHILD,
                        family_id=family_id, lot_id=lot_id)

    # ── ABM step (called once per in-game day) ────────────────────────────────

    def step(self) -> None:
        agent_list = list(self.agents)
        self.random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()
        for agent in list(self.agents):
            if not agent.alive or agent.migrated:
                agent.remove()

    # ── rendering ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
        half = TILE_SIZE // 2
        for agent in self.agents:
            x = agent.col * TILE_SIZE - camera_x + half
            y = agent.row * TILE_SIZE - camera_y + half
            pygame.draw.circle(surface, agent.color, (x, y), _AGENT_RADIUS)
            pygame.draw.circle(surface, (0, 0, 0),   (x, y), _AGENT_RADIUS, 1)
