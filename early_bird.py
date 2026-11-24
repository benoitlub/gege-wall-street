"""Public discovery cohort; no trading or security approval."""
import json,time,urllib.request,os,math
from pathlib import Path
def get(path):
    req=urllib.request.Request("https://api.dexscreener.com/"+path,headers={"User-Agent":"GegeResearch/1"})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
def main():
    p=Path("docs/early_bird.json")
    d=json.loads(p.read_text()) if p.exists() else {"mode":"observation_only","tokens":{}}
    tokens=d["tokens"]
    now=int(time.time())
    profiles=get("token-profiles/latest/v1")
    for item in profiles:
        a=item.get("tokenAddress")
        if item.get("chainId")=="solana" and a and a.isalnum() and a not in tokens and len(tokens)<1000:
            tokens[a]={"detected":now,"samples":[]}
    due=[(a,t) for a,t in tokens.items() if now-t["detected"]<=90000 and (not t["samples"] or now-t["samples"][-1]["time"]>=300)]
    for i in range(0,len(due),30):
        batch=due[i:i+30]
        try:
            rows=get("tokens/v1/solana/"+",".join(a for a,t in batch))
            for a,t in batch:
                pairs=[q for q in rows if q.get("baseToken",{}).get("address")==a]
                if t.get("pair"): pairs=[q for q in pairs if q.get("pairAddress")==t["pair"]]
                q=max(pairs,key=lambda q:(q.get("liquidity") or {}).get("usd") or 0,default={})
                s={"time":now,"status":"missing_pair"}
                if q:
                    price=float(q.get("priceUsd") or 0)
                    if math.isfinite(price) and price>0:
                        t["pair"]=q["pairAddress"]
                        s.update(status="observed",price=price,liquidity=(q.get("liquidity") or {}).get("usd"),pair_created=q.get("pairCreatedAt"))
                t["samples"].append(s)
        except Exception as e:
            for a,t in batch:t["samples"].append({"time":now,"status":"collection_error","error":type(e).__name__})
    d.update(updated=now,target=1000,limitations=["Latest profiles are not an exhaustive launch feed","Detection time is not launch time","Missing pairs are not assumed worthless","No security approval or executable returns"])
    tmp=p.with_suffix(".tmp");tmp.write_text(json.dumps(d,indent=2));os.replace(tmp,p)
if __name__=="__main__":main()
