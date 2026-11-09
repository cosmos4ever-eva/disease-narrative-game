from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    seed: int
    day: int = 1
    tick: int = 0
    current_scene: str = "camp"
    status: str = "running"
    discovered_claims: set[str] = field(default_factory=set)
    discovered_items: set[str] = field(default_factory=set)
    npc_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    event_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "day": self.day,
            "tick": self.tick,
            "current_scene": self.current_scene,
            "status": self.status,
            "discovered_claims": sorted(self.discovered_claims),
            "discovered_items": sorted(self.discovered_items),
            "npc_states": self.npc_states,
            "event_log": self.event_log,
        }
