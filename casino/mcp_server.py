from dotenv import load_dotenv
import os
from fastmcp import FastMCP
from common import SimpleBearerAuthProvider
import asyncio

load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"

mcp_server = FastMCP(
    "Job Finder MCP Server",
    auth=SimpleBearerAuthProvider(TOKEN),
)