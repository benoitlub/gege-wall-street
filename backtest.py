"""Research benchmark on historical candles; never submits orders."""
import math

def simulate(prices, strategy, capital=20., fee=.001, slip=.002, start=20):
    if len(prices)<=start+1 or any(not math.isfinite(p) or p<=0 for p in prices):
        raise ValueError("Insufficient or invalid prices")
    cash=capital
    units=0.
    peak=capital
    drawdown=0.
    trades=0
    for i in range(start,len(prices)):
        history=prices[:i]
        signal=strategy(history)
        p=prices[i]
        if signal and not units and i<len(prices)-1:
            units=cash/(p*(1+slip)*(1+fee))
            cash=0.
            trades+=1
        elif units and (not signal or i==len(prices)-1):
            cash=units*p*(1-slip)*(1-fee)
            units=0.
            trades+=1
        equity=cash+units*p*(1-slip)*(1-fee)
        peak=max(peak,equity)
        drawdown=max(drawdown,1-equity/peak)
    return {"initial":capital,"final":cash,"net_return":cash/capital-1,"max_drawdown":drawdown,"executions":trades}

def momentum(h):
    return h[-1]>sum(h[-20:])/20 and h[-1]>h[-5]

def reversal(h):
    return h[-1]<sum(h[-10:])/10*.98

def breakout(h):
    return h[-1]>max(h[-20:-1])

STRATEGIES={"momentum":momentum,"reversal":reversal,"breakout":breakout,"cash":lambda h:False,"buy_hold":lambda h:True}

def compare(prices):
    # Fixed rules, untouched chronological test segment with prior warmup.
    split=max(20,int(len(prices)*.7))
    return {name:simulate(prices,rule,start=split) for name,rule in STRATEGIES.items()}
