from backend.engine.game import Game


def test_game_has_fixed_seed_and_initial_agents():
    game = Game(seed=123)
    snapshot = game.snapshot()
    assert snapshot["seed"] == 123
    assert "agent_maxwell" in snapshot["npc_states"]
    assert snapshot["npc_states"]["agent_maxwell"]["infection_state"] == "latent"


def test_dialogue_writes_memory_and_advances_time():
    game = Game(seed=123)
    before = game.snapshot()["tick"]
    response = game.ask("agent_willow", "你知道感染源吗？")
    assert response["action"] in {"answer", "evade", "reveal"}
    assert game.snapshot()["tick"] == before + 1
    assert game.agents["agent_willow"].memory.memories[-1].source == "player_action"


def test_claim_verification_is_recorded():
    game = Game(seed=123)
    result = game.investigate("claim_010")
    assert result["truth"] is True
    assert "claim_010" in game.snapshot()["discovered_claims"]
