"""Paper only. No wallet or transaction signing."""
from dataclasses import dataclass

@dataclass
class Quote:
    liquidity: float
    top10: float
    largest: float
    mint_disabled: bool
    freeze_disabled: bool
    lp_verified: bool

def eligible(q):
    return (q.liquidity >= 25000 and q.top10 <= .4 and q.largest <= .1
            and q.mint_disabled and q.freeze_disabled and q.lp_verified)

class Portfolio:
    def __init__(self, cash=100):
        self.cash = cash
        self.positions = {}
    def buy(self, token, price, q, risk):
        if not eligible(q) or not 0 <= risk <= 4 or price <= 0 or token in self.positions:
            return False
        budget = self.cash * .02
        self.positions[token] = (budget / (price * 1.01 * 1.003), budget)
        self.cash -= budget
        return True
    def sell(self, token, price):
        if price < 0:
            raise ValueError("negative price")
        units, cost = self.positions.pop(token)
        proceeds = units * price * .99 * .997
        self.cash += proceeds
        return proceeds - cost

if __name__ == "__main__":
    p = Portfolio()
    good = Quote(50000,.25,.07,True,True,True)
    bad = Quote(50000,.25,.07,True,True,False)
    assert not p.buy("unverified",1,bad,2)
    assert p.buy("fictional",1,good,2)
    assert p.sell("fictional",1) < 0
    print("Offline demo passed; fictitious cash:", round(p.cash, 4))
