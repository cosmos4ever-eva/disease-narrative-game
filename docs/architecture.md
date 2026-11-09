# 游戏开发框架

```text
Streamlit 前端
    -> Game API / Game Session
    -> Workflow Orchestrator
    -> 规则引擎：时间、感染、Claim、事件、结局
    -> NPC Agent Runtime：记忆、关系、目标、行动、对话
    -> JSON 数据与单局存档
```

## 运行边界

- 规则引擎拥有客观真相和状态写权限。
- Agent 只能选择白名单行动，并生成符合人格的表达。
- Mock Agent 是默认实现，真实 LLM 通过适配器接入。
- 每局使用固定 seed，便于调试和回放。

## MVP 运行回路

```text
玩家主要行动
 -> 校验行动
 -> 修改 GameState
 -> 触发 Claim/Event
 -> 推进 Tick
 -> 执行感染传播
 -> 调度受影响 Agent
 -> 检索记忆并选择行动
 -> 生成对话
 -> 写入记忆与日志
 -> 返回前端
```
