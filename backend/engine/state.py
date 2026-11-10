from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    seed: int
    day: int = 1
    tick: int = 0
    phase: str = "day"
    action_points: int = 3
    max_action_points: int = 3
    current_scene: str = "camp"
    status: str = "running"
    source_sealed: bool = False
    accused_agent_id: str | None = None
    unlocked_scenes: set[str] = field(default_factory=lambda: {"camp"})
    unlocked_agents: set[str] = field(default_factory=lambda: {"agent_wilson", "agent_wolfgang"})
    story_actions_completed: set[str] = field(default_factory=set)
    current_story_node: str = "prologue_camp_start"
    discovered_claims: set[str] = field(default_factory=set)
    discovered_items: set[str] = field(default_factory=set)
    npc_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    event_log: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "day": self.day,
            "tick": self.tick,
            "phase": self.phase,
            "action_points": self.action_points,
            "max_action_points": self.max_action_points,
            "current_scene": self.current_scene,
            "status": self.status,
            "source_sealed": self.source_sealed,
            "accused_agent_id": self.accused_agent_id,
            "unlocked_scenes": sorted(self.unlocked_scenes),
            "unlocked_agents": sorted(self.unlocked_agents),
            "story_actions_completed": sorted(self.story_actions_completed),
            "current_story_node": self.current_story_node,
            "discovered_claims": sorted(self.discovered_claims),
            "discovered_items": sorted(self.discovered_items),
            "npc_states": self.npc_states,
            "event_log": self.event_log,
        }
