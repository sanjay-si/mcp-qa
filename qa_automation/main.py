from __future__ import annotations

import asyncio
import os
import shutil
from pathlib import Path
from openai import AsyncOpenAI

from .servers import filesystem_server, playwright_server
from .agent_runner import run_agent


async def check_prerequisites() -> bool:
    return bool(shutil.which("npm") and shutil.which("npx"))


async def main() -> None:
    print("OpenAI Agents SDK with MCP Support - Automation Testing Agent Use Case")

    if not await check_prerequisites():
        print("Error: npm/npx is not installed. Please install it and try again.")
        return

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    samples_dir = Path(__file__).parent / "fs_files"
    samples_dir.mkdir(exist_ok=True)

    async with filesystem_server(str(samples_dir)) as file_server, playwright_server() as automation_server:
        file_tools = await file_server.list_tools()
        print("\n======= MCP FILE SERVER INIT =======")
        print(f"Available file server tools: {[tool.name for tool in file_tools]}")

        auto_tools = await automation_server.list_tools()
        print("\n======= MCP PLAYWRIGHT SERVER INIT =======")
        print(f"Available automation server tools: {[tool.name for tool in auto_tools]}")

        await run_agent(file_server, automation_server, client)


if __name__ == "__main__":
    asyncio.run(main())

