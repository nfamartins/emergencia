# 🛠️ Instruções de Implementação — Fase 2 (Correções)

> Estas instruções corrigem e expandem o ABM existente.
> Leia o código atual de cada arquivo antes de modificar.
> Siga os princípios do CLAUDE.md: inglês no código, modularidade, funções pequenas.

---

## Arquivos a modificar

```
game/
├── settings.py                   ← novas constantes
├── world/
│   ├── distributions.py          ← nomes, sobrenomes, patrimônio, bolsa família
│   └── layout.py                 ← tipo Lot ampliado, atribuição de estabelecimentos
├── abm/
│   ├── village.py                ← geração de estabelecimentos, ocupações, horário
│   └── villager.py               ← cash, hunger, mobilidade, interação
└── ui/
    └── hud.py                    ← painel de conhecidos
```

Novo arquivo:
```
game/abm/establishment.py         ← classe Establishment
```

---

## 1. settings.py — novas constantes

Adicionar ao final do arquivo:

```python
# ── economia ──────────────────────────────────────────────────────────────────
MIN_WAGE_MONTHLY      = 1500.0    # R$ — salário mínimo mensal
MIN_WAGE_DAILY        = MIN_WAGE_MONTHLY / 30
BOLSA_FAMILIA_BENEFIT = 500.0     # R$ por mês
BOLSA_FAMILIA_THRESHOLD = MIN_WAGE_MONTHLY * 0.5  # renda per capita < R$750

FOOD_PER_PERSON_WEEK  = 7.0       # unidades de food por pessoa por semana
FOOD_RESTOCK_DAILY    = 50.0      # unidades que chegam por compra externa (mock)
FOOD_PRICE            = 10.0      # R$ por unidade de food

# ── horário ───────────────────────────────────────────────────────────────────
WORK_START_HOUR       = 9
WORK_END_HOUR         = 18
BAR_LUNCH_START       = 12
BAR_LUNCH_END         = 14
BAR_NIGHT_START       = 19
BAR_NIGHT_END         = 22
WORK_SKIP_PROB        = 0.02      # probabilidade de faltar ao trabalho

# ── mobilidade (pesos fora do trabalho — extensível com dados IBGE) ───────────
# Cada lista: [casa, praça, bar]  — normalizada internamente
MOBILITY_EMPLOYED_OFFHOURS  = [0.6, 0.25, 0.15]
MOBILITY_UNEMPLOYED_DAY     = [0.4, 0.35, 0.25]
MOBILITY_CHILD_OFFHOURS     = [0.7, 0.30, 0.00]
MOBILITY_BAR_LUNCH_PROB     = 0.15   # prob. de empregado ir ao bar no almoço
MOBILITY_BAR_NIGHT_PROB     = 0.25   # prob. de adulto ir ao bar à noite

# ── interação jogador ─────────────────────────────────────────────────────────
INTERACTION_RADIUS_TILES    = 1      # raio em tiles para clique de interação
```

---

## 2. world/distributions.py — nomes, sobrenomes, patrimônio

Adicionar ao final do arquivo (preservar tudo que já existe):

