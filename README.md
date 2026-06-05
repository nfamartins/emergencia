# Emergência

Um jogo de exploração 2D top-down onde suas ações moldam um sistema social vivo simulado por modelagem de agentes (ABM). Localizado no Brasil, com dados demográficos reais.

> Uma mulher, de São Paulo, cansada do ritmo urbano, compra um pedaço de terra numa cidade pequena. A vila tem vida própria — e você não sabe ainda como ela funciona.

---

## Requisitos

- **Python** 3.12 ou superior (exceto 3.14.1)
- **Poetry** 2.x — gerenciador de ambiente e dependências

### Verificar se já estão instalados

```bash
python --version   # deve ser 3.12+
poetry --version   # deve ser 2.x
```

### Instalar Poetry (caso necessário)

```bash
# Windows (PowerShell)
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -

# macOS / Linux
curl -sSL https://install.python-poetry.org | python3 -
```

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/nfamartins/emergencia.git
cd emergencia
```

Ou baixar o ZIP pelo GitHub e extrair.

### 2. Instalar dependências

```bash
poetry install
```

Isso cria automaticamente um `.venv` local com todas as dependências:
`pygame`, `mesa`, `networkx`, `matplotlib`.

### 3. Rodar o jogo

```bash
poetry run python game/main.py
```

---

## Controles

| Tecla | Ação |
|---|---|
| `W` `A` `S` `D` / setas | Mover personagem |
| `M` | Abrir/fechar mapa overview (visão completa) |
| `ENTER` | Confirmar fim de dia (quando modal aparecer) |
| `TAB` | Modo Sistema *(em desenvolvimento)* |
| `ESC` | Fechar mapa overview / sair do jogo |

---

## O que esperar ao rodar

Ao iniciar, você aparece na **fazenda inicial** (área rural, canto superior do mapa). Use WASD para explorar.

- **Mapa overview (M):** pressione M para ver o mapa completo. A vila fica na metade esquerda, com 9 quarteirões e praça central. Você (ponto amarelo) começa na área rural à direita.
- **Tempo:** 1 minuto real = 1 hora de jogo. O HUD superior mostra data, estação e horário.
- **Fim de dia:** às 22:00 aparece um modal. Pressione ENTER para dormir — o jogo salva automaticamente e avança para o próximo dia. O ABM faz um step: os moradores da vila envelhecem, trabalham, consomem.
- **Moradores:** o contador "moradores: N" no HUD mostra quantos agentes vivem na vila. Cada um tem família, atributos e comportamento próprio.

---

## Estrutura do projeto

```
game/          → código do jogo
docs/          → concept art e documentação
saves/         → save automático (gerado em runtime)
```

Consulte [CLAUDE.md](CLAUDE.md) para documentação técnica completa: arquitetura, parâmetros do mapa, modelo demográfico e roadmap de fases.

---

## Desenvolvimento

```bash
# Ativar ambiente interativo
poetry shell

# Adicionar nova dependência
poetry add <pacote>
```

---

*Projeto em desenvolvimento ativo — versão 0.1 (Fases 1 e 2 concluídas)*
