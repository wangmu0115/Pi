from dataclasses import dataclass
from typing import Literal

from miniagent import Answer, Environment, Message, Model

SYSTEM_PROMPT = """1"""


@dataclass
class RunResult:
    status: Literal["finished", "step_limit"]
    summary: str
    steps: int
    messages: list[Message]


class Agent:
    def __init__(self, model: Model, env: Environment, *, max_steps: int = 5):
        if max_steps < 1:
            raise ValueError("The iterations for Agent Loop must greater than 0.")
        self._max_steps = max_steps
        self._model = model
        self._env = env

    def run(self, task: str) -> RunResult:
        # conversation history
        messages = [Message("system", SYSTEM_PROMPT), Message("user", task)]
        for step in range(1, self._max_steps + 1):
            # 调用语言模型，获取下一步行动
            action = self._model.query(messages)
            messages.append(Message("assistant", action))  # append message to history
            if isinstance(action, Answer):  # 任务完成，退出 agent loop
                return RunResult("finished", action.summary, step, messages)
            # 执行动作，返回观测
            observation = self._env.execute(action)
            messages.append(Message("user", observation))  # append message to history
        # 达到循环上限
        return RunResult(
            "step_limit",
            "达到 Agent Loop 上限，任务未完成。",
            self._max_steps,
            messages,
        )
