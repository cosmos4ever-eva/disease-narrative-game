# Godot Frontend

这是正式游戏前端的 Godot 4 项目，后端仍由项目根目录的 FastAPI 提供。

## 运行

1. 安装 Godot 4.x。
2. 在项目根目录启动后端：

```powershell
uvicorn backend.main:app --host 127.0.0.1 --port 8010
```

3. 在 Godot 中导入 `godot/project.godot` 并运行项目。

当前版本已经实现：

- 场景卡片和当前场景高亮
- 通过后端读取 GameState
- 点击场景移动
- 移动消耗行动力

后续会接入场景背景图、NPC 立绘、调查物品和 Agent 对话。
