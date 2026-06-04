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
poetry run python jogo/main.py

# adicionar nova dependência
poetry add <pacote>
```

Python requerido: `>=3.12,<3.14.1 || >3.14.1`

---

## Estrutura de arquivos (alvo)

```
jogo/
├── main.py              # entry point, game loop
├── settings.py          # constantes globais
├── world/
│   ├── __init__.py
│   ├── map.py           # mapa, tiles, renderização
│   └── time_system.py   # dias, meses, anos, estações
├── entities/
│   ├── __init__.py
│   └── player.py        # personagem, movimento
└── ui/
    ├── __init__.py
    └── hud.py           # HUD: data, estação, atributos básicos
```

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
| 1 | Mapa navegável + tempo + estações | Planejado |
| 2 | Vila com 20–30 agentes vivos | Planejado |
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
