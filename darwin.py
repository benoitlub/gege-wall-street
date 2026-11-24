"""Exploratory ranking, not evidence of future profitability."""
def rank(results):
    ranked=[]
    for name,m in results.items():
        gain=m["net_return"]
        dd=m["max_drawdown"]
        score=gain-2*dd
        ranked.append({"strategy":name,"score":score,"net_return":gain,
                       "max_drawdown":dd,"executions":m["executions"],
                       "eligible_for_further_research":name!="cash" and gain>0 and dd<=.10 and m["executions"]>=10 and not m.get("liquidated",False)})
    ranked.sort(key=lambda x:x["score"],reverse=True)
    candidates=[x for x in ranked if x["eligible_for_further_research"] and x["score"]>0]
    return {"ranking":ranked,"next_candidate":candidates[0]["strategy"] if candidates else "cash",
            "status":"exploratory_only","score_formula":"net_return - 2 * max_drawdown",
            "limits":{"max_drawdown":.10,"min_executions":10},
            "warning":"Selection on this sample requires fresh independent validation; executions are not independent trades."}
