import json
from pathlib import Path
from typing import Any


SAVE_PATH = Path(__file__).resolve().parents[1] / "saves" / "current_game.json"


def save_state(state: dict[str, Any]) -> None:
    SAVE_PATH.parent.mkdir(exist_ok=True)
    SAVE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
