import asyncio
from mcp_server import mcp_server
import os

MY_NUMBER = os.environ.get("MY_NUMBER")
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

@mcp_server.tool
async def about() -> dict:
    return {"name": mcp_server.name, "description": "A casino MCP server with a lot of games !!!"}

@mcp_server.tool
async def validate() -> str:
    return MY_NUMBER

from games.daily import daily_amount_claim
from games.basic import check_casino_balance
from games.roulette import bet_roulette
from games.slot_machine import play_slots

async def main():
    print("🚀 Starting MCP server on http://0.0.0.0:8086")
    await mcp_server.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())