from agents import (
    Agent,
    Runner,
    set_default_openai_client,
    OpenAIChatCompletionsModel,
    AnthropicMessagesModel,
    GoogleGenerativeAIChatModel,
    set_tracing_disabled,
)
from agents.mcp import MCPServer, MCPServerStdio
import os
import shutil
from dotenv import load_dotenv
import asyncio
import sys
import warnings
import atexit

warnings.filterwarnings("ignore", category=ResourceWarning)

# Optionally silence stderr during shutdown
original_stderr = sys.stderr

def silence_stderr_on_exit():
    sys.stderr = open(os.devnull, 'w')

atexit.register(silence_stderr_on_exit)

load_dotenv()

# Load environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Model selection
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "azure").lower()


def get_model():
    """Initialize the LLM model based on MODEL_PROVIDER."""

    if MODEL_PROVIDER == "azure":
        from openai import AsyncAzureOpenAI

        client = AsyncAzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_version=AZURE_OPENAI_API_VERSION,
        )
        set_default_openai_client(client)
        return OpenAIChatCompletionsModel(
            model=AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL,
            openai_client=client,
        )

    if MODEL_PROVIDER == "openai":
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        set_default_openai_client(client)
        return OpenAIChatCompletionsModel(
            model=os.getenv("OPENAI_MODEL"),
            openai_client=client,
        )

    if MODEL_PROVIDER == "claude":
        from anthropic import AsyncAnthropic

        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return AnthropicMessagesModel(
            model=os.getenv("CLAUDE_MODEL"),
            anthropic_client=client,
        )

    if MODEL_PROVIDER == "deepseek":
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL"),
        )
        set_default_openai_client(client)
        return OpenAIChatCompletionsModel(
            model=os.getenv("DEEPSEEK_MODEL"),
            openai_client=client,
        )

    if MODEL_PROVIDER == "gemini":
        import google.generativeai as genai

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        return GoogleGenerativeAIChatModel(
            model=os.getenv("GEMINI_MODEL"),
        )

    raise ValueError(f"Unsupported MODEL_PROVIDER: {MODEL_PROVIDER}")


# Disable tracing
set_tracing_disabled(disabled=True)

async def run_agent_with_servers(file_server: MCPServer, automation_server: MCPServer) -> None:
    """Run the agent with the MCP server"""
    
    # Read instructions from file
    instructions_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agent_instructions_v2.txt")
    with open(instructions_path, "r") as f:
        instructions = f.read()
    
    agent = Agent(
        name="Automation Agent",
        instructions=instructions,
        mcp_servers=[file_server, automation_server],
        model=get_model(),
    )

    result = await Runner.run(
        starting_agent=agent, 
        input="Can you do the automation testing of this web page: https://demo.playwright.dev/todomvc/",
        max_turns=100
    )
    print(f"Agent execution completed with result: {result.final_output}")

    """Example using the MCP Playwrite server (stdio-based)"""
    print("\n======= MCP PLAYWRITE SERVER INIT =======")

    try:
        # Initialize the automation server
        async with MCPServerStdio(
            name="Playwrite Server",
            params={
                "command": "npx",
                "args": ["-y", "@executeautomation/playwright-mcp-server"]
            },
            cache_tools_list=True
        ) as automation_server:
            tools = await automation_server.list_tools()
            print(f"Available automation server tools: {[tool.name for tool in tools]}")
        
        return automation_server
    except Exception as e:
        print(f"Error: {e}")
        return None

async def main():
    """Main function to run the agent"""
    print("Open AI Agents SDK with MCP Support - Automation Testing Agent Use Case")

    # Check for npm/npx installation
    if not shutil.which("npm") or not shutil.which("npx"):
        print("Error: npm/npx is not installed. Please install it and try again.")
        return
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    samples_dir = os.path.join(current_dir, "fs_files")
    os.makedirs(samples_dir, exist_ok=True)
    
    try:
        # Initialize both servers and keep them open while we use them
        async with MCPServerStdio(
            name="Filesystem Server",
            params={
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", samples_dir],
            },
            cache_tools_list=True
        ) as file_server, MCPServerStdio(
            name="Playwrite Server",
            params={
                "command": "npx",
                "args": ["-y", "@executeautomation/playwright-mcp-server"]
            },
            cache_tools_list=True
        ) as automation_server:
            
            # List the tools for both servers
            file_tools = await file_server.list_tools()
            print(f"\n======= MCP FILE SERVER INIT =======\nAvailable file server tools: {[tool.name for tool in file_tools]}")
            
            auto_tools = await automation_server.list_tools()
            print(f"\n======= MCP PLAYWRITE SERVER INIT =======\nAvailable automation server tools: {[tool.name for tool in auto_tools]}")
            
            # Run the agent with both servers while they're still open
            await run_agent_with_servers(file_server, automation_server)
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
