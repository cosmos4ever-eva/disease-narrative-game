import streamlit as st

from backend.engine.game import Game


@st.cache_resource
def get_game() -> Game:
    return Game(seed=7)


game = get_game()
st.set_page_config(page_title="疫病推理游戏", layout="wide")
st.title("疫病推理游戏 · Agent MVP")

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

left, right = st.columns([1, 2])
with left:
    st.subheader("NPC")
    agent_id = st.selectbox("选择角色", list(game.agents.keys()))
    st.subheader("调查")
    claim_id = st.selectbox("验证 Claim", [claim["claim_id"] for claim in game.claims])
    if st.button("调查线索"):
        result = game.investigate(claim_id)
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