```python
# ── nomes brasileiros ─────────────────────────────────────────────────────────
# Fonte: nomes mais comuns no Brasil (IBGE)

_FIRST_NAMES_F = [
    "Ana", "Maria", "Francisca", "Antônia", "Adriana", "Juliana", "Márcia",
    "Fernanda", "Patrícia", "Aline", "Sandra", "Camila", "Amanda", "Bruna",
    "Larissa", "Letícia", "Natália", "Vanessa", "Claudia", "Luciana",
]

_FIRST_NAMES_M = [
    "José", "João", "Antônio", "Francisco", "Carlos", "Paulo", "Pedro",
    "Lucas", "Luiz", "Marcos", "Luis", "Gabriel", "Rafael", "Daniel",
    "Marcelo", "Bruno", "Eduardo", "Felipe", "Raimundo", "Rodrigo",
]

_SURNAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira",
    "Alves", "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins",
    "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira",
    "Barbosa", "Rocha", "Dias", "Nascimento", "Andrade", "Moreira",
    "Nunes", "Marques", "Machado", "Mendes", "Freitas",
]


def first_name(gender: str, rng: Optional[_random.Random] = None) -> str:
    r = rng or _random
    pool = _FIRST_NAMES_F if gender == "F" else _FIRST_NAMES_M
    return r.choice(pool)


def surname(rng: Optional[_random.Random] = None) -> str:
    r = rng or _random
    return r.choice(_SURNAMES)


# ── patrimônio familiar inicial ───────────────────────────────────────────────
# Distribuição log-normal calibrada para desigualdade brasileira (Gini ≈ 0.53).
# Parâmetros: mu e sigma da log-normal subjacente.
# Referência: IBGE POF 2017-2018 / World Inequality Database Brasil.
#
# Log-normal(mu=8.0, sigma=1.2) com mínimo R$500:
#   mediana ≈ R$2.980  |  média ≈ R$5.400  |  p90 ≈ R$13.000
#
# Donos de comércio: fator 2–3× aplicado sobre o sorteio base.

_WEALTH_MU     = 8.0    # log-normal mu
_WEALTH_SIGMA  = 1.2    # log-normal sigma  — aumentar → mais desigualdade
_WEALTH_MIN    = 500.0  # R$ — piso absoluto
_OWNER_WEALTH_FACTOR_MIN = 2.0
_OWNER_WEALTH_FACTOR_MAX = 3.0


def family_wealth(rng: Optional[_random.Random] = None) -> float:
    """Patrimônio inicial da família em R$. Log-normal, mínimo R$500."""
    r = rng or _random
    raw = r.lognormvariate(_WEALTH_MU, _WEALTH_SIGMA)
    return max(_WEALTH_MIN, round(raw, 2))


def owner_wealth(rng: Optional[_random.Random] = None) -> float:
    """Patrimônio inicial para donos de comércio (2–3× acima da média)."""
    r = rng or _random
    factor = r.uniform(_OWNER_WEALTH_FACTOR_MIN, _OWNER_WEALTH_FACTOR_MAX)
    return round(family_wealth(rng) * factor, 2)


# ── idade mínima de crianças ──────────────────────────────────────────────────
# Corrigido: mínimo 7 anos (crianças em idade escolar).

def child_age(youngest_parent_age: int,                    # substitui a função existente
              rng: Optional[_random.Random] = None) -> int:
    """Uniforme [7, min(17, parent_age − 19)]. Retorna 7 se pai muito jovem."""
    r = rng or _random
    max_age = min(17, youngest_parent_age - 19)
    if max_age < 7:
        return 7
    return r.randint(7, max_age)
```

> ⚠️ A função `child_age` acima **substitui** a existente. Remova a original.

---

## 3. game/abm/establishment.py — novo arquivo

Criar do zero:

```python
"""
Establishment — representa um terreno comercial ou institucional ocupado.
Cada instância é associada a um Lot do layout e carrega estoque, ocupações
e lógica de negócio mínima.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from abm.villager import Villager

# ── tipos de estabelecimento ──────────────────────────────────────────────────

ESTABLISHMENT_TYPES = {
    # name            : (label_pt,            is_commercial, max_owners, max_employees, has_food)
    "market"          : ("Mercado",            True,          1,          2,             True),
    "bar"             : ("Bar",                True,          1,          1,             False),
    "school"          : ("Escola",             False,         0,          3,             False),
    "health_post"     : ("Posto de Saúde",     False,         0,          3,             False),
    "pharmacy"        : ("Farmácia",           True,          1,          1,             False),
    "neighborhood_assoc": ("Assoc. de Bairro", False,         0,          2,             False),
    "salon"           : ("Salão",              True,          1,          1,             False),
    "empty"           : ("Vazio",              False,         0,          0,             False),
}


@dataclass
class Establishment:
    lot_id:    int
    est_type:  str                        # chave em ESTABLISHMENT_TYPES
    row:       int                        # tile row do centro do lote
    col:       int                        # tile col do centro do lote

    owner_id:      Optional[int]  = None  # unique_id do villager dono
    employee_ids:  list[int]      = field(default_factory=list)

    # estoque de food (só relevante para mercado por enquanto)
    food_stock:    float          = 0.0

    @property
    def label(self) -> str:
        return ESTABLISHMENT_TYPES[self.est_type][0]

    @property
    def is_commercial(self) -> bool:
        return ESTABLISHMENT_TYPES[self.est_type][1]

    @property
    def max_owners(self) -> int:
        return ESTABLISHMENT_TYPES[self.est_type][2]

    @property
    def max_employees(self) -> int:
        return ESTABLISHMENT_TYPES[self.est_type][3]

    @property
    def has_food(self) -> bool:
        return ESTABLISHMENT_TYPES[self.est_type][4]

    @property
    def total_workers(self) -> int:
        return (1 if self.owner_id is not None else 0) + len(self.employee_ids)

    def restock(self, amount: float) -> None:
        """Adiciona food ao estoque (compra externa mockada)."""
        if self.has_food:
            self.food_stock += amount

    def sell_food(self, requested: float, budget: float) -> tuple[float, float]:
        """
        Tenta vender `requested` unidades ao preço FOOD_PRICE.
        Respeita estoque disponível E orçamento do comprador.
        Retorna (units_sold, cost).
        """
        from settings import FOOD_PRICE
        max_affordable = budget / FOOD_PRICE
        available = min(self.food_stock, requested, max_affordable)
        if available <= 0:
            return 0.0, 0.0
        cost = round(available * FOOD_PRICE, 2)
        self.food_stock = max(0.0, self.food_stock - available)
        return available, cost
```

