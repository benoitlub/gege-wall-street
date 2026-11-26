"""Conservative paper risk gate; no live execution."""
from decimal import Decimal, ROUND_DOWN
from datetime import datetime, timezone

def day(stamp):
    return datetime.fromtimestamp(stamp,timezone.utc).date()

def daily_block(events, stamp, initial=Decimal("20")):
    today=day(stamp)
    losses=sum((max(Decimal("0"),-Decimal(str(e["net"]))) for e in events if e.get("action")=="close" and day(e["timestamp"])==today),Decimal("0"))
    return losses>=initial*Decimal(".05")

def budget(capital):
    return (capital*Decimal(".02")).quantize(Decimal(".01"),rounding=ROUND_DOWN)

def token_gate(observation):
    checks=observation.get("checks",{})
    return (observation.get("eligible") is True and checks.get("lp_verified") is True
            and observation.get("wallet_ownership_verified") is True
            and observation.get("pool_age_verified") is True
            and observation.get("ai_risk_verified") is True
            and type(observation.get("ai_risk")) in (int,float)
            and 0<=observation["ai_risk"]<=4)
