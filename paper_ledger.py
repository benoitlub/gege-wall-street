"""Persistent paper accounting. No historical benchmark ingestion."""
import json
import os
from pathlib import Path
from treasury import Treasury, money

class Ledger:
    def __init__(self,path):
        self.path=Path(path)
        self.treasury=Treasury()
        self.events={}
        if self.path.exists():
            data=json.loads(self.path.read_text())
            if data["mode"]!="paper_only": raise ValueError("Invalid mode")
            self.events=data["events"]
            for event in self.events.values():
                if event["kind"]=="settlement": self.treasury.settle(event["net"])
                elif event["kind"]=="payout": self.treasury.paper_payout()
                else: raise ValueError("Unknown event")

    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True)
        tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps({"mode":"paper_only","events":self.events,"treasury":self.treasury.snapshot()},indent=2))
        os.replace(tmp,self.path)

    def settle(self,event_id,net):
        if not isinstance(event_id,str) or not event_id: raise ValueError("Missing event ID")
        event={"kind":"settlement","net":str(money(net))}
        if event_id in self.events:
            if self.events[event_id]!=event: raise ValueError("Conflicting event")
            return False
        self.treasury.settle(net)
        self.events[event_id]=event
        self.save()
        return True

    def payout(self,event_id):
        if not isinstance(event_id,str) or not event_id: raise ValueError("Missing event ID")
        if event_id in self.events: return False
        amount=self.treasury.paper_payout()
        if not amount: return False
        self.events[event_id]={"kind":"payout","amount":str(amount)}
        self.save()
        return True

if __name__=="__main__":
    ledger=Ledger("docs/treasury.json")
    ledger.save()
