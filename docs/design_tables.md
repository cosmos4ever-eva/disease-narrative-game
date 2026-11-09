# 多智能体疫病推理游戏设计表

本项目是一个由多个 NPC Agent 驱动的悬疑推理游戏。每个 NPC 都拥有独立人格、长期记忆、私密信息、关系状态和行动目标。NPC Agent 负责根据玩家行为生成个性化对话与行动；规则引擎负责感染状态、客观线索、时间推进和结局判定。

## 0. 核心设计边界

| 模块 | 负责内容 | Agent 是否可自由决定 |
|---|---|---|
| 人格层 | 语气、表达习惯、情绪表现、行为倾向 | 允许，但受角色配置约束 |
| 记忆层 | 记录事件、更新关系、检索相关经历 | 可生成摘要，但不能篡改事实来源 |
| 决策层 | 是否回答、隐瞒、转移话题、请求帮助、移动 | 只能从行动白名单中选择 |
| 对话层 | 将允许表达的信息组织成自然语言 | 允许 |
| 世界状态层 | 感染状态、Claim 真值、物品、时间、结局 | 不允许，必须由规则引擎决定 |
| 事件层 | 传播、升级、场景事件、结局 | 不允许，必须由规则引擎触发 |

基本原则：**Agent 可以拥有错误认知，但不能修改客观真相；Agent 可以改变调查路径，但不能绕过规则直接结束游戏。**

## 一、NPC Agent 表

### 1.1 Agent 稳定配置

| agent_id | 角色 | 初始场景 | 性格约束 | 核心目标 | 私密信息 | 初始感染 | 可观察表现 |
|---|---|---|---|---|---|---|---|
| agent_wilson | Wilson | camp | 理性、好奇、重视证据，但容易高估判断 | 找到感染机制并证明自己的判断 | 发现过异常孢子，但以为只是普通霉菌 | 未感染 | 记录本凌乱、反复查看样本 |
| agent_willow | Willow | forest_edge | 冲动、叛逆、讨厌被审问，用挑衅掩饰恐惧 | 隐藏纵火行为，同时确认自己是否被感染 | 烧掉过发光藤蔓，可能破坏了证据 | 潜伏感染 | 手套有黑灰、偶尔发热和咳嗽 |
| agent_wendy | Wendy | graveyard | 冷静、悲观、观察细致，说话含蓄 | 保护 Abigail 的秘密，并提醒玩家注意源头 | 见过 Abigail 接近暗影遗物后的异常反应 | 未感染 | 低声自语、提到“影子在呼吸” |
| agent_wolfgang | Wolfgang | camp | 直接、胆小、重视力量，害怕超自然现象 | 活下来，并避免独自面对遗迹 | 看到有人从 ruins_path 带回黑色石匣，但没看清是谁 | 未感染 | 紧张发抖、不愿独自去遗迹 |
| agent_maxwell | Maxwell | ruins_path | 优雅、操控欲强、擅长选择性表达 | 隐藏接触史，掌控调查方向，寻找解除感染的方法 | 最先接触暗影遗物，知道疫病与遗物有关 | 潜伏感染 | 声音偶尔失真、影子动作慢半拍 |

### 1.2 Agent 动态状态

| 字段 | 含义 | 示例 |
|---|---|---|
| trust_to_player | 对玩家的信任度，0-100 | 55 |
| fear | 当前恐惧程度，0-100 | 40 |
| suspicion_to_others | 对其他 NPC 的怀疑值 | `agent_maxwell: 75` |
| current_goal | 当前优先目标 | `hide_contact_history` |
| current_scene | 当前所在场景 | `camp` |
| infection_state | 真实感染状态 | `latent` |
| perceived_infection | Agent 主观认为谁感染 | `agent_willow` |
| available_actions | 当前允许选择的行动 | `answer`, `evade`, `move` |
| last_memory_update | 最近一次记忆更新时间 | `day_1_tick_3` |

### 1.3 Agent 记忆表

长期记忆不是完整聊天记录，而是可检索、可更新的结构化记忆。

