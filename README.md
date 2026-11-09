# Disease Narrative Game

多智能体悬疑疫病推理游戏的可运行 MVP。

## 已实现

- 规则驱动的 GameState、时间推进、Claim 验证和感染传播
- NPC Agent 的人格、目标、关系、有限行动和单局记忆
- Mock Agent 默认运行，不需要 API Key
- FastAPI 后端接口
- Streamlit 前端：玩家模式和开发者模式
- JSON 数据与 JSON 存档
- 固定随机种子和基础 pytest 测试

## 启动

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run frontend/app.py
```

后端 API 可单独启动：

```powershell
uvicorn backend.main:app --reload
```

## 项目边界

Mock Agent 负责演示记忆、关系和行动流程。真实 LLM 适配器尚未接入；后续可以在 `backend/agents/` 中新增 Provider，而不改变规则内核。
