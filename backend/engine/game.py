import random
from typing import Any

from ..agents.npc_agent import MockNPCAgent
from ..data_loader import load_json
from .rules import advance_time, accuse, seal_source, verify_claim
from .state import GameState


class Game:
    def __init__(self, seed: int = 7):
        random.seed(seed)
        self.agents_config = load_json("agents.json")
        self.claims = load_json("claims.json")
        memories = load_json("memories.json")
        self.state = GameState(seed=seed)
        self.agents = {}
        for config in self.agents_config:
            npc = {"infection_state": config["initial_infection"], "trust_to_player": config["initial_trust"], "exposure_count": 0, "scene": config["initial_scene"]}
            self.state.npc_states[config["agent_id"]] = npc
            self.agents[config["agent_id"]] = MockNPCAgent(config, memories.get(config["agent_id"], []))

    def ask(self, agent_id: str, text: str) -> dict[str, Any]:
        response = self.agents[agent_id].respond(text, self.state.npc_states[agent_id])
        self.state.event_log.append({"type": "dialogue", "agent_id": agent_id, "text": text, "action": response["action"]})
        advance_time(self.state, self.agents_config)
        return response

    def investigate(self, claim_id: str) -> dict[str, Any]:
        claim = next(item for item in self.claims if item["claim_id"] == claim_id)
        result = verify_claim(self.state, claim)
        advance_time(self.state, self.agents_config)
        return result

    def seal(self) -> bool:
        return seal_source(self.state)

    def accuse(self, agent_id: str) -> str:
        return accuse(self.state, agent_id)

    def snapshot(self) -> dict[str, Any]:
        return self.state.to_dict()