| memory_id | owner_agent | 类型 | 内容 | 来源 | 可信度 | 重要性 | 可见范围 | 更新条件 |
|---|---|---|---|---|---:|---:|---|---|
| mem_wilson_001 | agent_wilson | 事件 | 我在 camp 发现了黑色孢子 | 直接观察 | 0.95 | 0.90 | private | 调查实验台后强化 |
| mem_willow_001 | agent_willow | 事件 | 我在 forest_edge 烧掉了发光藤蔓 | 自身行动 | 1.00 | 0.95 | private | 被证据逼问时激活 |
| mem_wendy_001 | agent_wendy | 事件 | Abigail 靠近石匣后表现异常 | 目击 | 0.80 | 0.90 | private | 玩家建立信任后可透露 |
| mem_wolfgang_001 | agent_wolfgang | 传闻 | 有人从遗迹带回了黑色石匣 | 部分观察 | 0.60 | 0.75 | private | 被鼓励回忆时可能修正 |
| mem_maxwell_001 | agent_maxwell | 秘密 | 我最先触碰了黑色遗物 | 自身行动 | 1.00 | 1.00 | private | 高压力或最终质问时激活 |

记忆对象建议使用以下结构：

```json
{
  "memory_id": "mem_maxwell_001",
  "owner_agent": "agent_maxwell",
  "type": "episodic",
  "content": "我最先触碰了黑色遗物",
  "source": "self_action",
  "event_time": 0,
  "importance": 1.0,
  "confidence": 1.0,
  "visibility": "private",
  "emotional_tag": "fear",
  "decay_rate": 0.0,
  "conflicts_with": [],
  "retrieval_tags": ["shadow_box", "ruins_path", "infection_source"]
}
```

### 1.4 Agent 关系表

关系是动态记忆的一部分，不是固定的 NPC 介绍文字。

| owner_agent | target | 初始关系 | 初始信任 | 关系变化原因 | 对话影响 |
|---|---|---|---:|---|---|
| agent_wilson | agent_maxwell | 怀疑 | 30 | 发现其样本与遗迹有关 | 更容易追问 Maxwell |
| agent_wilson | agent_wendy | 尊重 | 65 | Wendy 提供细致观察 | 更愿意分享实验结果 |
| agent_willow | agent_wolfgang | 冲突 | 25 | Wolfgang 目击过她离开营地 | 容易互相指责 |
| agent_wendy | agent_maxwell | 警惕 | 35 | 感知到他的影子异常 | 只提供隐喻信息 |
| agent_wolfgang | agent_maxwell | 受影响 | 50 | Maxwell 主动安抚并引导他 | 容易重复 Maxwell 的判断 |
| agent_maxwell | agent_willow | 利用 | 20 | Willow 的纵火行为适合作为替罪羊 | 主动把嫌疑引向 Willow |

## 二、Claim 表

Claim 是规则系统中的客观事实单元。Agent 可以知道、误解、隐瞒或错误传播 Claim，但不能改变 Claim 的真值。

| claim_id | 命题内容 | 客观真值 | 来源 | Agent 可持有的认知 | 验证方式 | 验证后影响 |
|---|---|---|---|---|---|---|
| claim_001 | 昨晚有人从遗迹小路带回了黑色石匣 | 真 | Wolfgang | 只记得模糊身影 | 检查脚印与拖痕 | 解锁追踪石匣 |
| claim_002 | Willow 昨晚没有离开营地 | 假 | Willow | 明知是假，但会回避 | 检查烧焦藤蔓与灰烬 | 解锁追问纵火 |
| claim_003 | 发光藤蔓被火烧过 | 真 | 场景物品 | 可通过调查确认 | 调查 forest_edge | 证明 Willow 到过现场 |
| claim_004 | Wilson 的样本里有黑色孢子 | 真 | 实验台 | Wilson 初始低估危险性 | 检查实验台 | 修正感染认知 |
| claim_005 | Wendy 听到 Abigail 提到“会呼吸的石头” | 真 | Wendy | 会使用隐喻表达 | 高信任对话或检查墓地 | 指向暗影遗物 |
| claim_006 | Maxwell 从未碰过黑色石匣 | 假 | Maxwell | 会主动否认 | 检查手套纤维与石匣残留 | 解锁最终质问 |
| claim_007 | 感染只会在确认感染者附近传播 | 假 | Wilson 初步判断 | Wilson 的错误假设 | 等待一轮观察传播 | 修正传播认知 |
| claim_008 | 潜伏感染者也可能传播疫病 | 真 | 感染规则 | NPC 可逐渐推断 | 对比时间线和症状 | 获得关键机制线索 |
| claim_009 | Willow 烧毁藤蔓是为了掩盖去过现场 | 半真 | Willow | 知道动机但会淡化 | 温和追问并验证 claim_003 | 说明她不是源头 |
| claim_010 | 石匣最早出现在 ruins_path 的裂缝旁 | 真 | 场景物品 | Maxwell 会回避 | 调查遗迹裂缝 | 解锁源头判定 |
| claim_011 | 墓地冷斑出现在石匣被带回之后 | 真 | Wendy/场景 | Wendy 可建立时间线 | 检查墓地冷斑 | 建立传播时间线 |
| claim_012 | 封存石匣可阻断新增感染，但不能治愈已感染者 | 真 | 规则系统 | NPC 只能推测或误解 | 验证封存条件 | 决定结局 |

