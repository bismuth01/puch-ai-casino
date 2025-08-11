from mcp_server import mcp_server
from common import RichToolDescription
from database import daily_claim
import asyncio

from typing import Annotated
from pydantic import Field

DAILY_CLAIM_DESCRIPTION=RichToolDescription(
    description="Claim your daily amount of money",
    use_when="When the user asks to claim his daily amount",
    side_effects="Can only be claimed every 24 hours"
)

@mcp_server.tool(description=DAILY_CLAIM_DESCRIPTION.model_dump_json())
async def daily_amount_claim(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    if daily_claim(puch_user_id):
        return "$1000 Daily Amount Claimed !!! 💵"
    else:
        return "Daily Amount Can Only Be Claimed Every 24 Hours"