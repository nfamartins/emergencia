# CLAUDE.md — Emergência

Jogo em Python/Pygame com simulação de agentes (ABM). Uma mulher de SP muda para uma cidade pequena do Brasil; o jogador age no mundo enquanto um sistema social vivo roda por baixo.

---

## Princípios de desenvolvimento

- **Elegância e legibilidade:** código claro e bem nomeado vale mais que comentário. Identifiers expressivos, funções pequenas com responsabilidade única, sem abstrações prematuras.
- **Modularidade:** cada sistema do jogo (tempo, mapa, agentes, UI, ABM) vive em seu próprio módulo. Dependências explícitas, sem acoplamento desnecessário entre camadas.
- **Skills para padrões recorrentes:** sempre que um padrão de desenvolvimento ou visual se repetir (ex: renderização de tiles, desenho de painéis HUD, comportamento de agente), criar uma skill reutilizável em vez de duplicar código.
- **Inglês no código:** nomes de pastas, arquivos, funções, variáveis e classes sempre em inglês. Português apenas em strings visíveis ao jogador e em comentários.
- **Status do CLAUDE.md:** ao concluir uma fase ou etapa planejada, atualizar imediatamente o status na tabela de fases.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python ≥ 3.12 |
| Engine | Pygame 2.6 |
| ABM | Mesa 3.5 |
| Rede social | NetworkX 3.6 |
| Visualização | Painel Pygame / Matplotlib |
| Ambiente | Poetry 2.x |

```bash
poetry install               # instalar dependências
poetry shell                 # ativar ambiente
poetry run python game/main.py   # rodar o jogo
poetry add <pacote>          # adicionar dependência
```

Python requerido: `>=3.12,<3.14.1 || >3.14.1`

---

## Estrutura de arquivos

```
game/
├── main.py              # game loop, estados, câmera
├── settings.py          # todas as constantes globais
├── save.py              # save/load (saves/save.json)
├── world/
│   ├── map.py           # geração de tiles (vila + rural)
│   ├── layout.py        # geometria: blocos, terrenos, praça
│   ├── distributions.py # distribuições demográficas (IBGE PNAD 2022)
│   └── time_system.py   # dias, meses, anos, estações, horas, minutos
├── abm/
│   ├── village.py       # Mesa Model — geração de famílias, step diário
│   └── villager.py      # Mesa Agent — atributos comportamentais + relações
├── entities/
│   └── player.py        # personagem, movimento, posição home
└── ui/
    ├── hud.py           # HUD superior (tempo), rodapé (hints + versão), modal fim de dia
    └── minimap.py       # overview full-screen do mapa (tecla M)
docs/
└── concept_art/
    └── village_layout_v1.jpg   # rascunho inicial do layout da vila
saves/
└── save.json            # gerado em runtime (gitignored)
```

---

## Controles

| Tecla | Ação |
|---|---|
| WASD / setas | Mover personagem |
| M | Abrir/fechar mapa overview |
| ENTER | Confirmar fim de dia (no modal) |
| TAB | Modo Sistema (Fase 4 — placeholder) |
| ESC | Fechar mapa overview / sair do jogo |

---

## Mapa — parâmetros espaciais

**1 tile = 1 m × 1 m**

| Elemento | Dimensão (tiles) |
|---|---|
| Quarteirão | 100 × 50 |
| Terreno | 25 × 25 |
| Rua / calçada | 5 de largura |
| Margem horizontal | 10 |
| Margem vertical (rural acima da vila) | 90 |
| Praça central | 100 × 50 (bloco (1,1) do grid 3×3) |
| Vila total | 320 × 170 (cols 10–330, rows 90–260) |
| Mapa total | 750 × 280 |

**Layout da vila:** grid 3×3 de quarteirões — central = praça. 8 quarteirões × 8 terrenos = 64 terrenos. 12 comerciais/institucionais (face à praça), 52 residenciais.

**Conceito art:** `docs/concept_art/village_layout_v1.jpg`

