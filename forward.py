"""Prospective spot-only experiment. No private API or orders."""
import json, math, os, time, urllib.request
from pathlib import Path
from decimal import Decimal, ROUND_FLOOR
from historical_lab import candles
from directional import adaptive
from treasury import Treasury

PAIRS=("XBTEUR","ETHEUR","SOLEUR")
COST=.003
def step(state, stamp, price, signal, pair="XBTEUR"):
    if not math.isfinite(price) or price<=0: raise ValueError("Invalid quote")
    if stamp<=state.get("last",0): return state
    t=Treasury(**{k:Decimal(v) for k,v in state["treasury"].items() if k in ("capital","reserve","payable","paid","deficit")},halted=state["treasury"]["halted"])
    pos=state.get("position")
    event={"pair":pair,"timestamp":stamp,"price":price,"signal":signal,"action":"cash"}
    if pos:
        if pos.get("pair","XBTEUR")!=pair: raise ValueError("Position pair mismatch")
        pnl=Decimal(str(pos["budget"]*(price/pos["price"]*(1-COST)/(1+COST)-1))).quantize(Decimal(".01"),rounding=ROUND_FLOOR)
        t.settle(pnl)
        event.update(action="close",net=str(pnl))
        pos=None
    elif signal==1 and not t.halted and t.capital>=Decimal("10") and t.deficit<Decimal("2"):
        budget=float((t.capital*Decimal(".25")).quantize(Decimal(".01")))
        pos={"pair":pair,"price":price,"budget":budget,"opened":stamp}
        event.update(action="open",budget=budget)
    state.update(last=stamp,position=pos,treasury=t.snapshot())
    state["events"].append(event)
    return state

def main():
    path=Path("docs/forward.json")
    state=json.loads(path.read_text()) if path.exists() else {"mode":"paper_only","treasury":Treasury().snapshot(),"events":[]}
    if state["mode"]!="paper_only": raise ValueError("Invalid mode")
    observations={}
    for pair in PAIRS:
        try:
            rows=candles(pair)
            prices=[float(r[4]) for r in rows]
            if any(not math.isfinite(p) or p<=0 for p in prices): raise ValueError("Invalid candles")
            if time.time()-int(rows[-1][0])>10800: raise ValueError("Stale candles")
            score=(sum(prices[-5:])/5)/(sum(prices[-20:])/20)-1
            with urllib.request.urlopen("https://api.kraken.com/0/public/Ticker?pair="+pair,timeout=25) as response:
                d=json.load(response)
            if d.get("error"): raise ValueError("Ticker error")
            q=next(iter(d["result"].values()))
            bid,ask=float(q["b"][0]),float(q["a"][0])
            if not 0<bid<=ask or not math.isfinite(ask): raise ValueError("Invalid spread")
            observations[pair]={"bid":bid,"ask":ask,"score":score,"signal":adaptive(prices)}
        except Exception as exc:
            observations[pair]={"error":type(exc).__name__}
    stamp=int(time.time())
    if stamp-state.get("last",0)<1800: return
    pos=state.get("position")
    valid={p:q for p,q in observations.items() if "error" not in q}
    if pos:
        pair=pos.get("pair","XBTEUR")
        if pair in valid: step(state,stamp,valid[pair]["bid"],valid[pair]["signal"],pair)
    elif valid:
        pair=max(valid,key=lambda p:valid[p]["score"])
        q=valid[pair]
        step(state,stamp,q["ask"],q["signal"] if len(valid)==len(PAIRS) else 0,pair)
    state["observations"]=observations
    state["observed_at"]=stamp
    state["limitations"]=["BTC ETH SOL spot only; observed bid/ask plus assumed 0.3% per side","Single shared capital; one position at a time; strongest positive trend","No actual fills or automatic payouts; closes at next successful observation"]
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(state,indent=2));os.replace(tmp,path)

if __name__=="__main__": main()
