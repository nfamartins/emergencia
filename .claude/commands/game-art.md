# Game Art — Padrões Visuais do Emergência

Referência para criação e ajuste de elementos visuais. Consultar antes de adicionar cores, tiles, UI ou qualquer elemento gráfico.

---

## Paleta de cores base (`settings.py`)

| Constante         | RGB               | Uso                          |
|-------------------|-------------------|------------------------------|
| `COLOR_GRASS`     | (86, 130, 46)     | Tile de grama                |
| `COLOR_DIRT`      | (139, 90, 43)     | Tile de terra / lavoura      |
| `COLOR_WATER`     | (64, 164, 223)    | Tile de água                 |
| `COLOR_VILLAGE`   | (180, 160, 120)   | Tile de vila                 |
| `COLOR_PLAYER`    | (255, 220, 100)   | Personagem                   |
| `COLOR_TEXT`      | (255, 255, 255)   | Texto principal              |
| `COLOR_TILE_BORDER` | (160, 160, 160) | Grade entre tiles (fundo)    |

Cores de estações (aplicadas como tint 30% sobre tiles GRASS e DIRT):

| Estação    | RGB               |
|------------|-------------------|
| Verão      | (210, 180, 100)   |
| Outono     | (180, 130, 70)    |
| Inverno    | (160, 180, 200)   |
| Primavera  | (120, 180, 100)   |

---

## Tiles

- Tamanho: `TILE_SIZE = 32px`
- Grade: tiles desenhados com `TILE_SIZE - 1` (1px de gap), fundo `COLOR_TILE_BORDER` — cinza suave, quase imperceptível
- Tint sazonal: só nos tiles `GRASS` e `DIRT` — mistura 70% cor base + 30% cor da estação
- Novos tiles: adicionar constante `COLOR_*` em `settings.py` e entrada em `_BASE_COLORS` / `_TINT_TILES` em `map.py`

---

## UI / HUD

**Fontes:** `SysFont("monospace", 18, bold=True)` para texto principal; `SysFont("monospace", 13)` para hints e info

**Barra superior** (altura 36px):
- Fundo: preto semitransparente `(0, 0, 0, 140)`
- Conteúdo: data + hora + estação

**Barra inferior** (altura 24px):
- Fundo: preto semitransparente `(0, 0, 0, 120)`
- Esquerda: dicas de controles — `(180, 180, 180)`
- Direita: versão do pygame/Python — `(120, 120, 120)`

**Modais / overlays:**
- Fundo geral: `(0, 0, 0, 160)` SRCALPHA
- Caixa: `(30, 30, 30)` preenchimento, `(200, 200, 200)` borda 2px, `border_radius=8`
- Texto de ação / destaque: `(220, 220, 100)`

---

## Princípios

- Paleta terrosa e dessaturada — remete a biomas brasileiros
- UI minimalista: não compete com o mundo, serve de legenda
- Tints sazonais criam variação sem multiplicar assets
- Ao adicionar um novo bioma/cidade, criar entrada em `SEASONS` ou equivalente com cor representativa do bioma
- Evitar cores puras RGB (0,255,0) — sempre preferir tons naturais
