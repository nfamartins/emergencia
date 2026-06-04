# CLAUDE.md — Emergência

Jogo em Python/Pygame com simulação de agentes (ABM). Uma mulher de SP muda para uma cidade pequena do Brasil; o jogador age no mundo enquanto um sistema social vivo roda por baixo.

---

## Princípios de desenvolvimento

- **Elegância e legibilidade:** código claro e bem nomeado vale mais que comentário. Identifiers expressivos, funções pequenas com responsabilidade única, sem abstrações prematuras.
- **Modularidade:** cada sistema do jogo (tempo, mapa, agentes, UI, ABM) vive em seu próprio módulo. Dependências explícitas, sem acoplamento desnecessário entre camadas.
- **Skills para padrões recorrentes:** sempre que um padrão de desenvolvimento ou visual se repetir (ex: renderização de tiles, desenho de painéis HUD, comportamento de agente), criar uma skill reutilizável em vez de duplicar código.
- **Inglês no código:** nomes de pastas, arquivos, funções, variáveis e classes sempre em inglês. Português apenas em strings visíveis ao jogador e em comentários.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Linguagem | Python |
| Engine | Pygame |
| ABM | Mesa |
| Rede social | NetworkX |
| Visualização | Painel Pygame / Matplotlib |

**Gerenciamento de ambiente:** Poetry (2.x).

```bash
# instalar dependências
poetry install

# ativar shell
poetry shell

# rodar o jogo
poetry run python game/main.py

# adicionar nova dependência
poetry add <pacote>
```

Python requerido: `>=3.12,<3.14.1 || >3.14.1`

---

## Estrutura de arquivos (alvo)

```
game/
├── main.py
├── settings.py
├── save.py
├── world/
│   ├── map.py           # geração do mapa (vila + rural)
│   ├── layout.py        # geometria: blocos, terrenos, praça
│   ├── distributions.py # distribuições demográficas (IBGE)
│   └── time_system.py
├── abm/
│   ├── village.py       # Mesa Model — famílias e step diário
│   └── villager.py      # Mesa Agent — atributos + relações familiares
├── entities/
│   └── player.py
└── ui/
    └── hud.py
docs/
└── concept_art/
    └── village_layout_v1.png   ← salvar a imagem aqui manualmente
```

## Mapa — parâmetros espaciais

**1 tile = 1 m²**

| Elemento | Dimensão (tiles) |
|---|---|
| Quarteirão | 100 × 50 |
| Terreno | 25 × 25 |
| Rua | 5 de largura |
| Margem do mapa | 10 |
| Praça central | 100 × 50 (bloco central do grid 3×3) |
| Vila total | 320 × 170 |
| Mapa total | 750 × 200 |

**Layout:** 9 quarteirões (3×3 grid) — o central é a praça. 8 quarteirões × 8 terrenos = 64 terrenos (12 comerciais/institucionais nos terrenos que fazem face à praça, 52 residenciais).

**Posição do jogador (home):** `PLAYER_HOME_COL=440, PLAYER_HOME_ROW=35` — fazenda inicial na área rural.

**Área rural (col > 330):** rio no topo, fazenda inicial, manchas de mata, lagoa, estradas de terra.

## Modelo demográfico

Famílias geradas via `world/distributions.py` (baseado em PNAD IBGE 2022):

| Tipo | Proporção | Composição |
|---|---|---|
| single | 14% | 1 adulto |
| couple | 20% | 2 adultos (casal) |
| couple_children | 50% | 2 adultos + 1–3 filhos |
| single_parent | 16% | 1 adulto + 1–4 filhos |

- **Adultos:** gênero aleatório (50/50), idade normal(µ=40, σ=15), clamp [25, 85]
- **Parceiro:** idade normal(base, σ=5), clamp [25, 85]
- **Filhos:** gênero aleatório, idade uniforme [0, min(24, idade_pai−19)]
- **30 famílias iniciais** designadas a terrenos residenciais aleatórios (22 ficam vazios)

---

## Conceito central

- Exploração 2D top-down (pixel art, inspiração Stardew Valley)
- ABM roda completo desde o início; o jogador desbloqueia *acesso epistêmico* ao sistema progressivamente
- Dois modos alternáveis pelo jogador:
  - **Modo Mundo** (TAB para sair): explorar, craftar, plantar, interagir com NPCs
  - **Modo Sistema** (TAB para entrar): painel de análise — fluxos, redes, indicadores — pausa o tempo
- A tensão entre *agir* e *entender* é o coração do jogo

---

## Mecânicas-chave

**Tempo:** 1 tick = 1 dia de jogo. Dias → meses → anos. Estações mudam a paleta visual e os parâmetros do ABM.

**Agentes (Fase 2+):** 20–30 agentes com atributos `fome`, `renda`, `saúde`, `satisfação`. Scheduler diário. Podem migrar ou morrer se atributos chegam a zero.

**Conhecimento como recurso:** O ABM roda completo desde o início. O que muda é o acesso epistêmico do jogador, desbloqueado por tempo, vínculos e estudo:

| Camada | Nome | Como desbloquear |
|---|---|---|
| 0 | Chegada | Estado inicial |
| 1 | Observação | Tempo + presença em espaços comuns |
| 2 | Relações | Vínculos com agentes-chave |
| 3 | Instituições | Participação em associações |
| 4 | Teoria | Livros, cursos, mentorias |

**Fracasso irreversível + meta-loop:** O jogo tem game over real. Ao recomeçar, conhecimento epistêmico acumulado persiste (roguelike de epistemologia).

**Cidade escolhida = parâmetros do ABM:** dados reais do IBGE/MapBiomas (IDH, bioma, Gini, migração) definem o sistema inicial.

---

## Fases de desenvolvimento (MVP)

| Fase | Entregável jogável | Status |
|---|---|---|
| 1 | Mapa navegável + tempo + estações | Concluído |
| 2 | Vila com 20–30 agentes vivos | Concluído |
| 3 | Ações do jogador afetam os agentes | Planejado |
| 4 | Painel Modo Sistema mínimo | Planejado |
| 5 | Game over + recomeço com insight | Planejado |
| 6 | Mais culturas, dilemas, atributos, rede social | Planejado |

### Fase 1 — Fundação (detalhes)

Entrega: mapa 2D navegável, personagem com WASD/setas, câmera centralizada, sistema de tempo (dias/meses/anos), estações com paleta dinâmica, HUD com data/estação, TAB como placeholder para Modo Sistema.

**settings.py — constantes:**
- Tela: 1280×720, 60 FPS
- Mapa: tiles 32px, 40×30 tiles
- `SECONDS_PER_DAY = 3.0` (segundos reais por dia de jogo, ajustável)
- Estações por mês (0-indexado): Verão 0–2, Outono 3–5, Inverno 6–8, Primavera 9–11

**Tipos de tile:** GRASS, DIRT, WATER, VILLAGE. Vila no centro do mapa; borda de água; parcelas de terra ao sul da vila.

**Câmera:** centralizada no jogador (`camera_x = player.x - SCREEN_WIDTH // 2`).

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