---

## 4. world/layout.py — atribuição de estabelecimentos aos lotes

Adicionar ao final do arquivo (após `generate_lots`):

```python
# ── atribuição de estabelecimentos ───────────────────────────────────────────

# Tipos disponíveis, em ordem de prioridade de atribuição.
# Os primeiros serão alocados nos lotes comerciais mais próximos da praça.
_ESTABLISHMENT_SEQUENCE = [
    "market",
    "bar",
    "school",
    "health_post",
    "pharmacy",
    "neighborhood_assoc",
    "salon",
    # restante dos lotes comerciais ficam "empty"
]


def _plaza_center() -> tuple[float, float]:
    """Centro da praça em tiles (row, col)."""
    pr, pc, ph, pw = plaza_bounds()
    return pr + ph / 2, pc + pw / 2


def assign_establishments(lots: list[Lot]) -> list[tuple[Lot, str]]:
    """
    Associa um tipo de estabelecimento a cada lote comercial.
    Lotes mais próximos da praça recebem os tipos prioritários.
    Retorna lista de (Lot, est_type) para todos os lotes comerciais.
    """
    com_lots = [l for l in lots if l.lot_type == "commercial"]
    pr, pc = _plaza_center()

    # ordena por distância ao centro da praça (menor = mais próximo)
    com_lots_sorted = sorted(
        com_lots,
        key=lambda l: (l.center_row - pr) ** 2 + (l.center_col - pc) ** 2
    )

    result = []
    for i, lot in enumerate(com_lots_sorted):
        est_type = _ESTABLISHMENT_SEQUENCE[i] if i < len(_ESTABLISHMENT_SEQUENCE) else "empty"
        result.append((lot, est_type))
    return result
```

---

## 5. abm/villager.py — refatoração completa

Substituir o arquivo inteiro pelo código abaixo:

