"""Persist observations and explain risk gates; never place orders."""
import json
from pathlib import Path

def reasons(o):
    if o.get("decision") == "error":
        return ["Observation failed"]
    q = o.get("checks", {})
    failures = []
    for key, predicate, label in [
        ("liquidity", lambda x: x >= 25000, "Liquidity below threshold"),
        ("top10", lambda x: 0 <= x <= .4, "Top ten token accounts too concentrated"),
        ("largest", lambda x: 0 <= x <= .1, "Largest token account too concentrated"),
        ("mint_disabled", lambda x: x is True, "Mint authority not verified disabled"),
        ("freeze_disabled", lambda x: x is True, "Freeze authority not verified disabled"),
        ("lp_verified", lambda x: x is True, "LP protection unverified"),
    ]:
        try:
            if not predicate(q[key]):
                failures.append(label)
        except (KeyError, TypeError, ValueError):
            failures.append(label + " (missing or invalid)")
    failures.append("Beneficial wallet ownership not verified")
    return failures

def summarize(snapshot, history):
    rows = snapshot.get("observations", [])
    decisions = [{**o, "guardian_reasons": reasons(o), "paper_order": False} for o in rows]
    result = {**snapshot, "observations": decisions,
              "summary": {"observed": len(rows),
                          "rejected": sum(o.get("decision") != "error" for o in rows),
                          "errors": sum(o.get("decision") == "error" for o in rows),
                          "orders": 0},
              "portfolio": {"initial_eur": 100, "valuation_eur": None, "status": "not_started"}}
    history = [h for h in history if h.get("timestamp") != snapshot.get("timestamp")]
    history.append({"timestamp": snapshot.get("timestamp"), "status": snapshot.get("status"),
                    "summary": result["summary"], "observations": decisions})
    return result, history[-100:]

def main():
    status = Path("docs/status.json")
    journal = Path("docs/history.json")
    history = json.loads(journal.read_text()) if journal.exists() else []
    result, history = summarize(json.loads(status.read_text()), history)
    status.write_text(json.dumps(result, indent=2), encoding="utf-8")
    journal.write_text(json.dumps(history, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
