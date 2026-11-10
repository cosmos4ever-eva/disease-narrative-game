import random
from typing import Any

from ..agents.npc_agent import MockNPCAgent
from ..data_loader import load_json
from ..storage import save_state
from .rules import advance_time, accuse, consume_action, seal_source, verify_claim
from .state import GameState


class Game:
    def __init__(self, seed: int = 7):
        random.seed(seed)
        self.agents_config = load_json("agents.json")
        self.claims = load_json("claims.json")
        self.scenes = {scene["scene_id"]: scene for scene in load_json("scenes.json")}
        memories = load_json("memories.json")
        self.state = GameState(seed=seed)
        self.agents = {}
        for config in self.agents_config:
            npc = {"infection_state": config["initial_infection"], "trust_to_player": config["initial_trust"], "exposure_count": 0, "scene": config["initial_scene"]}
            self.state.npc_states[config["agent_id"]] = npc
            self.agents[config["agent_id"]] = MockNPCAgent(config, memories.get(config["agent_id"], []))

    def ask(self, agent_id: str, text: str) -> dict[str, Any]:
        if agent_id not in self.agents or self.state.npc_states[agent_id]["scene"] != self.state.current_scene or not consume_action(self.state):
            return {"action": "invalid", "dialogue": "当前无法执行这个行动。", "reason": "action_not_allowed"}
        response = self.agents[agent_id].respond(text, self.state.npc_states[agent_id])
        self.state.event_log.append({"type": "dialogue", "agent_id": agent_id, "text": text, "action": response["action"]})
        self._finish_action()
        return response

    def investigate(self, claim_id: str) -> dict[str, Any]:
        if not consume_action(self.state):
            return {"claim_id": claim_id, "truth": None, "impact": "当前无法调查。", "valid": False}
        claim = next((item for item in self.claims if item["claim_id"] == claim_id), None)
        if claim is None:
            self.state.action_points += 1
            return {"claim_id": claim_id, "truth": None, "impact": "未知 Claim。", "valid": False}
        if claim.get("scene") != self.state.current_scene:
            self.state.action_points += 1
            return {"claim_id": claim_id, "truth": None, "impact": "这个线索不属于当前场景。", "valid": False}
        result = verify_claim(self.state, claim)
        result["valid"] = True
        self._finish_action()
        return result

    def move_to(self, scene_id: str) -> dict[str, Any]:
        if scene_id not in self.scenes:
            return {"valid": False, "impact": "未知场景。"}
        if scene_id == self.state.current_scene:
            return {"valid": False, "impact": "你已经在这个场景。"}
        if scene_id not in self.scenes[self.state.current_scene]["connections"]:
            return {"valid": False, "impact": "这个场景目前无法直接到达。"}
        if self.state.phase != "day" or self.state.status != "running":
            return {"valid": False, "impact": "当前无法移动。"}
        previous = self.state.current_scene
        self.state.current_scene = scene_id
        self.state.event_log.append({"type": "move", "from": previous, "to": scene_id})
        save_state(self.snapshot())
        return {"valid": True, "from": previous, "to": scene_id}

    def seal(self) -> bool:
        if self.state.phase != "day" or self.state.status != "running":
            return False
        result = seal_source(self.state)
        if result:
            self.state.event_log.append({"type": "action", "action": "seal_source"})
            save_state(self.snapshot())
        return result

    def accuse(self, agent_id: str) -> str:
        if not consume_action(self.state):
            return self.state.status
        result = accuse(self.state, agent_id)
        self._finish_action()
        return result

    def end_day(self) -> dict[str, Any]:
        if self.state.phase != "day" or self.state.status != "running":
            return self.snapshot()
        self.state.event_log.append({"type": "day_ended", "day": self.state.day, "unused_action_points": self.state.action_points})
        self.state.action_points = 0
        self._resolve_night()
        return self.snapshot()

    def _finish_action(self) -> None:
        save_state(self.snapshot())
        if self.state.action_points == 0:
            self._resolve_night()

    def _resolve_night(self) -> None:
        if self.state.status != "running":
            return
        self.state.phase = "night"
        self.state.event_log.append({"type": "night_started", "day": self.state.day})
        for config in self.agents_config:
            self.state.event_log.append({"type": "npc_night_action", "agent_id": config["agent_id"], "action": "observe"})
        advance_time(self.state, self.agents_config)
        if self.state.status == "running":
            self.state.day += 1
            self.state.phase = "day"
            self.state.action_points = self.state.max_action_points
            self.state.event_log.append({"type": "day_started", "day": self.state.day, "action_points": self.state.action_points})
        save_state(self.snapshot())

    def snapshot(self) -> dict[str, Any]:
        return self.state.to_dict()
