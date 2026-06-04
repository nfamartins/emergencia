from settings import (DAYS_PER_MONTH, MONTHS_PER_YEAR, SEASONS,
                      HOURS_PER_DAY, DAY_START_HOUR, DAY_END_HOUR,
                      SECONDS_PER_HOUR)

MONTH_NAMES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
               "Jul", "Ago", "Set", "Out", "Nov", "Dez"]


class TimeSystem:
    def __init__(self):
        self.day   = 1
        self.month = 0
        self.year  = 1
        self.hour  = DAY_START_HOUR
        self._elapsed = 0.0

    def update(self, dt: float, seconds_per_hour: float) -> int:
        self._elapsed += dt
        hours_passed = 0
        while self._elapsed >= seconds_per_hour:
            self._elapsed -= seconds_per_hour
            self.hour += 1
            hours_passed += 1
            if self.hour >= HOURS_PER_DAY:
                self.hour = 0
                self._advance_day()
        return hours_passed

    def advance_to_next_day(self) -> None:
        self._advance_day()
        self.hour     = DAY_START_HOUR
        self._elapsed = 0.0

    def _advance_day(self) -> None:
        self.day += 1
        if self.day > DAYS_PER_MONTH:
            self.day = 1
            self.month += 1
        if self.month >= MONTHS_PER_YEAR:
            self.month = 0
            self.year += 1

    @property
    def is_day_end_hour(self) -> bool:
        return self.hour >= DAY_END_HOUR

    @property
    def season(self) -> str:
        for name, data in SEASONS.items():
            if self.month in data["months"]:
                return name
        return "Verão"

    @property
    def season_color(self) -> tuple:
        return SEASONS[self.season]["color"]

    @property
    def minute(self) -> int:
        return int(self._elapsed / SECONDS_PER_HOUR * 60)

    def __str__(self) -> str:
        return (f"Dia {self.day} de {MONTH_NAMES[self.month]}"
                f" · Ano {self.year} · {self.season} · {self.hour:02d}:{self.minute:02d}")

    def to_dict(self) -> dict:
        return {"day": self.day, "month": self.month,
                "year": self.year, "hour": self.hour}

    def from_dict(self, data: dict) -> None:
        self.day      = data["day"]
        self.month    = data["month"]
        self.year     = data["year"]
        self.hour     = data.get("hour", DAY_START_HOUR)
        self._elapsed = 0.0