```python
from __future__ import annotations
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING
from mesa import Agent

if TYPE_CHECKING:
    from abm.village import VillageModel

from settings import (
    WORK_START_HOUR, WORK_END_HOUR, WORK_SKIP_PROB,
    BAR_LUNCH_START, BAR_LUNCH_END, BAR_NIGHT_START, BAR_NIGHT_END,
    MOBILITY_EMPLOYED_OFFHOURS, MOBILITY_UNEMPLOYED_DAY,
    MOBILITY_CHILD_OFFHOURS, MOBILITY_BAR_LUNCH_PROB, MOBILITY_BAR_NIGHT_PROB,
    FOOD_PER_PERSON_WEEK,
)


class Role(Enum):
    ADULT = auto()
    CHILD = auto()


class EmploymentStatus(Enum):
    OWNER      = auto()
    EMPLOYEE   = auto()
    UNEMPLOYED = auto()


class Villager(Agent):
    def __init__(self, model: "VillageModel", row: int, col: int,
                 age: int, gender: str, role: Role,
                 family_id: int, lot_id: int,
                 first_name: str, family_name: str):
        super().__init__(model)

        # posição
        self.row = row
        self.col = col

        # identidade
        self.age         = age
        self.gender      = gender          # "F" | "M"
        self.role        = role
        self.first_name  = first_name
        self.family_name = family_name

        # vínculos familiares
        self.family_id:  int           = family_id
        self.lot_id:     int           = lot_id
        self.partner_id: Optional[int] = None
        self.parent_ids: list[int]     = []
        self.child_ids:  list[int]     = []

        # vínculo empregatício
        self.employment_status: EmploymentStatus = EmploymentStatus.UNEMPLOYED
        self.workplace_lot_id:  Optional[int]    = None  # lot_id do estabelecimento
        self.is_shopper:        bool             = False  # único comprador da família
        self.shop_day:          int              = 0      # dia da semana da compra (0–6)

        # finanças (em R$)
        self.cash:             float = 0.0   # dinheiro em mãos
        self.monthly_wage:     float = 0.0   # salário mensal (0 se desempregado/criança)

        # atributos de bem-estar (0–100)
        self.hunger:       int = model.random.randint(20, 50)
        self.health:       int = model.random.randint(50, 90)
        self.satisfaction: int = 0

        # estado
        self.alive:             bool = True
        self.migrated:          bool = False
        self.known_to_player:   bool = False
        self.day_met:           Optional[int] = None  # dia do jogo do primeiro encontro

        self.satisfaction = self._compute_satisfaction()

    # ── propriedades ──────────────────────────────────────────────────────────

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.family_name}"

    @property
    def family_size(self) -> int:
        """Tamanho da família (via model)."""
        return len([a for a in self.model.agents
                    if a.family_id == self.family_id])

    @property
    def is_working_hour(self) -> bool:
        h = self.model.hour
        return WORK_START_HOUR <= h < WORK_END_HOUR

    @property
    def is_bar_lunch_hour(self) -> bool:
        h = self.model.hour
        return BAR_LUNCH_START <= h < BAR_LUNCH_END

    @property
    def is_bar_night_hour(self) -> bool:
        h = self.model.hour
        return BAR_NIGHT_START <= h < BAR_NIGHT_END

    # ── step horário (chamado a cada hora) ────────────────────────────────────

    def step(self) -> None:
        self._move()
        if self.model.hour == WORK_START_HOUR:
            self._receive_daily_wage()
        self._update_hunger()
        self._update_health()
        self.satisfaction = self._compute_satisfaction()
        self._check_survival()

    # ── movimento ─────────────────────────────────────────────────────────────

    def _move(self) -> None:
        target = self._choose_destination()
        if target is not None:
            self.row, self.col = target

    def _choose_destination(self) -> Optional[tuple[int, int]]:
        m = self.model

        if self.role == Role.CHILD:
            if self.is_working_hour:
                # vai para a escola
                school = m.get_establishment("school")
                if school:
                    return school.row, school.col
            else:
                dest = self.random.choices(
                    ["home", "plaza"], weights=MOBILITY_CHILD_OFFHOURS[:2]
                )[0]
                return self._tile_for(dest)

        # adulto
        employed = self.employment_status in (
            EmploymentStatus.OWNER, EmploymentStatus.EMPLOYEE
        )

        if employed and self.is_working_hour:
            if self.random.random() < WORK_SKIP_PROB:
                return self._tile_for("home")
            # intervalo de almoço → chance de ir ao bar
            if self.is_bar_lunch_hour and self.random.random() < MOBILITY_BAR_LUNCH_PROB:
                return self._tile_for("bar")
            wp = m.lot_by_id.get(self.workplace_lot_id)
            if wp:
                return wp.center_row, wp.center_col

        if self.is_bar_night_hour and self.random.random() < MOBILITY_BAR_NIGHT_PROB:
            return self._tile_for("bar")

        weights = (MOBILITY_EMPLOYED_OFFHOURS if employed
                   else MOBILITY_UNEMPLOYED_DAY)
        dest = self.random.choices(["home", "plaza", "bar"], weights=weights)[0]
        return self._tile_for(dest)

    def _tile_for(self, place: str) -> Optional[tuple[int, int]]:
        m = self.model
        if place == "home":
            lot = m.lot_by_id.get(self.lot_id)
            return (lot.center_row, lot.center_col) if lot else None
        est = m.get_establishment(place)  # "plaza", "bar", etc.
        if est:
            return est.row, est.col
        # fallback: praça
        plaza = m.plaza_tile
        return plaza

    # ── economia ──────────────────────────────────────────────────────────────

    def _receive_daily_wage(self) -> None:
        """Acumula fração diária do salário (pago diariamente para simplificar)."""
        self.cash += self.monthly_wage / 30

    def try_weekly_shopping(self, day_of_week: int) -> None:
        """
        Chamado pelo VillageModel no step diário (hora 10h).
        Compra food se: é o dia certo, tem dinheiro, e há estoque.
        """
        if not self.is_shopper:
            return
        if day_of_week != self.shop_day:
            return

        needed = self.family_size * FOOD_PER_PERSON_WEEK
        market = self.model.get_establishment("market")
        if not market:
            return

        units, cost = market.sell_food(needed, self.cash)
        if units > 0:
            self.cash = max(0.0, self.cash - cost)
            self._distribute_food(units)

    def _distribute_food(self, units: float) -> None:
        """Reduz hunger de todos da família proporcionalmente ao food comprado."""
        family = [a for a in self.model.agents if a.family_id == self.family_id]
        if not family:
            return
        reduction_per_person = min(40, int((units / len(family)) * 10))
        for member in family:
            member.hunger = max(0, member.hunger - reduction_per_person)

    # ── bem-estar ─────────────────────────────────────────────────────────────

    def _update_hunger(self) -> None:
        """Fome aumenta ~3 pontos por hora (≈72/dia), capped em 100."""
        self.hunger = min(100, self.hunger + 3)

    def _update_health(self) -> None:
        if self.hunger > 70:
            self.health = max(0, self.health - 1)
        else:
            self.health = min(100, self.health + 1)

    def _compute_satisfaction(self) -> int:
        cash_score = min(100, int(self.cash / 15))  # R$1500 → 100
        return int(0.4 * self.health + 0.35 * (100 - self.hunger) + 0.25 * cash_score)

    def _check_survival(self) -> None:
        if self.health <= 0:
            self.alive = False
        elif self.cash <= 0 and self.hunger > 85:
            self.migrated = True

    # ── visual ────────────────────────────────────────────────────────────────

    @property
    def color(self) -> tuple:
        t = max(0.0, min(1.0, self.satisfaction / 100))
        return (int(220 * (1 - t)), int(200 * t), 30)

    def __repr__(self) -> str:
        return (f"Villager({self.full_name}, age={self.age}, "
                f"{self.employment_status.name}, family={self.family_id})")
```

