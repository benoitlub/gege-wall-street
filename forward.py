"""Prospective spot-only experiment. No private API or orders."""
import json, math, os, time, urllib.request
from pathlib import Path
from decimal import Decimal, ROUND_FLOOR
from historical_lab import candles
from directional import adaptive
from treasury import Treasury

PAIR="XBTEUR"
COST=.003
def step(state, stamp, price, signal):
    if not math.isfinite(price) or price<=0: raise ValueError("Invalid quote")
    if stamp<=state.get("last",0): return state
    t=Treasury(**{k:Decimal(v) for k,v in state["treasury"].items() if k in ("capital","reserve","payable","paid","deficit")},halted=state["treasury"]["halted"])
    pos=state.get("position")
    event={"timestamp":stamp,"price":price,"signal":signal,"action":"cash"}
    if pos:
        pnl=Decimal(str(pos["budget"]*(price/pos["price"]*(1-COST)/(1+COST)-1))).quantize(Decimal(".01"),rounding=ROUND_FLOOR)
        t.settle(pnl)
        event.update(action="close",net=str(pnl))
        pos=None
    elif signal==1 and not t.halted and t.capital>=Decimal("10") and t.deficit<Decimal("2"):
        budget=float((t.capital*Decimal(".25")).quantize(Decimal(".01")))
        pos={"price":price,"budget":budget,"opened":stamp}
        event.update(action="open",budget=budget)
    state.update(last=stamp,position=pos,treasury=t.snapshot())
    state["events"].append(event)
    return state

def main():
    path=Path("docs/forward.json")
    state=json.loads(path.read_text()) if path.exists() else {"mode":"paper_only","treasury":Treasury().snapshot(),"events":[]}
    if state["mode"]!="paper_only": raise ValueError("Invalid mode")
    rows=candles(PAIR)
    signal=adaptive([float(r[4]) for r in rows])
    with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair="+PAIR,timeout=25) as response:
        d=json.load(response)
    if d.get("error"): raise ValueError("Ticker error")
    q=next(iter(d["result"].values()))
    price=float(q["a"][0] if not state.get("position") else q["b"][0])
    stamp=int(time.time())
    if stamp-state.get("last",0)<1800: return
    step(state,stamp,price,signal)
    state["limitations"]=["BTC spot only; observed bid/ask plus assumed 0.3% per side","No actual fills; fixed 25% allocation; closes at next successful observation","No automatic payouts yet"]
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(state,indent=2));os.replace(tmp,path)

if __name__=="__main__": main()
