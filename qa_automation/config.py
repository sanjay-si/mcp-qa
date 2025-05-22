from __future__ import annotations

import os
from dotenv import load_dotenv
from openai import AsyncAzureOpenAI
from agents import set_default_openai_client, set_tracing_disabled

load_dotenv()

AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_MODEL")


def configure_openai_client() -> AsyncAzureOpenAI:
    """Create and register the default OpenAI client."""
    client = AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_version=AZURE_OPENAI_API_VERSION,
    )
    set_default_openai_client(client)
    set_tracing_disabled(disabled=True)
    return client