---

## 6. abm/village.py — refatoração completa

Substituir o arquivo inteiro:

```python
from __future__ import annotations
import pygame
from mesa import Model
from abm.villager import Villager, Role, EmploymentStatus
from abm.establishment import Establishment, ESTABLISHMENT_TYPES
from world.layout import Lot, assign_establishments
from world import distributions
from settings import (
    TILE_SIZE, MIN_WAGE_MONTHLY, FOOD_RESTOCK_DAILY,
    BOLSA_FAMILIA_BENEFIT, BOLSA_FAMILIA_THRESHOLD,
)

_AGENT_RADIUS = 4


class Family:
    """Agrega dados financeiros e sociais de uma família."""
    def __init__(self, family_id: int, surname: str, wealth: float):
        self.family_id:      int   = family_id
        self.surname:        str   = surname
        self.wealth:         float = wealth   # patrimônio inicial em R$
        self.bolsa_familia:  bool  = False


class VillageModel(Model):
    def __init__(self, lots: list[Lot], num_families: int = 30):
        super().__init__()

        self.hour: int = 0   # hora atual do dia (0–23)

        # lotes
        self.lot_by_id: dict[int, Lot] = {l.id: l for l in lots}

        # estabelecimentos
        self.establishments: list[Establishment] = self._build_establishments(lots)
        self._est_by_type: dict[str, Establishment] = {
            e.est_type: e for e in self.establishments if e.est_type != "empty"
        }

        # praça (tile de referência para mobilidade)
        self.plaza_tile: tuple[int, int] = self._find_plaza_tile(lots)

        # famílias e agentes
        self.families: dict[int, Family] = {}
        res_lots = [l for l in lots if l.lot_type == "residential"]
        selected = self.random.sample(res_lots, min(num_families, len(res_lots)))
        for family_id, lot in enumerate(selected):
            self._spawn_family(family_id, lot)

        # atribui ocupações após gerar todos os agentes
        self._assign_occupations()

        # distribui cash inicial a partir do patrimônio familiar
        self._distribute_initial_cash()

    # ── setup ─────────────────────────────────────────────────────────────────

    def _build_establishments(self, lots: list[Lot]) -> list[Establishment]:
        assignments = assign_establishments(lots)
        result = []
        for lot, est_type in assignments:
            est = Establishment(
                lot_id=lot.id,
                est_type=est_type,
                row=lot.center_row,
                col=lot.center_col,
            )
            if est.has_food:
                est.food_stock = FOOD_RESTOCK_DAILY * 3   # estoque inicial
            result.append(est)
        return result

    def _find_plaza_tile(self, lots: list[Lot]) -> tuple[int, int]:
        from world.layout import plaza_bounds
        pr, pc, ph, pw = plaza_bounds()
        return pr + ph // 2, pc + pw // 2

    def _spawn_family(self, family_id: int, lot: Lot) -> None:
        surname   = distributions.surname(self.random)
        is_owner  = False   # definido depois em _assign_occupations
        wealth    = distributions.family_wealth(self.random)
        self.families[family_id] = Family(family_id, surname, wealth)

        ftype = distributions.family_type(self.random)
        r, c  = lot.center_row, lot.center_col

        if ftype == "single":
            self._make_adult(r, c, family_id, lot.id, surname)

        elif ftype == "couple":
            a, b = self._make_couple(r, c, family_id, lot.id, surname)

        elif ftype == "couple_children":
            a, b = self._make_couple(r, c, family_id, lot.id, surname)
            n = distributions.num_children(ftype, self.random)
            youngest_parent = min(a.age, b.age)
            for _ in range(n):
                child = self._make_child(r, c, family_id, lot.id, youngest_parent, surname)
                child.parent_ids = [a.unique_id, b.unique_id]
                a.child_ids.append(child.unique_id)
                b.child_ids.append(child.unique_id)

        elif ftype == "single_parent":
            parent = self._make_adult(r, c, family_id, lot.id, surname)
            n = distributions.num_children(ftype, self.random)
            for _ in range(n):
                child = self._make_child(r, c, family_id, lot.id, parent.age, surname)
                child.parent_ids = [parent.unique_id]
                parent.child_ids.append(child.unique_id)

        # designa comprador da família (primeiro adulto encontrado)
        adults = [a for a in self.agents if a.family_id == family_id
                  and a.role == Role.ADULT]
        if adults:
            shopper = self.random.choice(adults)
            shopper.is_shopper = True
            shopper.shop_day   = self.random.randint(0, 6)

    def _make_adult(self, r, c, family_id, lot_id, surname) -> Villager:
        gender = distributions.random_gender(self.random)
        return Villager(self, r, c,
                        age=distributions.adult_age(self.random),
                        gender=gender, role=Role.ADULT,
                        family_id=family_id, lot_id=lot_id,
                        first_name=distributions.first_name(gender, self.random),
                        family_name=surname)

    def _make_couple(self, r, c, family_id, lot_id, surname):
        age_a = distributions.adult_age(self.random)
        age_b = distributions.partner_age(age_a, self.random)
        g_a   = distributions.random_gender(self.random)
        g_b   = "M" if g_a == "F" else "F"
        a = Villager(self, r, c, age=age_a, gender=g_a, role=Role.ADULT,
                     family_id=family_id, lot_id=lot_id,
                     first_name=distributions.first_name(g_a, self.random),
                     family_name=surname)
        b = Villager(self, r, c, age=age_b, gender=g_b, role=Role.ADULT,
                     family_id=family_id, lot_id=lot_id,
                     first_name=distributions.first_name(g_b, self.random),
                     family_name=surname)
        a.partner_id = b.unique_id
        b.partner_id = a.unique_id
        return a, b

    def _make_child(self, r, c, family_id, lot_id, parent_age, surname) -> Villager:
        gender = distributions.random_gender(self.random)
        return Villager(self, r, c,
                        age=distributions.child_age(parent_age, self.random),
                        gender=gender, role=Role.CHILD,
                        family_id=family_id, lot_id=lot_id,
                        first_name=distributions.first_name(gender, self.random),
                        family_name=surname)

    def _assign_occupations(self) -> None:
        """Atribui donos e funcionários a cada estabelecimento."""
        adults = [a for a in self.agents if a.role == Role.ADULT]
        self.random.shuffle(adults)
        pool = list(adults)

        for est in self.establishments:
            if est.est_type == "empty":
                continue

            # donos (apenas comércios)
            if est.max_owners > 0 and pool:
                owner = pool.pop(0)
                owner.employment_status = EmploymentStatus.OWNER
                owner.workplace_lot_id  = est.lot_id
                owner.monthly_wage      = 0.0  # renda via mock de vendas (Fase 3)
                est.owner_id = owner.unique_id
                # patrimônio do dono é maior
                self.families[owner.family_id].wealth = distributions.owner_wealth(self.random)

            # funcionários
            n_emp = min(est.max_employees, len(pool))
            for _ in range(n_emp):
                if not pool:
                    break
                emp = pool.pop(0)
                emp.employment_status = EmploymentStatus.EMPLOYEE
                emp.workplace_lot_id  = est.lot_id
                emp.monthly_wage      = MIN_WAGE_MONTHLY
                est.employee_ids.append(emp.unique_id)

    def _distribute_initial_cash(self) -> None:
        """Distribui cash inicial aos adultos com base no patrimônio familiar."""
        for agent in self.agents:
            if agent.role == Role.ADULT:
                fam = self.families[agent.family_id]
                adults_in_fam = sum(1 for a in self.agents
                                    if a.family_id == agent.family_id
                                    and a.role == Role.ADULT)
                agent.cash = round(fam.wealth / max(adults_in_fam, 1), 2)

    # ── step (chamado a cada hora pelo time_system) ────────────────────────────

    def step(self) -> None:
        # reabastece mercado uma vez por dia (meia-noite)
        if self.hour == 0:
            for est in self.establishments:
                est.restock(FOOD_RESTOCK_DAILY)
            self._check_bolsa_familia()

        agent_list = list(self.agents)
        self.random.shuffle(agent_list)

        day_of_week = self._current_day_of_week()

        for agent in agent_list:
            agent.step()
            # compra semanal: processa às 10h
            if self.hour == 10:
                agent.try_weekly_shopping(day_of_week)

        # remove agentes mortos/migrados
        for agent in list(self.agents):
            if not agent.alive or agent.migrated:
                agent.remove()

    def _check_bolsa_familia(self) -> None:
        """Verifica e aplica Bolsa Família uma vez por mês (dia 1)."""
        # Será chamado pelo time_system apenas no dia 1 de cada mês
        for fam in self.families.values():
            adults = [a for a in self.agents
                      if a.family_id == fam.family_id and a.role == Role.ADULT]
            if not adults:
                continue
            total_income = sum(a.monthly_wage for a in adults)
            family_size  = sum(1 for a in self.agents if a.family_id == fam.family_id)
            per_capita   = total_income / max(family_size, 1)

            if per_capita < BOLSA_FAMILIA_THRESHOLD:
                fam.bolsa_familia = True
                # distribui entre adultos
                share = BOLSA_FAMILIA_BENEFIT / max(len(adults), 1)
                for a in adults:
                    a.cash += share
            else:
                fam.bolsa_familia = False

    def _current_day_of_week(self) -> int:
        """0=seg … 6=dom. Derivado do time_system via model (injetado em main)."""
        return getattr(self, "_day_of_week", 0)

    # ── queries ───────────────────────────────────────────────────────────────

    def get_establishment(self, est_type: str) -> Establishment | None:
        return self._est_by_type.get(est_type)

    def villagers_at(self, row: int, col: int) -> list[Villager]:
        return [a for a in self.agents if a.row == row and a.col == col]

    def known_villagers(self) -> list[Villager]:
        return [a for a in self.agents if a.known_to_player]

    # ── rendering ─────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int) -> None:
        font = pygame.font.SysFont("monospace", 9)

        # labels dos estabelecimentos
        for est in self.establishments:
            if est.est_type == "empty":
                continue
            x = est.col * TILE_SIZE - camera_x
            y = est.row * TILE_SIZE - camera_y - 12
            label = font.render(est.label, True, (255, 255, 180))
            surface.blit(label, (x, y))

        # agentes
        half = TILE_SIZE // 2
        for agent in self.agents:
            x = agent.col * TILE_SIZE - camera_x + half
            y = agent.row * TILE_SIZE - camera_y + half
            pygame.draw.circle(surface, agent.color, (x, y), _AGENT_RADIUS)
            pygame.draw.circle(surface, (0, 0, 0), (x, y), _AGENT_RADIUS, 1)
            # anel branco se conhecido pelo jogador
            if agent.known_to_player:
                pygame.draw.circle(surface, (255, 255, 255), (x, y), _AGENT_RADIUS + 2, 1)
```

