from typing import Any

from .memory import Memory, MemoryManager


class MockNPCAgent:
    """Deterministic Agent shell; a real LLM provider can replace this class later."""

    def __init__(self, config: dict[str, Any], memories: list[dict[str, Any]] | None = None):
        self.config = config
        self.memory = MemoryManager(memories)

    def respond(self, player_text: str, state: dict[str, Any]) -> dict[str, Any]:
        trust = state.get("trust_to_player", self.config.get("initial_trust", 50))
        secret = self.config.get("secret", "")
        lower = player_text.lower()
        relevant = self.memory.retrieve(player_text)
        if self.config["agent_id"] == "agent_maxwell" and any(word in lower for word in ("石匣", "遗物", "maxwell")):
            action = "evade" if trust < 70 else "reveal"
            dialogue = "你把注意力放在石匣上，或许是因为你已经找到了更值得怀疑的人。"
        elif secret and any(word in lower for word in ("感染", "孢子", "遗迹", "秘密")):
            action = "evade"
            dialogue = "我知道一些事情，但现在还不是全部说出来的时候。"
        else:
            action = "answer"
            dialogue = f"我会记住你问过这个问题。关于{self.config['name']}，目前我只能告诉你：先核对现场证据。"
        self.memory.add(Memory(
            memory_id=f"turn_{len(self.memory.memories) + 1}",
            content=f"玩家询问：{player_text}",
            source="player_action",
            importance=0.4,
            confidence=1.0,
            tags=["player", action],
        ))
        return {"action": action, "dialogue": dialogue, "retrieved_memories": [m.content for m in relevant]}
