"""Check the printed result tables against extracted numerical data and release cells."""
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
import re
import statistics as st
import sys
from scipy.stats import t

P=Path(__file__).resolve().parents[1]
EXP=P.parent/"experiments"
C=EXP/"cohort_029"
def read(name):
    with (P/"data"/(name+".csv")).open() as f:
        return list(csv.DictReader(f))
def load(path):
    return json.loads(path.read_bytes())
def require(ok,what):
    if not ok:
        raise ValueError(what)
def row(label,values):
    compact=re.sub(r"\s+","",article)
    text=re.sub(r"\s+","",label+"&"+"&".join(values)+r"\\")
    require(text in compact,label)
def mult(v):
    return r"\multicolumn{2}{c}{"+v+"}"
def frac(n,d):
    return f"{n}/{d:,}"
article=(P/"article.tex").read_text(encoding="utf8")
pairs=read("pairs")
d=Counter({(int(r["task"]),int(r["gold"]),int(r["action"])):int(r["count"]) for r in read("direction") if r["form"]=="1"})
secondary=load(C/"runs/confirmatory/analysis/secondary.json")
for q in (0,1):
    for gold in (0,1):
        cells=[r for r in secondary["row_cells"] if r["key"][:2]==[1,q] and r["key"][-1]==gold]
        require(sum(x["correct"] for x in cells)==d[q,gold,gold],"secondary direction")
        require(sum(x["activated"] for x in cells)==d[q,gold,1],"secondary activation")
for title,key in [("Correct when off required",0),("Correct when on required",1)]:
    row(title,[mult(frac(d[q,key,key],512)) for q in (0,1)])
row("Activated",[mult(frac(sum(d[q,g,1] for g in (0,1)),1024)) for q in (0,1)])
row("Scheduled row accuracy",[mult(frac(sum(d[q,g,g] for g in (0,1)),1024)) for q in (0,1)])
for title,axis,s in [("Target (primary)","target",None),(r"\quad Switch","target","1"),(r"\quad Invariant","target","0"),("Source role, switch","role","1"),("Source role, invariant","role","0"),("Physical order, invariant","order","0")]:
    values=[]
    for metric in ("both","changed"):
        for task in ("0","1"):
            group=[x for x in pairs if x["axis"]==axis and x["form"]=="1" and x["task"]==task and (s is None or x["switch"]==s)]
            values.append(frac(sum(int(x[metric]) for x in group),sum(int(x["pairs"]) for x in group)))
    row(title,values)
for name,label in [("target_constant_1","Always on"),("source_first","First table, exact weighting"),("source_min_effect","Smaller absolute weighted effect"),("target_equal","Governing table, equal weights"),("target_majority","Governing table, majority stratum"),("positive","Exact weighted contribution comparison")]:
    r=next(x for x in read("policies") if x["policy"]==name and x["tie"]=="0")
    row(label,[f"{int(r[k]):,}" for k in ("items","target_switch","role_switch")])
supp=(P/"supplement.tex").read_text(encoding="utf8")
for r in pairs:
    if r["axis"]!="target": continue
    data=[["Archive","Transfer"][int(r["form"])],["Causal","Arithmetic"][int(r["task"])],["Stable","Switch"][int(r["switch"])]]
    require("&".join(data+[r[k] for k in ("both","one","neither","changed")])+r"\\" in supp,"supplement target pairs")
counts=Counter()
diff=defaultdict(list)
for r in read("order016"):
    correct=int(r["action"]==r["gold"])
    counts[r["arm"],r["conflict"],r["order"]]+=correct
    if r["arm"]=="Q4_K_M" and r["conflict"]=="1":
        diff[r["family"]].append(correct*(1 if r["order"]=="historical_first" else -1))
p16=load(EXP/"cohort_016/primary_analysis.json")
for arm in ("F16","Q4_K_M"):
    for c in (0,1):
        for order in ("historical_first","randomized_first"):
            cell=p16["secondary_order_results"][arm.lower()][["aligned","conflict"][c]]["by_order"][order]
            require(counts[arm,str(c),order]==cell["correct"],"016 crossover")
x=[sum(v)/2 for v in diff.values()]
se=st.stdev(x)/len(x)**.5
dv=p16["primary_q4_conflict_order_effect"]
require(abs(st.mean(x)/se-dv["t_statistic"])<1e-8,"016 test statistic")
require(abs(t.sf(abs(st.mean(x)/se),95)*2/dv["two_sided_p_value"]-1)<1e-6,"016 p value")
require([round(z*100,1) for z in dv["family_percentile_bootstrap_95_interval"]]==[56.8,68.2],"016 bootstrap")
tok=load(C/"freeze/deployment/token_budget.json")["counts"]
ind=[json.loads(line) for line in (C/"freeze/fixture/design.jsonl").read_bytes().splitlines()]
groups=defaultdict(set)
for r in ind:
    groups[tuple(r["indices"][1:3])].add(tok[r["task_id"]]["tokens"])
require(groups=={(0,0):{210},(0,1):{197},(1,0):{327},(1,1):{235}},"token counts")
tasks={r["task_id"]:r for r in map(json.loads,(C/"freeze/fixture/tasks.jsonl").open(encoding="utf8"))}
for name,task_bit in (("causal",0),("arithmetic",1)):
    match=next(r for r in ind if r["indices"]==[96,1,task_bit,0,0,0])
    frozen=tasks[match["task_id"]]["messages"][1]["content"].encode("utf8")
    require((P/"data"/f"prompt-family096-{name}.txt").read_bytes()==frozen,"exact prompt bytes: "+name)
require(all(r["passed"] for r in load(P/"audit/release-verification.json")["checks"]),"release checks")
require(load(P/"audit/analysis-replay.json")=={"changed":[],"passed":True},"replay")
text="PASS. Printed primary/secondary and policy tables, supplement pair components, machine-readable secondary direction cells, Cohort 016 crossover and test, token counts, release checks and byte replay."
print(text)

