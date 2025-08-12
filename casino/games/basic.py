from mcp_server import mcp_server
from common import RichToolDescription
from database import get_balance, get_top_balances, get_username, set_username
import asyncio

from typing import Annotated
from pydantic import Field

def format_leaderboard(data):
    leaderboard = "🏆 *Top Players Leaderboard* 🏆\n\n"
    for i, (user_name, amount) in enumerate(data, start=1):
        leaderboard += f"{i}. {user_name} — 💰 {amount}\n"
    return leaderboard

CHECK_BALANCE_DESCRIPTION=RichToolDescription(
    description="Checks the users current casino balance",
    use_when="When the user asks to check his casino balance"
)

LEADERBOARD_DESCRIPTION=RichToolDescription(
    description="Shows the leaderboard according to balance",
    use_when="When the user asks to see the leaderboard"
)

SET_USERNAME_DESCRIPTION=RichToolDescription(
    description="Sets the username of the user for the leaderboard",
    use_when="When the user asks to set his username for the casino",
    side_effects="Username can only be set once"
)

GET_USERNAME_DESCRIPTION=RichToolDescription(
    description="Shows the username of the user",
    use_when="The user asks for his casino username"
)

@mcp_server.tool(description=CHECK_BALANCE_DESCRIPTION.model_dump_json())
async def check_casino_balance(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    balance = get_balance(puch_user_id)
    return f"Your Balance is ${balance}"

@mcp_server.tool(description=LEADERBOARD_DESCRIPTION.model_dump_json())
async def show_leaderboard(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
    limit: Annotated[int, Field(description="Number of top players to retrieve", default=10)]
) -> str:
    user_name = get_username(puch_user_id)
    if user_name:
        leaderboard_data = get_top_balances(limit)
        return format_leaderboard(leaderboard_data)
    else:
        return "Set a username first !!!"
    
@mcp_server.tool(description=SET_USERNAME_DESCRIPTION.model_dump_json())
async def set_casino_username(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")],
    username: Annotated[str, Field(description="Username to be set that shows up on the leaderboard; Discard anything that is inappropriate or vulgar or malicious")]
) -> str:
    if set_username(puch_user_id, username):
        return "Username successfully set"
    else:
        return "Username is already set, can only be set once"
    
@mcp_server.tool(description=GET_USERNAME_DESCRIPTION.model_dump_json())
async def get_casino_username(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    username = get_username(puch_user_id)
    if username:
        return f"Your username is {username}"
    else:
        return "Username has not been set"