---

## 7. world/time_system.py — adicionar hora e callbacks

Modificar a classe existente:

```python
# Adicionar atributo no __init__:
self.hour: int = 0

# Modificar _advance_day para _advance_hour:
def _advance_hour(self) -> bool:
    """Avança 1 hora. Retorna True se virou o dia."""
    self.hour += 1
    if self.hour >= 24:
        self.hour = 0
        self._advance_day()
        return True
    return False

# Modificar update() para avançar em horas:
def update(self, dt: float, seconds_per_day: float) -> int:
    """Retorna número de horas que passaram nesse frame."""
    seconds_per_hour = seconds_per_day / 24
    self.elapsed += dt
    ticks = 0
    while self.elapsed >= seconds_per_hour:
        self.elapsed -= seconds_per_hour
        self._advance_hour()
        ticks += 1
    return ticks

# Adicionar ao __str__:
def __str__(self) -> str:
    months = ["Jan","Fev","Mar","Abr","Mai","Jun",
              "Jul","Ago","Set","Out","Nov","Dez"]
    return f"Dia {self.day} de {months[self.month]} — Ano {self.year} — {self.season} — {self.hour:02d}h"

# Adicionar property:
@property
def day_of_week(self) -> int:
    """0=Seg … 6=Dom."""
    total_days = (self.year - 1) * 360 + self.month * 30 + self.day
    return total_days % 7
```

