import streamlit as st

from backend.engine.game import Game


@st.cache_resource
def get_game(schema_version: int = 2) -> Game:
    # Bump this version when the Game object shape changes so Streamlit does not reuse stale state.
    return Game(seed=7)


game = get_game()
st.set_page_config(page_title="疫病推理游戏", layout="wide")
st.markdown("""
<style>
.scene-card { padding: 18px; border-radius: 14px; min-height: 145px; border: 1px solid #d9d4ca; }
.scene-card.current { border: 3px solid #8b5e34; box-shadow: 0 4px 16px rgba(75, 52, 30, .16); }
.scene-card h3 { margin: 4px 0 8px; }
.scene-card p { color: #5f5b55; font-size: .9rem; }
.warm { background: #fff4df; } .green { background: #eaf3e7; }
.violet { background: #f0eafa; } .stone { background: #ecebea; } .amber { background: #fff0d4; }
</style>
""", unsafe_allow_html=True)
st.title("疫病推理游戏")

with st.sidebar:
    st.subheader("游戏状态")
    snapshot = game.snapshot()
    st.write(f"Day {snapshot['day']} · Tick {snapshot['tick']}")
    st.write(f"阶段：{'白天' if snapshot['phase'] == 'day' else '夜晚'}")
    st.write(f"行动力：{snapshot['action_points']} / {snapshot['max_action_points']}")
    st.write(f"场景：{snapshot['current_scene']}")
    developer_mode = st.toggle("开发者模式", value=False)
    if st.button("重新开始"):
        get_game.clear()
        st.rerun()
    if st.button("结束白天"):
        game.end_day()
        st.rerun()

scene_map, right = st.columns([1.4, 1])
with scene_map:
    st.subheader("探索场景")
    current_scene = game.scenes[snapshot["current_scene"]]
    st.caption(current_scene["description"])
    scene_columns = st.columns(len(game.scenes))
    for column, scene in zip(scene_columns, game.scenes.values()):
        with column:
            is_current = scene["scene_id"] == snapshot["current_scene"]
            st.markdown(
                f'<div class="scene-card {scene["tone"]} {"current" if is_current else ""}">'
                f'<div style="font-size:2rem">{scene["symbol"]}</div>'
                f'<h3>{scene["name"]}</h3><p>{scene["description"]}</p></div>',
                unsafe_allow_html=True,
            )
            if not is_current and st.button("前往", key=f"move_{scene['scene_id']}"):
                result = game.move_to(scene["scene_id"])
                if result["valid"]:
                    st.rerun()
                st.warning(result["impact"])

    st.subheader(f"{current_scene['name']} 中的角色")
    nearby_agents = [
        agent_id for agent_id, npc in snapshot["npc_states"].items()
        if npc["scene"] == snapshot["current_scene"]
    ]
    if nearby_agents:
        st.write("、".join(nearby_agents))
    else:
        st.info("当前场景没有 NPC。")

left, right = st.columns([1, 1])
with left:
    st.subheader("NPC")
    agent_id = st.selectbox("选择角色", nearby_agents or ["无可互动 NPC"])
    st.subheader("调查")
    scene_claims = [claim for claim in game.claims if claim.get("scene") == snapshot["current_scene"]]
    claim_id = st.selectbox("验证当前场景线索", [claim["claim_id"] for claim in scene_claims] or ["无可调查线索"])
    if st.button("调查线索"):
        result = game.investigate(claim_id) if scene_claims else {"valid": False, "impact": "当前场景暂无可调查线索。"}
        if result.get("valid"):
            st.success(f"已验证：{result['claim_id']}，真值：{result['truth']}")
        else:
            st.warning(result["impact"])

with right:
    st.subheader("对话")
    question = st.chat_input("输入你想问 NPC 的问题")
    if question:
        response = game.ask(agent_id, question)
        st.chat_message("user").write(question)
        st.chat_message("assistant").write(response["dialogue"])
        if developer_mode:
            st.json(response)

    if developer_mode:
        st.subheader("GameState")
        st.json(game.snapshot())
