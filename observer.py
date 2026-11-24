"""Read-only market observation. No trading or signing."""
import json
import time
import urllib.request
from pathlib import Path
from paper import Quote, eligible

DEX = "https://api.dexscreener.com"
RPC = "https://api.mainnet.solana.com"

def request(url, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json","User-Agent":"GegeWallStreet/0.2"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)

def rpc(method, params):
    result = request(RPC, {"jsonrpc":"2.0","id":1,"method":method,"params":params})
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    return result["result"]

def inspect(address):
    pairs = request(DEX + "/token-pairs/v1/solana/" + address)
    pairs = [p for p in pairs if p.get("baseToken",{}).get("address")==address]
    if not pairs:
        raise ValueError("No matching base-token pool")
    pair = max(pairs,key=lambda p:float((p.get("liquidity") or {}).get("usd") or 0))
    supply = int(rpc("getTokenSupply",[address])["value"]["amount"])
    time.sleep(.5)
    accounts = rpc("getTokenLargestAccounts",[address])["value"]
    time.sleep(.5)
    info = rpc("getAccountInfo",[address,{"encoding":"jsonParsed"}])["value"]["data"]["parsed"]["info"]
    shares = sorted([int(a["amount"])/supply for a in accounts],reverse=True)
    if not shares:
        raise ValueError("Missing token accounts")
    q = Quote(float((pair.get("liquidity") or {}).get("usd") or 0),sum(shares[:10]),shares[0],
              "mintAuthority" in info and info["mintAuthority"] is None,
              "freezeAuthority" in info and info["freezeAuthority"] is None,
              False)
    return {"address":address,"symbol":pair["baseToken"].get("symbol"),"price_usd":pair.get("priceUsd"),
            "checks":vars(q),"lp_status":"UNKNOWN","eligible":eligible(q),
            "decision":"skip","reason":"LP verification unavailable; account concentration is not wallet ownership"}

def scan(limit=5):
    profiles = request(DEX+"/token-profiles/latest/v1")
    addresses = list(dict.fromkeys(p["tokenAddress"] for p in profiles if p.get("chainId")=="solana"))[:limit]
    results=[]
    for address in addresses:
        try:
            results.append(inspect(address))
        except Exception as exc:
            results.append({"address":address,"decision":"error","reason":str(exc)})
        time.sleep(1)
    return results

if __name__=="__main__":
    output={"timestamp":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),"mode":"paper","initial_eur":100}
    try:
        output["observations"]=scan()
        output["status"]="observed"
    except Exception as exc:
        output.update(status="error",error=str(exc),observations=[])
    Path("docs").mkdir(exist_ok=True)
    Path("docs/status.json").write_text(json.dumps(output,indent=2),encoding="utf-8")
    print(json.dumps(output,indent=2))
    if output["status"]=="error":
        raise SystemExit(1)
