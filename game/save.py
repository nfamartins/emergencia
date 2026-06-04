import json
from pathlib import Path

_SAVES_DIR = Path(__file__).parent.parent / "saves"
_SAVE_FILE = _SAVES_DIR / "save.json"


def save_game(time_system, player) -> None:
    _SAVES_DIR.mkdir(exist_ok=True)
    data = {
        "time":   time_system.to_dict(),
        "player": {"x": player.x, "y": player.y},
    }
    with open(_SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_game(time_system, player) -> bool:
    if not _SAVE_FILE.exists():
        return False
    with open(_SAVE_FILE, encoding="utf-8") as f:
        data = json.load(f)
    time_system.from_dict(data["time"])
    player.x = data["player"]["x"]
    player.y = data["player"]["y"]
    return True
