"""Seal preflight evidence and verify detached lab signatures."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from tools.cohort029_prepare import ROOT, write
from tools.cohort029_runtime import load, sha
from causalfade.target_transport import TOTAL

CODE = (
    "causalfade/target_transport.py", "causalfade/target_forms.py",
    "tools/cohort029_prepare.py", "tools/cohort029_policies.py",
    "tools/verify_target_transport.py", "tools/cohort029_runtime.py",
    "tools/freeze_target_transport.py", "tools/run_target_transport.py",
    "tools/analyze_target_transport.py",
    "tests/test_target_transport_scm.py", "tests/test_target_transport_forms.py",
    "tests/test_target_transport_analysis.py", "tests/test_target_transport_runner.py",
)
DATA = ("forms.json", "schedule.json", "tasks.jsonl", "design.jsonl", "worlds.jsonl",
        "gold.jsonl", "public_oracle.jsonl", "fixture_audit.json", "policy_audit.json",
        "policy_rows_tie_0.jsonl.gz", "policy_rows_tie_1.jsonl.gz", "structural_diffs.json",
        "blind_review.json")
CLARIFICATION = ROOT / "experiments/cohort_029/policy-clarification.md"
ROLES = ("pi", "causal-lead", "statistician", "benchmark-engineer",
         "independent-reviewer", "transfer-author")


def frozen(candidate, preflight, evidence, protocol, out, policy_approval, trust):
    verify_signature(CLARIFICATION, policy_approval, trust, "pi")
    forms = load(candidate / "forms.json")
    tokens = load(preflight / "token_budget.json")
    inv = load(preflight / "inventory.json")
    gates = load(evidence / "gates.json")
    mock = load(evidence / "mock_recovery.json")
    coverage = load(evidence / "coverage.json")
    if forms["mock"] or sys.version_info[:2] != (3, 13) or forms["python"] != inv["python"]:
        raise ValueError("Formal fixture and preflight must share the locked Python 3.13 patch")
    if (tokens["tasks_sha256"] != sha(candidate / "tasks.jsonl") or
        tokens["model_sha256"] != inv["model_sha256"] or
        tokens["server_sha256"] != inv["server_sha256"] or
        set(tokens["counts"]) != set(load(candidate / "schedule.json")) or
        any(v["tokens"] + 48 > 2048 for v in tokens["counts"].values())):
        raise ValueError("Tokenizer report does not bind the complete deployment and fixture")
    policy = load(candidate / "policy_audit.json")
    if policy["policy_rule"] != "constant-rivals-v1" or policy["failures"] or mock["passed"] is not True:
        raise ValueError("Policy or mock preflight failed")
    if (set(coverage["scenarios"]) != {"constant", "rare", "balanced_extremes", "heterogeneous"} or
        coverage["coverage_primary"] not in {"t", "bounded"} or
        any(v["replications"] != 10000 for v in coverage["scenarios"].values())):
        raise ValueError("Coverage preflight has an invalid replicate count")
    if set(gates) != {str(i) for i in range(1, 8)}:
        raise ValueError("Seven pre-inference gate records are required. Authorization is gate eight.")
    gate_files = {}
    for record in gates.values():
        if not all(record.get(k) for k in
                   ("owner", "verifier", "artifact", "sha256", "predicate", "observed", "timestamp")):
            raise ValueError("Gate record has missing evidence")
        relative = Path(record["artifact"])
        if relative.is_absolute() or ".." in relative.parts or relative in (Path("gates.json"), Path(".")):
            raise ValueError("Evidence paths must be relative to the evidence directory")
        path = evidence / relative
        if record["pass"] is not True or sha(path) != record["sha256"]:
            raise ValueError(f"Gate evidence failed or changed: {relative}")
        gate_files[str(Path("evidence") / relative)] = path
    files = {f"fixture/{n}": candidate / n for n in DATA}
    files.update({f"deployment/{n}": preflight / n for n in ("inventory.json", "token_budget.json")})
    files.update({f"evidence/{n}": evidence / n for n in (
        "gates.json", "mock_recovery.json", "coverage.json",
        "form_review.md", "deviations.json")})
    files.update(gate_files)
    files["protocol.md"] = protocol
    files["policy-clarification.md"] = CLARIFICATION
    files["policy-clarification.sig"] = policy_approval
    files.update({f"source/{name}": ROOT / name for name in CODE})
    out.mkdir(parents=True, exist_ok=False)
    for n, source in files.items():
        dest = out / n
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, dest)
    manifest = dict(schema=1, protocol="CF-TP1", response_cap=TOTAL,
                    git_parent=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                                       text=True).strip(),
                    files={n: dict(sha256=sha(out / n), bytes=(out / n).stat().st_size)
                           for n in sorted(files)}, code={n: sha(ROOT / n) for n in CODE},
                    coverage_primary=coverage["coverage_primary"])
    write(out / "manifest.json", manifest)
    (out / "SHA256SUMS").write_text("".join(f"{v['sha256']}  {n}\n"
                                           for n, v in manifest["files"].items()))
    print(sha(out / "manifest.json"))


def verify_signature(payload, sig, trust, identity):
    with payload.open("rb") as data:
        subprocess.run(["ssh-keygen", "-Y", "verify", "-f", str(trust),
                        "-I", identity, "-n", "causalfade-cohort029", "-s", str(sig)],
                       stdin=data, stdout=subprocess.DEVNULL, check=True, timeout=15)


def authorization_signature(authorization):
    generated = authorization.with_suffix(authorization.suffix + ".sig")
    legacy = authorization.with_suffix(".sig")
    return legacy if legacy.is_file() and not generated.is_file() else generated



def verify(freeze, signatures, authorization, trust, run_path):
    path = freeze / "manifest.json"
    manifest = load(path)
    if manifest["schema"] != 1 or manifest["protocol"] != "CF-TP1" or manifest["response_cap"] != TOTAL:
        raise ValueError("Unexpected freeze schema, protocol, or response cap")
    for role in ROLES:
        verify_signature(path, signatures / f"{role}.sig", trust, role)
    verify_signature(authorization, authorization_signature(authorization), trust, "pi")
    auth = load(authorization)
    if (auth["manifest_sha256"] != sha(path) or auth["run_path"] != run_path or
        auth["authorized_responses"] != TOTAL or auth["authorized"] is not True):
        raise ValueError("Authorization does not match this freeze, run path and cap")
    for n, item in manifest["files"].items():
        rel = Path(n)
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("Invalid frozen file path")
        p = freeze / rel
        if p.stat().st_size != item["bytes"] or sha(p) != item["sha256"]:
            raise ValueError(f"Frozen artifact changed: {n}")
    if set(manifest["code"]) != set(CODE):
        raise ValueError("Frozen code set mismatch")
    for n, expected in manifest["code"].items():
        if sha(ROOT / n) != expected:
            raise ValueError(f"Frozen code changed: {n}")
    if sha(freeze / "policy-clarification.md") != sha(CLARIFICATION):
        raise ValueError("Frozen policy clarification does not match this runner")
    verify_signature(freeze / "policy-clarification.md", freeze / "policy-clarification.sig", trust, "pi")
    inv = load(freeze / "deployment/inventory.json")
    if auth["model_sha256"] != inv["model_sha256"] or auth["server_sha256"] != inv["server_sha256"]:
        raise ValueError("Authorization deployment mismatch")
    return sha(path)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for flag in ("candidate", "preflight", "evidence", "protocol", "out", "policy-approval", "trust"):
        cli.add_argument("--" + flag, type=Path, required=True)
    frozen(**vars(cli.parse_args()))
