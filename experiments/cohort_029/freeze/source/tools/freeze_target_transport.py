"""Rebuild the scientific fixture and atomically freeze verified collection inputs."""

import argparse
import platform
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from tools.cohort029_prepare import ROOT, prepare, write
from tools.cohort029_runtime import load, sha
from causalfade.target_transport import TOTAL, digest

CODE = (
    "causalfade/target_transport.py", "causalfade/target_forms.py",
    "tools/cohort029_prepare.py", "tools/cohort029_policies.py",
    "tools/verify_target_transport.py", "tools/cohort029_runtime.py",
    "tools/freeze_target_transport.py", "tools/run_target_transport.py",
    "tools/analyze_target_transport.py",
    "tests/test_target_transport_scm.py", "tests/test_target_transport_forms.py",
    "tests/test_target_transport_analysis.py", "tests/test_target_transport_runner.py",
    "tests/test_target_transport_freeze.py",
)
DATA = ("forms.json", "schedule.json", "tasks.jsonl", "design.jsonl", "worlds.jsonl",
        "gold.jsonl", "public_oracle.jsonl", "fixture_audit.json", "policy_audit.json",
        "policy_rows_tie_0.jsonl.gz", "policy_rows_tie_1.jsonl.gz", "structural_diffs.json",
        "blind_review.json")
BASE = ROOT / "experiments/cohort_029"
CLARIFICATION = BASE / "policy-clarification.md"
EVIDENCE = ("mock_recovery.json", "coverage.json", "provenance.json")


def validate_preflight(fixture, deployment):
    forms = load(fixture / "forms.json")
    inv = load(deployment / "inventory.json")
    tokens = load(deployment / "token_budget.json")
    if forms["mock"] or not platform.python_version().startswith("3.13."):
        raise ValueError("Formal freeze requires a non-mock fixture and Python 3.13")
    if forms["python"] != platform.python_version() or inv["python"] != forms["python"]:
        raise ValueError("Candidate, preflight and freeze require the same Python patch")
    schedule = load(fixture / "schedule.json")
    if not tokens["template"] or digest(tokens["template"].encode()) != tokens["template_sha256"]:
        raise ValueError("Token preflight chat template digest mismatch")
    if (tokens["tasks_sha256"] != sha(fixture / "tasks.jsonl")
        or tokens["model_sha256"] != inv["model_sha256"]
        or tokens["server_sha256"] != inv["server_sha256"]
        or (tokens["context"], tokens["completion"]) != (2048, 48)
        or len(set(schedule)) != TOTAL or set(tokens["counts"]) != set(schedule)
        or any(type(row["tokens"]) is not int or not 0 < row["tokens"] <= 2000
               or not re.fullmatch(r"[0-9a-f]{64}", row["chat_sha256"])
               or not re.fullmatch(r"[0-9a-f]{64}", row["token_ids_sha256"])
               for row in tokens["counts"].values())):
        raise ValueError("Token preflight is incomplete, over budget or belongs to different inputs")


def validate_candidate(candidate, preflight, authorship, review, stage, scratch):
    from tools.analyze_target_transport import calibrate, mock_run

    fixture = stage / "fixture"
    deployment = stage / "deployment"
    deployment.mkdir()
    for name in ("inventory.json", "token_budget.json"):
        shutil.copyfile(preflight / name, deployment / name)
    validate_preflight(candidate, deployment)
    note = dict(authorship=authorship, review=review, forms_sha256=sha(candidate / "forms.json"))
    for field in ("authorship", "review"):
        if not note[field].strip():
            raise ValueError(f"Describe actual {field}, or state unavailable")
        print(f"Transfer {field}: {note[field]}")
    # Recompute the oracles, balance, switch cells, prompt diffs and rival policies.
    transfer = scratch / "transfer.json"
    write(transfer, load(candidate / "forms.json")["transfer"])
    prepare(fixture, transfer, False)
    for name in DATA:
        if sha(candidate / name) != sha(fixture / name):
            raise ValueError(f"Candidate disagrees with deterministic validation: {name}")
    validate_preflight(fixture, deployment)
    evidence = stage / "evidence"
    evidence.mkdir()
    write(evidence / "provenance.json", note)
    mock_run(fixture, scratch / "mock-run")
    shutil.copyfile(scratch / "mock-run/mock_recovery.json", evidence / "mock_recovery.json")
    calibrate(evidence / "coverage.json")


