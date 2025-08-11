from mcp_server import mcp_server
from common import RichToolDescription
from database import get_balance
import asyncio

from typing import Annotated
from pydantic import Field

CHECK_BALANCE_DESCRIPTION=RichToolDescription(
    description="Checks the users current casino balance",
    use_when="When the user asks to check his casino balance"
)

@mcp_server.tool(description=CHECK_BALANCE_DESCRIPTION.model_dump_json())
async def check_casino_balance(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    balance = get_balance(puch_user_id)
    return f"Your Balance is ${balance}"