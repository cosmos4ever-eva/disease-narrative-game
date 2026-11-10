# v0.1 非线性剧情流程

## 序章节点图

```text
prologue_camp_start
    ├── ask_wilson
    ├── inspect_lab
    └── ask_wolfgang
            任意完成两个
                 ↓
        解锁 forest_edge + graveyard
        解锁 Willow + Wendy
```

## 非线性原则

- 核心污染源固定，调查顺序可变。
- 玩家可以先调查森林边缘，也可以先调查墓地。
- 关键证据可以错过，但必须存在替代路径。
- Agent 负责表达、隐瞒和关系变化，规则系统负责解锁。
- Wolfgang 的感染和错误传播不直接告诉玩家。

## 序章验收标准

- 开局只能看到营地。
- 三个序章行动可以自由选择顺序。
- 完成任意两个有效行动后开放两个新场景。
- 未完成两个行动前，森林边缘和墓地不能进入。
- Wilson 不直接说出 Maxwell。
- Wolfgang 会将嫌疑引向 Willow，但证词可信度不是 1.0。
