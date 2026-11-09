from dataclasses import dataclass, field
from typing import Any


@dataclass
class Memory:
    memory_id: str
    content: str
    memory_type: str = "event"
    source: str = "system"
    importance: float = 0.5
    confidence: float = 0.5
    tags: list[str] = field(default_factory=list)


class MemoryManager:
    def __init__(self, memories: list[dict[str, Any]] | None = None):
        self.memories = [Memory(**item) for item in (memories or [])]

    def retrieve(self, query: str, limit: int = 3) -> list[Memory]:
        terms = set(query.lower().split())
        scored = []
        for memory in self.memories:
            haystack = f"{memory.content} {' '.join(memory.tags)}".lower()
            score = sum(term in haystack for term in terms) + memory.importance
            scored.append((score, memory))
        return [memory for _, memory in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]

    def add(self, memory: Memory) -> None:
        self.memories.append(memory)