---

## 8. main.py — ajustes para hora e interação

```python
# No game loop, modificar o bloco de update:

ticks = time_system.update(dt, SECONDS_PER_DAY)
for _ in range(ticks):
    village_model.hour = time_system.hour
    village_model._day_of_week = time_system.day_of_week
    village_model.step()
    # Bolsa Família: só no dia 1 de cada mês
    if time_system.day == 1 and time_system.hour == 0:
        village_model._check_bolsa_familia()

# No bloco de eventos, adicionar clique:
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    mx, my = event.pos
    tile_col = (mx + camera_x) // TILE_SIZE
    tile_row = (my + camera_y) // TILE_SIZE
    _handle_click(tile_row, tile_col, player, village_model, time_system)

# Fora do loop, adicionar função:
def _handle_click(tile_row: int, tile_col: int, player, village_model, time_system) -> None:
    from settings import INTERACTION_RADIUS_TILES, TILE_SIZE
    player_tile_row = player.y // TILE_SIZE
    player_tile_col = player.x // TILE_SIZE
    dist = max(abs(tile_row - player_tile_row), abs(tile_col - player_tile_col))
    if dist > INTERACTION_RADIUS_TILES:
        return
    targets = village_model.villagers_at(tile_row, tile_col)
    for v in targets:
        if not v.known_to_player:
            v.known_to_player = True
            v.day_met = time_system.day + time_system.month * 30 + (time_system.year - 1) * 360
            print(f"Conheceu: {v.full_name} — {v.employment_status.name}")
```

