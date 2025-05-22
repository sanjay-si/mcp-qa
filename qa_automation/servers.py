from __future__ import annotations

import os
import shutil
from contextlib import asynccontextmanager
from agents.mcp import MCPServerStdio


@asynccontextmanager
async def filesystem_server(samples_dir: str):
    """Context manager for the filesystem MCP server."""
    server = MCPServerStdio(
        name="Filesystem Server",
        params={
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
        },
        cache_tools_list=True,
    )
    try:
        async with server as fs:
            yield fs
    finally:
        pass


@asynccontextmanager
async def playwright_server():
    """Context manager for the Playwright MCP server."""
    server = MCPServerStdio(
        name="Playwright Server",
        params={
            "command": "npx",
            "args": ["-y", "@executeautomation/playwright-mcp-server"],
        },
        cache_tools_list=True,
    )
    try:
        async with server as ps:
            yield ps
    finally:
        pass