def required_files():
    files = {f"fixture/{name}" for name in DATA}
    files.update(f"source/{name}" for name in CODE)
    files.update(f"evidence/{name}" for name in EVIDENCE)
    return files | {"protocol.md", "policy-clarification.md", "deployment/inventory.json",
                    "deployment/token_budget.json"}


def frozen(candidate, preflight, protocol, out, authorship, review):
    if out.exists():
        raise ValueError(f"Freeze already exists; refusing overwrite: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=out.parent) as temp:
        scratch = Path(temp)
        stage = scratch / "freeze"
        stage.mkdir()
        validate_candidate(candidate, preflight, authorship, review, stage, scratch)
        shutil.copyfile(protocol, stage / "protocol.md")
        shutil.copyfile(CLARIFICATION, stage / "policy-clarification.md")
        for name in CODE:
            dest = stage / "source" / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, dest)
        files = {name: dict(sha256=sha(stage / name), bytes=(stage / name).stat().st_size)
                 for name in sorted(required_files())}
        manifest = dict(schema=2, protocol="CF-TP1", response_cap=TOTAL, files=files,
                        coverage_primary=load(stage / "evidence/coverage.json")["coverage_primary"],
                        git_parent=subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                           cwd=ROOT, text=True).strip())
        write(stage / "manifest.json", manifest)
        (stage / "manifest.sha256").write_text(sha(stage / "manifest.json") + "\n")
        verify(stage)
        stage.rename(out)
    print(f"Frozen {out}: {sha(out / 'manifest.json')}")


def verify(freeze):
    path = freeze / "manifest.json"
    checksum = freeze / "manifest.sha256"
    if not path.is_file() or not checksum.is_file():
        raise ValueError(f"Missing frozen manifest or checksum in {freeze}. Complete preparation and freeze first.")
    manifest_hash = sha(path)
    if manifest_hash != checksum.read_text().strip():
        raise ValueError("Frozen manifest checksum mismatch")
    manifest = load(path)
    if (manifest["schema"], manifest["protocol"], manifest["response_cap"]) != (2, "CF-TP1", TOTAL):
        raise ValueError("Unexpected freeze schema, protocol or response cap")
    if set(manifest["files"]) != required_files():
        raise ValueError("Frozen artifact set mismatch")
    for name, item in manifest["files"].items():
        file = freeze / name
        if file.stat().st_size != item["bytes"] or sha(file) != item["sha256"]:
            raise ValueError(f"Frozen artifact changed: {name}")
    for name in CODE:
        if sha(ROOT / name) != manifest["files"][f"source/{name}"]["sha256"]:
            raise ValueError(f"Frozen code changed: {name}")
    if sha(CLARIFICATION) != manifest["files"]["policy-clarification.md"]["sha256"]:
        raise ValueError("Frozen policy clarification differs from the local version")
    return manifest_hash


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ("candidate", "preflight", "out"):
        cli.add_argument("--" + name, type=Path, required=True)
    cli.add_argument("--protocol", type=Path, default=BASE / "CF-TP1-v1.0.md")
    cli.add_argument("--authorship", default="Independent authorship undocumented; no independence claim.")
    cli.add_argument("--review", default="Independent review undocumented; no independent review claim.")
    try:
        frozen(**vars(cli.parse_args()))
    except (ValueError, OSError, KeyError) as exc:
        cli.exit(1, f"Freeze failed: {exc}\n")
