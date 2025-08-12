import random
from mcp_server import mcp_server
from common import RichToolDescription
from database import add_balance, deduct_balance, get_balance
from typing import Annotated
from pydantic import Field

BET_ROULETTE_DESCRIPTION = RichToolDescription(
    description="Bet on the roulette wheel with inside and outside bets. Always show the whole outcome given by the function",
    use_when="When the user wants to place a bet on roulette",
    side_effects="If the ball lands on the number or color chosen, player wins payout, else loses bet"
)

RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

@mcp_server.tool()
def bet_roulette(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
    bet_type: Annotated[str, Field(description="Bet type: straight, split, street, corner, sixline, color, odd, even, low, high, dozen, column")],
    bet_value: Annotated[str, Field(description="Specific numbers, colors, or range depending on bet type")],
    amount: Annotated[int, Field(description="The amount to bet")],
) -> str:
    balance = get_balance(puch_user_id)
    if balance is None or balance < amount:
        return "❌ Not enough balance."

    deduct_balance(puch_user_id, amount)

    # Spin the wheel
    winning_number = random.randint(0, 36)
    if winning_number == 0:
        winning_color = "green"
    elif winning_number in RED_NUMBERS:
        winning_color = "red"
    else:
        winning_color = "black"

    win = False
    payout = 0
    bet_type = bet_type.lower()
    bet_value = bet_value.lower()

    # Inside bets
    if bet_type == "straight":  # 1 number
        if int(bet_value) == winning_number:
            payout = amount * 35
            win = True

    elif bet_type == "split":  # 2 numbers
        nums = {int(n) for n in bet_value.split(",")}
        if winning_number in nums:
            payout = amount * 17
            win = True

    elif bet_type == "street":  # 3 numbers
        nums = {int(n) for n in bet_value.split(",")}
        if winning_number in nums:
            payout = amount * 11
            win = True

    elif bet_type == "corner":  # 4 numbers
        nums = {int(n) for n in bet_value.split(",")}
        if winning_number in nums:
            payout = amount * 8
            win = True

    elif bet_type == "sixline":  # 6 numbers
        nums = {int(n) for n in bet_value.split(",")}
        if winning_number in nums:
            payout = amount * 5
            win = True

    # Outside bets
    elif bet_type == "color":
        if bet_value in ["red", "black", "green"] and bet_value == winning_color:
            payout = amount * (17 if bet_value == "green" else 2)
            win = True

    elif bet_type == "odd" and winning_number != 0 and winning_number % 2 != 0:
        payout = amount * 2
        win = True

    elif bet_type == "even" and winning_number != 0 and winning_number % 2 == 0:
        payout = amount * 2
        win = True

    elif bet_type == "low" and 1 <= winning_number <= 18:
        payout = amount * 2
        win = True

    elif bet_type == "high" and 19 <= winning_number <= 36:
        payout = amount * 2
        win = True

    elif bet_type == "dozen":  # 1-12, 13-24, 25-36
        dozen_num = int(bet_value)
        if dozen_num == 1 and 1 <= winning_number <= 12:
            payout = amount * 3
            win = True
        elif dozen_num == 2 and 13 <= winning_number <= 24:
            payout = amount * 3
            win = True
        elif dozen_num == 3 and 25 <= winning_number <= 36:
            payout = amount * 3
            win = True

    elif bet_type == "column":  # 3 columns
        column = int(bet_value)
        if column == ((winning_number - 1) % 3) + 1:
            payout = amount * 3
            win = True

    else:
        return "❌ Invalid bet type or value."

    if win:
        add_balance(puch_user_id, payout)

    return  f"Show the entire message below in the exact format to the user as it is and don't say anything else **Roulette Outcome**\n\n🎯 Winning number: {winning_number} ({winning_color})\n{'✅ You won!' if win else '❌ You lost!'} {'Total Payout: ' + str(payout - amount) if win else ''}"
        
