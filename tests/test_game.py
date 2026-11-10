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
    game.story_action("ask_wilson")
    game.story_action("ask_wolfgang")
    game.move_to("forest_edge")
    response = game.ask("agent_willow", "你知道感染源吗？")
    assert response["action"] in {"answer", "evade", "reveal"}
    assert game.snapshot()["tick"] == before + 1
    assert game.snapshot()["action_points"] == 3
    assert game.agents["agent_willow"].memory.memories[-1].source == "player_action"


def test_claim_verification_is_recorded():
    game = Game(seed=123)
    result = game.investigate("claim_001")
    assert result["truth"] is True
    assert "claim_001" in game.snapshot()["discovered_claims"]


def test_good_ending_requires_source_claims_and_sealing():
    game = Game(seed=123)
    game.story_action("ask_wilson")
    game.story_action("ask_wolfgang")
    game.investigate("claim_001")
    assert game.seal() is False
    assert game.snapshot()["status"] == "running"

    game.move_to("forest_edge")
    game.investigate("claim_003")
    game.move_to("camp")
    game.move_to("graveyard")
    game.investigate("claim_005")
    game.move_to("camp")
    assert "ruins_path" in game.snapshot()["unlocked_scenes"]
    game.move_to("ruins_path")
    game.investigate("claim_010")
    assert game.seal() is True
    assert game.snapshot()["status"] == "ending_good"


def test_wrong_accusation_ends_game():
    game = Game(seed=123)
    assert game.accuse("agent_willow") == "ending_wrong_accuse"


def test_time_limit_ends_game_without_sealing_source():
    game = Game(seed=123)
    for _ in range(8):
        game.end_day()
        if game.snapshot()["status"] == "ending_bad":
            break
    assert game.snapshot()["status"] == "ending_bad"


def test_ending_day_discards_unused_points_and_resets_next_day():
    game = Game(seed=123)
    game.end_day()
    snapshot = game.snapshot()
    assert snapshot["day"] == 2
    assert snapshot["phase"] == "day"
    assert snapshot["action_points"] == 3
    assert snapshot["event_log"][-1]["type"] == "day_started"


def test_invalid_claim_does_not_consume_action_point():
    game = Game(seed=123)
    result = game.investigate("unknown_claim")
    assert result["valid"] is False
    assert game.snapshot()["action_points"] == 3


def test_move_requires_connected_scene_without_consuming_action_point():
    game = Game(seed=123)
    game.story_action("ask_wilson")
    game.story_action("ask_wolfgang")
    result = game.move_to("forest_edge")
    assert result["valid"] is True
    assert game.snapshot()["current_scene"] == "forest_edge"
    assert game.snapshot()["action_points"] == 1


def test_two_prologue_actions_unlock_scenes_and_agents():
    game = Game(seed=123)
    assert game.snapshot()["unlocked_scenes"] == ["camp"]
    game.story_action("ask_wilson")
    assert "forest_edge" not in game.snapshot()["unlocked_scenes"]
    game.story_action("inspect_lab")
    snapshot = game.snapshot()
    assert "forest_edge" in snapshot["unlocked_scenes"]
    assert "graveyard" in snapshot["unlocked_scenes"]
    assert "agent_willow" in snapshot["unlocked_agents"]


def test_two_stage_one_claims_unlock_ruins_and_maxwell():
    game = Game(seed=123)
    game.story_action("ask_wilson")
    game.story_action("ask_wolfgang")
    game.move_to("forest_edge")
    game.investigate("claim_003")
    game.move_to("camp")
    game.move_to("graveyard")
    game.investigate("claim_005")
    snapshot = game.snapshot()
    assert "ruins_path" in snapshot["unlocked_scenes"]
    assert "agent_maxwell" in snapshot["unlocked_agents"]


def test_dialogue_requires_npc_in_current_scene():
    game = Game(seed=123)
    response = game.ask("agent_willow", "你知道什么？")
    assert response["action"] == "invalid"
    assert game.snapshot()["action_points"] == 3
