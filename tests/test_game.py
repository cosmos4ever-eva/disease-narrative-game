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


def test_good_ending_requires_source_claims_and_sealing():
    game = Game(seed=123)
    game.investigate("claim_001")
    assert game.seal() is False
    assert game.snapshot()["status"] == "running"

    game.investigate("claim_010")
    assert game.seal() is True
    assert game.snapshot()["status"] == "ending_good"


def test_wrong_accusation_ends_game():
    game = Game(seed=123)
    assert game.accuse("agent_willow") == "ending_wrong_accuse"


def test_time_limit_ends_game_without_sealing_source():
    game = Game(seed=123)
    for _ in range(8):
        game.ask("agent_wilson", "你知道什么？")
        if game.snapshot()["status"] == "ending_bad":
            break
    assert game.snapshot()["status"] == "ending_bad"
