"""Hypothetical directional benchmark, not executable trading."""
import math

def adaptive(h):
    mean=sum(h[-20:])/20
    fast=sum(h[-5:])/5
    return 1 if fast>mean*1.01 else -1 if fast<mean*.99 else 0

def simulate(prices, rule=adaptive, capital=20., fee=.001, slip=.002,
             shortable=False, short_cost_per_bar=.0001, start=20):
    if len(prices)<=start+1 or start<20 or any(not math.isfinite(p) or p<=0 for p in prices):
        raise ValueError("Invalid price history")
    if capital<=0 or min(fee,slip,short_cost_per_bar)<0 or fee+slip>=1:
        raise ValueError("Invalid costs or capital")
    equity=capital
    peak=capital
    dd=0.
    position=0
    executions=0
    losses=0
    liquidated=False
    cost=fee+slip
    for i in range(start,len(prices)):
        if position:
            equity*=1+position*(prices[i]/prices[i-1]-1)-(short_cost_per_bar if position<0 else 0)
            if equity<=0:
                equity=0.
                dd=1.
                liquidated=True
                break
        target=0 if i==len(prices)-1 else rule(prices[:i])
        if target not in (-1,0,1):
            raise ValueError("Invalid signal")
        if target<0 and not shortable:
            target=0
        if target!=position:
            executions+=abs(target-position)
            equity*= (1-cost)**abs(target-position)
        if equity<peak:
            dd=max(dd,1-equity/peak)
        peak=max(peak,equity)
        if position and prices[i]/prices[i-1]*position<position:
            losses+=1
        position=target
    return {"initial":capital,"final":equity,"net_return":equity/capital-1,
            "max_drawdown":dd,"executions":executions,"adverse_bars":losses,
            "liquidated":liquidated,"short_enabled":shortable,
            "model":"hypothetical_constant_notional_per_bar",
            "limitations":["No verified borrowing or funding data","No intrabar liquidation or liquidity model","Rebalancing costs not fully modeled"]}

def compare(prices, shortable=False):
    start=max(20,int(len(prices)*.7))
    return {name:simulate(prices,rule,shortable=shortable,start=start)
            for name,rule in {"adaptive":adaptive,"long":lambda h:1,
                              "short":lambda h:-1,"cash":lambda h:0}.items()}
