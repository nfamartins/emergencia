from mesa import Agent


class Villager(Agent):
    def __init__(self, model, row: int, col: int):
        super().__init__(model)
        self.row          = row
        self.col          = col
        self.hunger       = model.random.randint(20, 50)   # 0-100; quanto maior, mais faminto
        self.income       = model.random.randint(30, 70)   # 0-100
        self.health       = model.random.randint(50, 90)   # 0-100
        self.satisfaction = self._compute_satisfaction()
        self.alive        = True
        self.migrated     = False

    def step(self) -> None:
        self._wander()
        self._consume()
        self._work()
        self._update_health()
        self.satisfaction = self._compute_satisfaction()
        self._check_survival()

    def _wander(self) -> None:
        dr, dc = self.random.choice([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)])
        candidate = (self.row + dr, self.col + dc)
        if candidate in self.model.village_tiles_set:
            self.row, self.col = candidate

    def _consume(self) -> None:
        self.hunger = min(100, self.hunger + self.random.randint(8, 18))
        if self.income >= 10 and self.hunger > 30:
            self.income = max(0, self.income - self.random.randint(5, 15))
            self.hunger = max(0, self.hunger - self.random.randint(25, 45))

    def _work(self) -> None:
        self.income = min(100, self.income + self.random.randint(8, 22))

    def _update_health(self) -> None:
        if self.hunger > 70:
            self.health = max(0, self.health - self.random.randint(3, 8))
        else:
            self.health = min(100, self.health + self.random.randint(0, 2))

    def _compute_satisfaction(self) -> int:
        return int(0.4 * self.health + 0.35 * (100 - self.hunger) + 0.25 * self.income)

    def _check_survival(self) -> None:
        if self.health <= 0:
            self.alive = False
        elif self.income <= 0 and self.hunger > 85:
            self.migrated = True

    @property
    def color(self) -> tuple:
        t = max(0.0, min(1.0, self.satisfaction / 100))
        return (int(220 * (1 - t)), int(200 * t), 30)
