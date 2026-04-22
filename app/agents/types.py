from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentTask:
    kind: str
    payload: dict[str, Any] = field(default_factory=dict)
    requested_by: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_input(
        cls,
        kind: str,
        payload: dict[str, Any] | None = None,
        requested_by: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> "AgentTask":
        return cls(
            kind=str(kind).strip(),
            payload=dict(payload or {}),
            requested_by=requested_by,
            metadata=dict(metadata or {}),
        )


@dataclass(frozen=True)
class AgentStepResult:
    agent_name: str
    task_kind: str
    status: str
    summary: str
    artifacts: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AgentRunResult:
    task_kind: str
    status: str
    route: list[str]
    steps: list[AgentStepResult]
    summary: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["steps"] = [step.to_dict() for step in self.steps]
        return payload
