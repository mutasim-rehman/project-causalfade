"""Paired, eight-family development analysis for cohort 022."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
from statistics import mean

from replication_pilot import load_run, load, source_hashes
from causalfade.guidance import analyze_rows
from causalfade.sensitivity import cluster_interval, digest, write_json


def analyze(dataset, qwen, independent, out):
    qconfig, qrows = load_run(qwen, dataset)
    iconfig, irows = load_run(independent, dataset)
    if qconfig["checkpoint"] != "qwen_f16" or iconfig["checkpoint"] != "mistral_q4":
        raise ValueError("Declared checkpoint roles mismatch")
    if qconfig["dataset_manifest_sha256"] != iconfig["dataset_manifest_sha256"] or qconfig["model_sha256"] == iconfig["model_sha256"]:
        raise ValueError("Fixture or model provenance mismatch")
    def central(rows):
        groups=defaultdict(lambda:defaultdict(list))
        for r in rows:
            if r["task_type"] in ("randomized_only","ordinary"):
                groups[r["family_id"]][r["task_type"]].append(r["correct"])
        return {f:mean(v["randomized_only"])-mean(v["ordinary"]) for f,v in groups.items()}
    qcentral,icentral=central(qrows),central(irows)
    families=sorted(qcentral)
    if families != sorted(icentral) or len(families)!=8:
        raise ValueError("Family pairing mismatch")
    out_data={"classification":"development_only","dataset_manifest_sha256":digest(Path(dataset)/"manifest.json"),
              "source_sha256":source_hashes(),"checkpoint_config_sha256":{"qwen_f16":digest(Path(qwen)/"config.json"),"mistral_q4":digest(Path(independent)/"config.json")},
              "qwen_f16":analyze_rows(qrows),"mistral_q4":analyze_rows(irows),
              "central_randomized_only_minus_ordinary":{"qwen_f16":cluster_interval([qcentral[f] for f in families]),
                  "mistral_q4":cluster_interval([icentral[f] for f in families]),
                  "mistral_minus_qwen":cluster_interval([icentral[f]-qcentral[f] for f in families])},
              "limitations":["Eight paired development families; intervals resample families.","Independent model is Q4_K_M while Qwen is F16: checkpoint family and precision are bundled.","Cross-request associations do not identify mediation."]}
    out=Path(out)
    if out.exists() or out.with_suffix(".md").exists():raise FileExistsError("Analysis outputs are not overwritten")
    write_json(out,out_data)
    lines=["# Cohort 022 independent checkpoint-family development replication","","Both models use the identical fresh fixture; this is not confirmatory.",""]
    for name in ("qwen_f16","mistral_q4"):
        lines.extend([f"## {name}",""])
        for kind,cell in out_data[name]["by_task_type"].items():
            lines.append(f'- {kind}: {cell["correct"]}/{cell["scheduled"]} correct; {cell["valid"]} valid.'+(f' Activation {cell["activation_rate_valid"]:.3f}.' if "activation_rate_valid" in cell and cell["activation_rate_valid"] is not None else ""))
        lines.append("")
    lines.extend(["## Central randomized-only minus ordinary accuracy",""])
    for key,value in out_data["central_randomized_only_minus_ordinary"].items():
        lines.append(f'- {key}: {value["estimate"]:+.3f}; eight-family percentile interval {value["family_percentile_95"]}.')
    lines.extend(["","See JSON for direction, order, guidance, joint-request and action-flip strata.","The independent reference is quantized; family and precision are bundled. No mechanistic or confirmatory claim follows."])
    out.with_suffix(".md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return out_data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ("dataset","qwen","independent","out"):p.add_argument(f"--{name}",type=Path,required=True)
    a=p.parse_args();analyze(a.dataset,a.qwen,a.independent,a.out)
    print(json.dumps({"analysis":str(a.out),"report":str(a.out.with_suffix('.md'))}))
if __name__=="__main__":main()
