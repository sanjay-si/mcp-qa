from __future__ import annotations

import asyncio
from pathlib import Path
from agents import Agent, Runner, OpenAIChatCompletionsModel

MODEL_NAME = "gpt-3.5-turbo"  # Default or configurable elsewhere


def build_agent(instructions: str, file_server, automation_server, client) -> Agent:
    return Agent(
        name="Automation Agent",
        instructions=instructions,
        mcp_servers=[file_server, automation_server],
        model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    )


async def run_agent(file_server, automation_server, client) -> None:
    instructions_path = Path(__file__).parent / "instructions" / "agent_instructions_v2.txt"
    instructions = instructions_path.read_text()

    agent = build_agent(instructions, file_server, automation_server, client)

    result = await Runner.run(
        starting_agent=agent,
        # input="Got the web page https://demo.playwright.dev/todomvc/, create two tasks and close the browser",
        # input="Book a flight from New Delhi to Ahmedabad using https://www.skyscanner.co.in/",
        input="goto http://hrberry.com/smarthr/index.php?q=cms&m=index&client=atmecs, login using a userid & password as '10' and 'wvJyR*mcn$XT67Y'. Then goto leave approval menu.",
        max_turns=100,
    )
    print(f"Agent execution completed with result: {result.final_output}")

