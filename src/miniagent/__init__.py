from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, Protocol


@dataclass(frozen=True)
class Command:
    command: str


@dataclass(frozen=True)
class Answer:
    summary: str


@dataclass(frozen=True)
class Observation:
    output: str
    returncode: int
    timed_out: bool = False


@dataclass(frozen=True)
class Message:
    role: Literal["system", "user", "assistant"]
    content: str | Command | Answer | Observation


class Model(Protocol):
    def query(self, messages: Sequence[Message]) -> Command | Answer: ...


class Environment(Protocol):
    def execute(self, action: Command) -> Observation: ...
