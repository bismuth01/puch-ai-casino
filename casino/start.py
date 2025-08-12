import asyncio
from mcp_server import mcp_server
import os

MY_NUMBER = os.environ.get("MY_NUMBER")
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

@mcp_server.tool()
async def about() -> str:
    return (
        "🎰 **Welcome to the Puch AI Casino!** 🃏\n\n"
        "Here, you can enjoy fun, interactive casino games and build your virtual fortune!\n\n"
        "💵 **Start Here:**\n"
        "• Use `daily_amount_claim` to collect your free **1000 rupees** every 24 hours.\n"
        "• Use `hourly_amount_claim` to collect your free **100 rupees** every hour.\n"
        "These are the easiest ways to build your balance quickly.\n\n"
        "🎮 **Games You Can Play:**\n"
        "• Roulette – Bet on numbers, colors, or combinations.\n"
        "• Slot Machine – Spin the reels and see if luck is on your side.\n"
        "• Blackjack – Play against the dealer and try to hit 21.\n\n"
        "🏆 **Compete & Climb the Leaderboard:**\n"
        "• Check your ranking based on your current balance.\n"
        "• Compete for the top spot against other players.\n\n"
        "💡 **Tip:** Start by claiming your hourly and daily bonuses, then use them to try the games.\n"
        "Good luck, and play responsibly!"
    )

@mcp_server.tool
async def validate() -> str:
    return MY_NUMBER

from games.claim import daily_amount_claim, hourly_amount_claim
from games.basic import check_casino_balance, show_leaderboard, get_casino_username, set_casino_username
from games.roulette import bet_roulette
from games.slot_machine import play_slots
from games.blackjack import blackjack_start, blackjack_stand, blackjack_hit

async def main():
    print("🚀 Starting MCP server on http://0.0.0.0:8086")
    await mcp_server.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())