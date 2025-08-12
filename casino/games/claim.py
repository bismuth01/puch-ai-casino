from mcp_server import mcp_server
from common import RichToolDescription
from database import get_daily_claim_time, set_daily_claim_time, get_hourly_claim_time, set_hourly_claim_time, add_balance
import asyncio
import time

from typing import Annotated
from pydantic import Field

DAILY_CLAIM_DESCRIPTION=RichToolDescription(
    description="Claim your daily amount of money",
    use_when="When the user asks to claim his daily amount",
    side_effects="Can only be claimed every 24 hours"
)

HOURLY_CLAIM_DESCRIPTION=RichToolDescription(
    description="Claim your hourly amount of money",
    use_when="When the user asks to claim his hourly amount",
    side_effects="Can only be claimed every hour"
)

@mcp_server.tool(description=DAILY_CLAIM_DESCRIPTION.model_dump_json())
async def daily_amount_claim(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    last_claim_time = get_daily_claim_time(puch_user_id)
    if int(time.time()) - last_claim_time > 24 * 60 * 60:
        set_daily_claim_time(puch_user_id, int(time.time()))
        add_balance(puch_user_id, 1000)
        return "1000 rupee Daily Amount Claimed !!! 💵"
    else:
        return "Daily Amount Can Only Be Claimed Every 24 Hours"
    
@mcp_server.tool(description=HOURLY_CLAIM_DESCRIPTION.model_dump_json())
async def hourly_amount_claim(
    puch_user_id: Annotated[str, Field(description="Puch User Unique Identifier")]
) -> str:
    last_claim_time = get_hourly_claim_time(puch_user_id)
    if int(time.time()) - last_claim_time > 60 * 60:
        set_hourly_claim_time(puch_user_id, int(time.time()))
        add_balance(puch_user_id, 100)
        return "100 rupee Daily Amount Claimed !!! 💵"
    else:
        return "Daily Amount Can Only Be Claimed Every Hour"