**Divisão do mapa:**

| Área | Colunas | Linhas | Conteúdo |
|---|---|---|---|
| Rural superior esquerdo | 0–330 | 0–89 | Rio diagonal, matas |
| Vila | 10–330 | 90–260 | 9 quarteirões, praça, ruas |
| Estrada de terra (vertical) | 330–334 | 0–279 | Separa vila e rural |
| Rural direito | 335–750 | 0–279 | Rio (topo), fazenda, matas, lagoa, estrada (fundo) |

**Posição home do jogador:** col 420, row 35 — centro da fazenda inicial.

---

## Sistema de tempo

- `SECONDS_PER_HOUR = 60.0` → 1 hora de jogo = 1 minuto real
- Dia começa às 06:00, fim de dia às 22:00 (16 horas = 16 minutos reais)
- HUD exibe: `Dia D de Mês · Ano A · Estação · HH:MM`
- Às 22:00: modal de fim de dia aparece (ENTER para dormir e salvar)
- Ao confirmar: ABM tick (step diário), save, retorno home, próximo dia

---

## Modelo demográfico

Módulo: `world/distributions.py` — baseado em PNAD/IBGE 2022.

| Tipo de família | Proporção |
|---|---|
| single (1 adulto) | 14% |
| couple (2 adultos) | 20% |
| couple_children (2 adultos + 1–3 filhos) | 50% |
| single_parent (1 adulto + 1–4 filhos) | 16% |

- **Adultos:** gênero 50/50, idade normal(µ=40, σ=15) ∈ [25, 85]
- **Parceiro:** idade normal(base, σ=5) ∈ [25, 85]
- **Filhos:** gênero 50/50, idade uniforme ∈ [0, min(24, idade_pai − 19)]
- **30 famílias** designadas a terrenos residenciais aleatórios (22 ficam vazios)
- Cada `Villager` armazena: `partner_id`, `parent_ids`, `child_ids`

---

## Agentes (ABM)

Classe `Villager(Agent)` — atributos 0–100:
- `hunger`, `income`, `health`, `satisfaction`
- `role`: ADULT | CHILD
- Crianças não trabalham (`income` fixo em 0)
- Step diário: vagueia no terreno → consome → trabalha → saúde → satisfação
- Remove-se se `health ≤ 0` (morte) ou `income = 0 + hunger > 85` (migração)
- Cor: verde (satisfeito) → vermelho (insatisfeito)

---

## Fases de desenvolvimento (MVP)

| Fase | Entregável jogável | Status |
|---|---|---|
| 1 | Mapa navegável + tempo + estações | Concluído |
| 2 | Vila com agentes vivos + famílias demográficas | Concluído |
| 3 | Ações do jogador afetam os agentes | Planejado |
| 4 | Painel Modo Sistema mínimo | Planejado |
| 5 | Game over + recomeço com insight | Planejado |
| 6 | Mais culturas, dilemas, atributos, rede social | Planejado |

---

## Dilemas centrais (sem resposta certa — ABM arbitra)

| Dilema | Caminho A | Caminho B |
|---|---|---|
| Produção | Monocultura: retorno rápido, degradação lenta | Agrofloresta: retorno lento, resiliência crescente |
| Integração | Alta: influência e informação, e obrigações | Baixa: autonomia, mas invisibilidade sistêmica |
| Mercado | Atravessador: caixa imediato, drena economia local | Cooperativa: melhor margem, exige relações |
| Água | Irrigação intensiva: produtividade alta, aquífero em risco | Manejo conservador: menor produção, resiliência |

---

## Perguntas em aberto

- Quais conhecimentos do meta-loop persistem exatamente entre partidas?
- Como tratar eventos externos reais? (seca histórica, pandemia, crise econômica)
- Arte: pixel art 2D top-down confirmado, ou avaliar outras estéticas?
- Existe multiplayer local/assíncrono (duas pessoas na mesma vila)?
- O Modo Sistema tem narrador/voz, ou é puramente visual/dado?
