from typing import Any

from .state import GameState


def verify_claim(state: GameState, claim: dict[str, Any]) -> dict[str, Any]:
    claim_id = claim["claim_id"]
    state.discovered_claims.add(claim_id)
    state.event_log.append({"type": "claim_verified", "claim_id": claim_id})
    return {"claim_id": claim_id, "truth": claim["truth"], "impact": claim.get("impact", "")}


def advance_time(state: GameState, npc_configs: list[dict[str, Any]]) -> None:
    state.tick += 1
    if state.tick % 2 == 0:
        for npc_id, npc in state.npc_states.items():
            if npc.get("infection_state") == "latent":
                npc["exposure_count"] = npc.get("exposure_count", 0) + 1
                if npc["exposure_count"] >= 3:
                    npc["infection_state"] = "confirmed"
    if state.tick >= 8 and not state.discovered_items:
        state.status = "ending_bad"
