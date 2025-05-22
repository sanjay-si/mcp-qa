from __future__ import annotations

import asyncio
from pathlib import Path
from agents import Agent, Runner, OpenAIChatCompletionsModel

from .config import AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL


def build_agent(instructions: str, file_server, automation_server, client) -> Agent:
    return Agent(
        name="Automation Agent",
        instructions=instructions,
        mcp_servers=[file_server, automation_server],
        model=OpenAIChatCompletionsModel(model=AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL, openai_client=client),
    )


async def run_agent(file_server, automation_server, client) -> None:
    instructions_path = Path(__file__).parent / "instructions" / "agent_instructions_v2.txt"
    instructions = instructions_path.read_text()

    agent = build_agent(instructions, file_server, automation_server, client)

    result = await Runner.run(
        starting_agent=agent,
        input="Can you do the automation testing of this web page: https://demo.playwright.dev/todomvc/",
        max_turns=100,
    )
    print(f"Agent execution completed with result: {result.final_output}")

