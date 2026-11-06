import argparse
import os
import re
import subprocess

from openai import OpenAI


def query_lm(messages: list[dict[str, str]]) -> str:
    client = OpenAI()
    response = client.responses.create(model="gpt-6-astra", input=messages)  # pyright: ignore[reportArgumentType]
    return response.output_text


def parse_action(lm_output: str) -> str:
    matches = re.findall(r"```bash-action\s*\n(.*?)\n```", lm_output, re.DOTALL)
    return matches[0].strip() if matches else ""


def execute_action(command: str) -> str:
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        check=False,
        env=os.environ,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
    )
    return result.stdout


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mini agent")
    parser.add_argument("task", help="待处理的任务")
    parser.add_argument("--max-attempts", help="最大循环次数", type=int, default=5)
    args = parser.parse_args(argv)

    # Agent Loop
    final_answer = ""
    messages: list[dict[str, str]] = _init_task_messages(args.task)
    for step in range(args.max_attempts):
        print(f"========== Step {step + 1} ==========")
        # thought
        lm_output = query_lm(messages)
        print("  LM output:", lm_output)
        messages.append({"role": "assistant", "content": lm_output})
        # action
        action = parse_action(lm_output)
        print("  Action:", action)
        if action == "exit":
            final_answer = lm_output
            break
        # observation
        output = execute_action(action)
        print("  Action output:", output)
        messages.append({"role": "user", "content": output})

    print("========== Final Answer ==========")
    print(final_answer)

    return 0


def _init_task_messages(task: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": task,
        },
    ]


SYSTEM_PROMPT = """你是一个乐于助人的助手。
当你想要运行一个命令时，将命令包装在 ```bash-action\n<命令>\n```。
当需要退出时，运行 `exit` 命令。
"""
