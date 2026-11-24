"""Paper treasury. No exchange, wallet or bank integration."""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN

def money(x):
    v=Decimal(str(x))
    if not v.is_finite(): raise ValueError("Non-finite amount")
    return v.quantize(Decimal("0.01"), rounding=ROUND_DOWN)

@dataclass
class Treasury:
    capital: Decimal = Decimal("20.00")
    reserve: Decimal = Decimal("0.00")
    payable: Decimal = Decimal("0.00")
    paid: Decimal = Decimal("0.00")
    deficit: Decimal = Decimal("0.00")
    halted: bool = False

    def settle(self, realized_net):
        """Apply a closed simulated position's net P&L exactly once upstream."""
        pnl=money(realized_net)
        if self.halted: raise ValueError("Treasury halted")
        if pnl<0:
            loss=-pnl
            if loss>self.capital+self.reserve:
                raise ValueError("Loss exceeds funded paper balance")
            cover=min(self.reserve,loss)
            self.reserve-=cover
            self.capital-=loss-cover
            self.deficit+=loss
            if self.capital==0: self.halted=True
        else:
            recovery=min(self.deficit,pnl)
            self.deficit-=recovery
            self.capital+=recovery
            surplus=pnl-recovery
            reserve=money(surplus/4)
            payable=money(surplus/4)
            self.reserve+=reserve
            self.payable+=payable
            self.capital+=surplus-reserve-payable

    def paper_payout(self):
        if self.deficit or self.halted: return Decimal("0.00")
        amount=self.payable
        self.payable=Decimal("0.00")
        self.paid+=amount
        return amount

    def snapshot(self):
        return {**{k:str(v) for k,v in vars(self).items() if isinstance(v,Decimal)},
                "halted":self.halted,"mode":"paper_only","real_money":False}
