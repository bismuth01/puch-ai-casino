import random
from mcp_server import mcp_server
from common import RichToolDescription
from database import add_balance, deduct_balance, get_balance
from typing import Annotated
from pydantic import Field

SLOT_MACHINE_DESCRIPTION = RichToolDescription(
    description="Play a slot machine game with emojis and payouts.",
    use_when="When the user asks to play slots",
    side_effects="Deducts bet amount, spins the slot, awards payout if matching symbols"
)

SYMBOLS = ["🍒", "🍋", "🍇", "🍊", "⭐", "🔔", "💎", "7️⃣"]

PAYOUTS = {
    "💎": 50,
    "7️⃣": 30,
    "⭐": 20,
    "🍒": 10,
    "🍋": 10,
    "🍇": 10,
    "🍊": 10,
    "🔔": 15
}

@mcp_server.tool(description=SLOT_MACHINE_DESCRIPTION.model_dump_json())
def play_slots(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
    amount: Annotated[int, Field(description="The amount to bet")],
) -> str:
    balance = get_balance(puch_user_id)
    if balance is None or balance < amount:
        return {"success": False, "message": "❌ Not enough balance to play."}

    deduct_balance(puch_user_id, amount)

    # Spin the slots
    slot_grid = [[random.choice(SYMBOLS) for _ in range(3)] for _ in range(3)]

    # We'll evaluate only the middle row for main wins (like a classic 3x3)
    middle_row = slot_grid[1]

    payout = 0
    win = False

    # Check if all three match
    if middle_row[0] == middle_row[1] == middle_row[2]:
        symbol = middle_row[0]
        payout = amount * PAYOUTS.get(symbol, 5)  # default 5x if missing
        win = True

    # Check for two matching symbols
    elif middle_row[0] == middle_row[1] or middle_row[1] == middle_row[2] or middle_row[0] == middle_row[2]:
        payout = amount * 3
        win = True

    # Add winnings if any
    if win:
        add_balance(puch_user_id, payout)

    # Prepare slot display
    slot_display = "\n".join(" | ".join(row) for row in slot_grid)

    return f"Show the entire message below to the user as it is **Slot Machine Outcome**\n\n🎰 SLOT MACHINE 🎰\n{slot_display}\n{'✅ You win ' + str(payout) + ' coins!' if win else '❌ No luck this time!'}"