## 三、Agent 行动与对话表

Agent 每次只能从允许动作中选择。行动由记忆、目标、关系和世界状态共同影响。

| action_id | 行动 | 适用条件 | 可能结果 | 是否写入记忆 |
|---|---|---|---|---|
| action_answer | 直接回答 | 信任足够且问题未触及核心秘密 | 输出与已知 Claim 一致的回答 | 记录玩家提问 |
| action_evade | 回避问题 | 信任低或问题涉及秘密 | 转移话题、给出模糊答案 | 记录玩家正在调查该秘密 |
| action_lie | 提供误导信息 | 存在可用误导 Claim 且目标允许 | 传播错误或半真信息 | 记录一次欺骗行为 |
| action_reveal | 主动透露线索 | 信任高、压力高或目标变化 | 暴露一条可验证 Claim | 强化玩家相关记忆 |
| action_accuse | 指控其他 NPC | 怀疑值高且有引用记忆 | 改变玩家调查方向 | 记录指控来源 |
| action_request_help | 请求玩家帮助 | 恐惧高或目标受阻 | 生成支线或交换信息 | 增加对玩家依赖 |
| action_move | 移动到其他场景 | 规则允许且当前目标需要 | 改变接触与传播关系 | 记录移动原因 |
| action_hide_evidence | 隐藏或转移物品 | 拥有物品且目标允许 | 物品位置变化，由规则系统记录 | 记录秘密行动 |
| action_confess | 承认部分事实 | 压力达到阈值或关键证据出现 | 只承认允许揭示的内容 | 更新恐惧、羞耻或信任记忆 |

对话生成流程：

```text
当前世界状态
    -> 检索相关长期记忆
    -> 判断当前目标与关系
    -> 选择允许行动
    -> 获取该行动允许表达的 Claim
    -> 生成符合人格的台词
    -> 写入本轮事件记忆
```

模型不能直接编造新线索、新感染状态、新角色或新结局。

## 四、Event 表

事件由规则引擎触发；Agent 可以对事件作出反应，但不能自行触发需要规则判定的事件。

| event_id | 事件名 | 触发条件 | Agent 反应 | 状态变化 | 后续解锁 |
|---|---|---|---|---|---|
| event_001 | 营地出现第一名病人 | 游戏开始 | Wilson 调查，Willow/Maxwell 隐藏异常 | 时间为 day=1, tick=0 | 初始问话与场景选择 |
| event_002 | 检查烧焦藤蔓 | 访问 forest_edge 并调查 | Willow 回避、反击或部分承认 | claim_003 证实 | 追问 Willow |
| event_003 | Wilson 发现孢子异常 | claim_004 证实 | Wilson 更新认知并提高恐惧 | 感染机制线索增加 | 观察传播 |
| event_004 | Wendy 提到会呼吸的石头 | 信任达到 55 或 claim_011 证实 | Wendy 选择隐喻透露 | claim_005 可验证 | 调查遗物 |
| event_005 | 追问 Willow 纵火 | claim_002 被证伪且与 Willow 对话 | 根据玩家态度改变信任 | claim_009 解锁 | 排除 Willow 为源头 |
| event_006 | Wolfgang 恐惧升级 | tick >= 3 且恐惧高 | 夸大、求助或重复他人说法 | 新增误导信息 | 提醒玩家核查来源 |
| event_007 | 感染扩散 | 每经过 2 tick | 感染者隐藏症状或改变目标 | 传播规则执行 | 坏结局倒计时 |
| event_008 | 找到黑色石匣 | claim_001 与 claim_010 均证实 | Maxwell 否认、转移或部分承认 | 石匣加入已发现列表 | 最终质问 |
| event_009 | 质问 Maxwell | 石匣已发现且 claim_006 被证伪 | 根据压力和记忆选择承认或操控 | 关系与秘密更新 | 进入结局判定 |

