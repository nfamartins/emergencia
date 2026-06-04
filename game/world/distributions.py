"""
Demographic distributions for the village population.
All functions accept an optional `rng` (random.Random instance) for
reproducibility. When omitted, the module-level random is used.

Sources / approximations:
  - Family types: IBGE PNAD 2022 household composition
  - Age distribution: normal(µ=40, σ=15) clipped [25, 85]
  - Partner age: normal(base_age, σ=5) clipped [25, 85]
  - Children: uniform [0, min(24, parent_age-19)]
"""
import random as _random
from typing import Optional


# ── adult age ─────────────────────────────────────────────────────────────────

def adult_age(rng: Optional[_random.Random] = None) -> int:
    r = rng or _random
    while True:
        v = r.gauss(40, 15)
        if 25 <= v <= 85:
            return int(v)


def partner_age(base_age: int, rng: Optional[_random.Random] = None) -> int:
    r = rng or _random
    while True:
        v = r.gauss(base_age, 5)
        if 25 <= v <= 85:
            return int(v)


# ── child age ─────────────────────────────────────────────────────────────────

def child_age(youngest_parent_age: int,
              rng: Optional[_random.Random] = None) -> int:
    """Uniform [0, min(24, parent_age − 19)]. Returns 0 if parent too young."""
    r = rng or _random
    max_age = min(24, youngest_parent_age - 19)
    if max_age <= 0:
        return 0
    return r.randint(0, max_age)


# ── gender ────────────────────────────────────────────────────────────────────

def random_gender(rng: Optional[_random.Random] = None) -> str:
    r = rng or _random
    return r.choice(["F", "M"])


# ── family type ───────────────────────────────────────────────────────────────
# Approximate IBGE PNAD 2022 proportions for municipality-level Brazil.

_FAMILY_TYPES = [
    ("single",          0.14),   # 1 adult
    ("couple",          0.20),   # 2 adults, no children
    ("couple_children", 0.50),   # 2 adults + 1–3 children
    ("single_parent",   0.16),   # 1 adult + 1–4 children
]

def family_type(rng: Optional[_random.Random] = None) -> str:
    r = rng or _random
    roll, cumulative = r.random(), 0.0
    for name, prob in _FAMILY_TYPES:
        cumulative += prob
        if roll < cumulative:
            return name
    return _FAMILY_TYPES[-1][0]


def num_children(ftype: str, rng: Optional[_random.Random] = None) -> int:
    r = rng or _random
    if ftype == "couple_children":
        return r.randint(1, 3)
    if ftype == "single_parent":
        return r.randint(1, 4)
    return 0
