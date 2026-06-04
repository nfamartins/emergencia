from settings import DAYS_PER_MONTH, MONTHS_PER_YEAR, SEASONS

MONTH_NAMES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


class TimeSystem:
    def __init__(self):
        self.day = 1
        self.month = 0
        self.year = 1
        self._elapsed = 0.0

    def update(self, dt: float, seconds_per_day: float) -> int:
        self._elapsed += dt
        days_passed = 0
        while self._elapsed >= seconds_per_day:
            self._elapsed -= seconds_per_day
            self._advance_day()
            days_passed += 1
        return days_passed

    def _advance_day(self):
        self.day += 1
        if self.day > DAYS_PER_MONTH:
            self.day = 1
            self.month += 1
        if self.month >= MONTHS_PER_YEAR:
            self.month = 0
            self.year += 1

    @property
    def season(self) -> str:
        for name, data in SEASONS.items():
            if self.month in data["months"]:
                return name
        return "Verão"

    @property
    def season_color(self) -> tuple:
        return SEASONS[self.season]["color"]

    def __str__(self) -> str:
        return f"Dia {self.day} de {MONTH_NAMES[self.month]} · Ano {self.year} · {self.season}"
