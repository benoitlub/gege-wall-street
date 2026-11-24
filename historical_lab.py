"""Public historical research only; no credentials or orders."""
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from backtest import compare
from directional import compare as directional_compare

def candles(pair):
    url="https://api.kraken.com/0/public/OHLC?pair="+pair+"&interval=60"
    with urllib.request.urlopen(url,timeout=25) as response:
        data=json.load(response)
    if data.get("error"): raise ValueError("Kraken API error")
    rows=next(v for k,v in data["result"].items() if k!="last")[:-1]
    if len(rows)<100: raise ValueError("Insufficient history")
    if any(int(b[0])-int(a[0])!=3600 for a,b in zip(rows,rows[1:])):
        raise ValueError("Non-contiguous candles")
    return rows

def main():
    report={"timestamp":datetime.now(timezone.utc).isoformat(),"mode":"historical_research_only","interval_minutes":60,"assets":{},"limitations":["Fixed rules, no optimization","Single chronological holdout, not independent repeated validation","Short benchmark hypothetical, no verified funding or borrow availability","No microcap liquidity or execution validation"]}
    for pair in ("XBTEUR","ETHEUR","SOLEUR"):
        try:
            rows=candles(pair)
            prices=[float(row[4]) for row in rows]
            report["assets"][pair]={"candles":len(rows),"first":int(rows[0][0]),"last":int(rows[-1][0]),"spot":compare(prices),"directional_hypothetical":directional_compare(prices,shortable=True)}
        except Exception as exc:
            report["assets"][pair]={"error":type(exc).__name__}
    report["status"]="completed" if all("error" not in v for v in report["assets"].values()) else "partial_or_failed"
    Path("docs/backtest.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report["status"]=="completed"

if __name__=="__main__":
    raise SystemExit(0 if main() else 1)
