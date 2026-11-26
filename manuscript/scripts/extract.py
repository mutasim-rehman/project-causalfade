"""Reconstruct manuscript summaries from the released bytes. No inference."""
import base64
import csv
import hashlib
import json
import re
import statistics as st
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from scipy.stats import t

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT.parent / "experiments"
C = EXP / "cohort_029"
FIX = C / "freeze/fixture"
RUN = C / "runs/confirmatory"
AN = RUN / "analysis"

def read(path):
    return json.loads(path.read_bytes())

def lines(path):
    return [json.loads(line) for line in path.read_bytes().splitlines()]

def keyed(records):
    result = {r["task_id"]: r for r in records}
    assert len(result) == len(records)
    return result

def save(name, rows):
    with (ROOT/"data"/(name+".csv")).open("w",encoding="utf8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)

def strict(items):
    assert len(items)==1 and items[0][0]=="activate"
    value=items[0][1]
    assert type(value) is int and value in (0,1)
    return value

def interval(values):
    groups=[values[k:k+16] for k in range(0,128,16)]
    terms=[st.variance(g)/1024 for g in groups]
    se=sum(terms)**0.5
    df=sum(terms)**2/sum(x**2/15 for x in terms)
    mean=st.mean(values)
    radius=t.ppf(.975,df)*se
    return dict(mean=mean,low=mean-radius,high=mean+radius,se=se,df=df)

def main():
    assert hashlib.sha256((RUN/"events.jsonl").read_bytes()).hexdigest()=="673eb723637614dc8b94875f2e8c4e9e20234c1d179c992791853797875977bd"
    design=keyed(lines(FIX/"design.jsonl"))
    oracle=keyed(lines(FIX/"public_oracle.jsonl"))
    gold=keyed(lines(FIX/"gold.jsonl"))
    scored=keyed(lines(AN/"row_scores.jsonl"))
    events=keyed([e for e in lines(RUN/"events.jsonl") if e["type"]=="response"])
    assert events.keys()==scored.keys()==gold.keys()==design.keys()==oracle.keys()
    rows={}
    directions=Counter()
    positions=Counter()
    for key,e in events.items():
        raw=base64.b64decode(e["response_b64"])
        assert hashlib.sha256(raw).hexdigest()==e["response_sha256"]
        choice=json.loads(raw)["choices"][0]
        assert choice["finish_reason"]=="stop"
        a=json.loads(choice["message"]["content"],object_pairs_hook=strict)
        truth=gold[key]["action"]
        assert a==scored[key]["action"] and truth==oracle[key]["action"]==scored[key]["gold"]
        i=tuple(design[key]["indices"])
        rows[i]=(a,truth)
        directions[i[1],i[2],truth,a]+=1
        positions[i[1],i[2],oracle[key]["options"][0],int(a==truth),a]+=1
    assert len(rows)==4096
    save("direction",[dict(form=f,task=q,gold=g,action=a,count=directions[f,q,g,a]) for f in range(2) for q in range(2) for g in range(2) for a in range(2)])
    save("option_order",[dict(form=f,task=q,first_option=o,n=sum(v for (ff,qq,oo,c,a),v in positions.items() if (ff,qq,oo)==(f,q,o)),correct=sum(positions[f,q,o,1,a] for a in (0,1)),activated=sum(positions[f,q,o,c,1] for c in (0,1))) for f in (0,1) for q in (0,1) for o in (0,1)])
    counters=defaultdict(Counter)
    family=defaultdict(list)
    for axis,dim in [("target",5),("role",4),("order",3)]:
        for i,(a,g) in rows.items():
            if i[dim]: continue
            other=i[:dim]+(1,)+i[dim+1:]
            aa,gg=rows[other]
            c=counters[axis,i[1],i[2],int(g!=gg)]
            correct=int(a==g)+int(aa==gg)
            c["pairs"]+=1
            c["both"]+=correct==2
            c["one"]+=correct==1
            c["neither"]+=correct==0
            c["changed"]+=a!=aa
            if axis=="target": family[i[:3]].append(int(correct==2))
    save("pairs",[dict(axis=axis,form=f,task=q,switch=s,**c) for (axis,f,q,s),c in sorted(counters.items())])
    frows=[dict(slot=i,h=i//16,form=f,causal=st.mean(family[i,f,0]),arithmetic=st.mean(family[i,f,1])) for f in range(2) for i in range(128)]
    save("families",frows)
    transfer=frows[128:]
    ints=[dict(measure=key,**interval([r[key] for r in transfer])) for key in ("causal","arithmetic")]
    diff=interval([r["causal"]-r["arithmetic"] for r in transfer])
    primary=read(AN/"primary.json")
    assert abs(diff["mean"]-primary["delta"])<1e-12
    assert abs(diff["low"]-primary["interval_t"][0])<1e-5
    assert [sum(sum(family[i,1,q]) for i in range(128)) for q in (0,1)]==[primary[k]["both_correct"] for k in ("causal","control")]
    ints.extend([dict(measure="difference",**diff),dict(measure="bounded",mean=diff["mean"],low=primary["interval_bounded"][0],high=primary["interval_bounded"][1],se="",df="")])
    save("intervals",ints)
    policies=[]
    for tie,report in read(FIX/"policy_audit.json")["ties"].items():
        for name,c in report.items():
            def both(axis,s):
                return sum(n for flag,ok,n in c[axis+"_pairs"] if ok==2 and flag==s)
            policies.append(dict(policy=name,tie=int(tie),items=c["correct"],target_switch=both("target",1),target_stable=both("target",0),role_switch=both("role",1),role_stable=both("role",0),families_wrong=c["disagreement_families"]))
    save("policies",policies)
    worlds=lines(FIX/"worlds.jsonl")
    matrix=[]
    for w in worlds:
        matrix.append(dict(family=w["family_id"],p=w["p"],g=w["g"],b=w["b"],w0=w["weights"][0],w1=w["weights"][1],**{f"d{r}{k}":100*float(Fraction(**w["corners"][r][k])) for r in (0,1) for k in (0,1)}))
    save("quartets",matrix)
    w=worlds[96]
    save("example",[dict(role=r,group=s,off=w["tables"][r][s][0]/2,on=w["tables"][r][s][1]/2) for r in (0,1) for s in (0,1)])
    c16=EXP/"cohort_016"
    truth=keyed(lines(c16/"input/oracle_truth.jsonl"))
    tasks=keyed(lines(c16/"input/public_tasks.jsonl"))
    archive=read(c16/"primary_analysis.json")
    outputs=[]
    for arm,folder in [("F16","run_001_7b_f16"),("Q4_K_M","run_002_7b_q4_k_m")]:
        for resp in lines(c16/folder/"raw_responses.jsonl"):
            key=resp["task_id"]; item=tasks[key]; g=truth[key]
            vals=re.findall(r"off ([\d.]+)%, on ([\d.]+)%",item["prompt"])
            diffs=[Fraction(y)-Fraction(x) for x,y in vals]
            assert len(diffs)==2 and abs(diffs[0])!=abs(diffs[1])
            heuristic=int(min(diffs,key=abs)>0)
            choice=resp["response"]["choices"][0]
            assert choice["finish_reason"]=="stop"
            action=json.loads(choice["message"]["content"],object_pairs_hook=strict)
            assert heuristic==g["optimal_action"]
            first=item["presentation_order"]=="randomized_first"
            outputs.append(dict(arm=arm,id=key,family=g["family_id"],conflict=int(g["conflict"]),order=item["presentation_order"],random_gap=float(abs(diffs[0 if first else 1])),historical_gap=float(abs(diffs[1 if first else 0])),gold=g["optimal_action"],action=action,shortcut=heuristic))
    save("order016",outputs)
    grouped=defaultdict(list)
    for r in outputs:
        if r["conflict"] and r["arm"]=="Q4_K_M":
            sign=1 if r["order"]=="historical_first" else -1
            grouped[r["family"]].append(sign*int(r["gold"]==r["action"]))
    delta=[sum(v)/2 for v in grouped.values()]
    d=archive["primary_q4_conflict_order_effect"]
    assert len(delta)==96 and abs(st.mean(delta)-d["mean_difference"])<1e-12 and abs(st.stdev(delta)-d["family_level_sd"])<1e-12
    print("Raw journal, both archived keys, paired primary interval, Cohort 016 primary and all magnitude-rule predictions verified.")
if __name__=="__main__":
    main()
