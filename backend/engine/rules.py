from typing import Any

from .state import GameState


SOURCE_CLAIMS = {"claim_001", "claim_010"}
SOURCE_AGENT_ID = "agent_maxwell"


def verify_claim(state: GameState, claim: dict[str, Any]) -> dict[str, Any]:
    claim_id = claim["claim_id"]
    state.discovered_claims.add(claim_id)
    state.event_log.append({"type": "claim_verified", "claim_id": claim_id})
    return {"claim_id": claim_id, "truth": claim["truth"], "impact": claim.get("impact", "")}


def seal_source(state: GameState) -> bool:
    """Seal the source only after both source claims have been verified."""
    if not SOURCE_CLAIMS.issubset(state.discovered_claims):
        return False
    state.source_sealed = True
    state.discovered_items.add("item_shadow_box")
    state.event_log.append({"type": "source_sealed", "item_id": "item_shadow_box"})
    evaluate_ending(state)
    return True


def accuse(state: GameState, agent_id: str) -> str:
    state.accused_agent_id = agent_id
    state.event_log.append({"type": "accusation", "agent_id": agent_id})
    if agent_id == SOURCE_AGENT_ID and state.source_sealed:
        state.status = "ending_good"
    elif agent_id != SOURCE_AGENT_ID:
        state.status = "ending_wrong_accuse"
    evaluate_ending(state)
    return state.status


def evaluate_ending(state: GameState) -> str:
    if state.status.startswith("ending_"):
        return state.status
    confirmed_count = sum(
        npc.get("infection_state") == "confirmed"
        for npc in state.npc_states.values()
    )
    if state.source_sealed and confirmed_count <= 1:
        state.status = "ending_good"
    elif all(npc.get("infection_state") in {"latent", "confirmed"} for npc in state.npc_states.values()) and state.npc_states:
        state.status = "ending_bad"
    elif state.tick >= 8 and not state.source_sealed:
        state.status = "ending_bad"
    return state.status


def advance_time(state: GameState, npc_configs: list[dict[str, Any]]) -> None:
    state.tick += 1
    if state.tick % 2 == 0:
        for npc_id, npc in state.npc_states.items():
            if npc.get("infection_state") == "latent":
                npc["exposure_count"] = npc.get("exposure_count", 0) + 1
                if npc["exposure_count"] >= 3:
                    npc["infection_state"] = "confirmed"
    evaluate_ending(state)


def consume_action(state: GameState) -> bool:
    if state.phase != "day" or state.action_points <= 0 or state.status != "running":
        return False
    state.action_points -= 1
    return True