## 五、感染规则表

感染状态是真实世界状态，只能由规则引擎更新。Agent 只能通过症状、行为和记忆表现感染状态。

| rule_id | 规则名 | 条件 | 结果 | Agent 表现 |
|---|---|---|---|---|
| inf_001 | 源头污染 | 接触石匣或遗迹裂缝且无防护 | 进入潜伏感染 | 耳鸣、失神、记忆检索异常 |
| inf_002 | 同场景暴露 | 与潜伏/确认感染者同场景累计 2 tick | 进入潜伏感染 | 对话停顿、轻微咳嗽 |
| inf_003 | 潜伏转确认 | latent_ticks >= 3 | 进入确认感染 | 语言重复、影子异常、目标改变 |
| inf_004 | 潜伏传播 | 潜伏感染者与未感染者同场景 | exposure_count +1 | 症状弱，不等于确诊 |
| inf_005 | 确认传播 | 确认感染者与未感染者同场景 | exposure_count +2 | 症状明显、主动隐藏或攻击性提高 |
| inf_006 | 场景残留污染 | 源头未封存时调查遗迹或森林边缘 | 调查者 exposure_count +1 | 场景记忆出现黑色孢子 |
| inf_007 | 简易隔离 | 玩家将 NPC 移到 isolated_camp | 停止同场景传播，但病程继续 | 被隔离者信任下降或求助 |
| inf_008 | 封存源头 | 石匣已发现且选择封存 | 停止源头与场景污染 | 已感染者不会自动痊愈 |
| inf_009 | 错误处理源头 | 未验证条件就直接烧毁石匣 | 同场景 NPC 暴露增加 | Agent 记住玩家的鲁莽行为 |
| inf_010 | 终局判定 | 每个 tick 结束后检查状态 | 进入对应结局 | 所有 Agent 生成终局反应 |

## 六、结局表

| ending_id | 结局 | 条件 | Agent 层表现 |
|---|---|---|---|
| ending_good | 封存源头 | 找到石匣，验证 claim_012，确认感染人数 <= 1 | 幸存者根据长期记忆对玩家产生不同评价 |
| ending_wrong_accuse | 误判结局 | 指认非源头角色并驱逐，源头未处理 | 被冤枉者记住玩家选择，感染继续扩散 |
| ending_bad | 全员感染 | 所有 NPC 潜伏/确认感染，或 tick >= 8 且源头未处理 | 所有 Agent 的语言与目标逐渐趋同 |

## 七、推荐数据文件

| 文件 | 内容 |
|---|---|
| `data/agents.json` | Agent 稳定配置：人格、目标、秘密、初始场景、行动策略 |
| `data/memories.json` | NPC 初始记忆、记忆类型、来源、可信度、可见范围 |
| `data/relationships.json` | NPC-NPC 与 NPC-玩家关系初始值及变化规则 |
| `data/claims.json` | 客观命题、真值、来源、验证方式和影响 |
| `data/actions.json` | Agent 行动白名单、适用条件和结果 |
| `data/events.json` | 规则事件、触发条件、状态变化和 Agent 反应 |
| `data/infection_rules.json` | 感染状态转换、传播阈值和场景污染 |
| `saves/state.json` | 当前时间、NPC 状态、记忆更新、Claim 验证状态和物品状态 |

## 八、第一版 Agent MVP 验收标准

1. 玩家连续两次询问同一个 NPC 时，NPC 能读取上一轮记忆并改变语气或信息策略。
2. 玩家帮助、怀疑或欺骗 NPC 后，该 NPC 的信任度和后续行动会发生变化。
3. 不同 NPC 对同一个客观事件可以持有不同认知，但最终真值由 Claim 和规则系统统一管理。
4. NPC 可以回避、撒谎、透露、指控或请求帮助，但只能选择行动白名单中的动作。
5. 结束游戏后，可以查看每个 NPC 的关键记忆、关系变化和行动原因。
6. 同一案件重复运行时，核心真相不变，但对话、关系和调查路径可以不同。