---

## 9. ui/hud.py — painel de conhecidos

Adicionar método à classe `HUD`:

```python
def draw_known_panel(self, surface: pygame.Surface, village_model) -> None:
    """Painel lateral direito com lista de villagers conhecidos."""
    known = village_model.known_villagers()
    if not known:
        return

    panel_w = 220
    panel_x = surface.get_width() - panel_w - 8
    panel_y = 44
    line_h  = 16
    panel_h = min(len(known) * line_h + 20, 300)

    bg = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    surface.blit(bg, (panel_x, panel_y))

    header = self.font_small.render("Pessoas conhecidas", True, (255, 220, 100))
    surface.blit(header, (panel_x + 6, panel_y + 4))

    for i, v in enumerate(known[:15]):   # máximo 15 visíveis
        emp = v.employment_status.name.capitalize()
        line = f"{v.full_name} ({emp})"
        txt = self.font_small.render(line, True, (220, 220, 220))
        surface.blit(txt, (panel_x + 6, panel_y + 20 + i * line_h))
```

Chamar no `draw()` principal do `main.py`:
```python
hud.draw_known_panel(screen, village_model)
```

---

## Checklist de entrega da Fase 2 corrigida

- [ ] `settings.py` com todas as novas constantes
- [ ] `distributions.py` com nomes, sobrenomes, patrimônio (log-normal documentada), `child_age` corrigida
- [ ] `establishment.py` criado com tipos e lógica de venda (respeita estoque E orçamento)
- [ ] `layout.py` com `assign_establishments` (peso por proximidade à praça)
- [ ] `villager.py` refatorado: `cash`, mobilidade por hora, `known_to_player`, `try_weekly_shopping`
- [ ] `village.py` refatorado: famílias com sobrenome, ocupações, Bolsa Família, step horário
- [ ] `time_system.py` com hora (0–23) e `day_of_week`
- [ ] `main.py` com step horário, clique de interação
- [ ] `hud.py` com painel de conhecidos
- [ ] Agentes visualmente distintos se conhecidos (anel branco)

---

*Fase 2 — Correções — junho 2025*
