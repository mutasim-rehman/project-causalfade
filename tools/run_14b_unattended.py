"""Download, locally quantize, evaluate, analyze and publish the 14B follow-up."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "experiments/cohort_017"
WEIGHTS = Path.home() / "Desktop/CAUSALFADE/weights/gguf"
F16 = WEIGHTS / "qwen2.5-14b-instruct-f16.gguf"
REVISION = "608247a797d920aa2f94c1381d53bdc6a2a3b5b8"
SOURCE = f"https://huggingface.co/second-state/Qwen2.5-14B-Instruct-GGUF/resolve/{REVISION}/Qwen2.5-14B-Instruct-f16.gguf"
EXPECTED_F16_BYTES = 29547716448
QUANTIZER = ROOT / ".tools/llama-b12176/llama-quantize"
SERVER = ROOT / ".tools/llama-b12176/llama-server"
DATASET = ROOT / "experiments/cohort_016/input"
START = time.monotonic()


def now():
    return datetime.now(timezone.utc).isoformat()


def save(path, data):
    temp = path.with_name(path.name + ".tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n")
    temp.replace(path)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def valid(path, minimum):
    return path.is_file() and path.stat().st_size >= minimum and path.open("rb").read(4) == b"GGUF"


def stage(name, **details):
    save(COHORT / "automation_status.json", {"stage": name, "updated_utc": now(),
                                              "elapsed_seconds": round(time.monotonic() - START), **details})
    print(f"{now()} {name} {details}", flush=True)


def run(command, log):
    with log.open("a") as out:
        out.write(f"{now()} command: {' '.join(map(str, command))}\n")
        out.flush()
        subprocess.run(list(map(str, command)), cwd=ROOT, stdout=out,
                       stderr=subprocess.STDOUT, check=True)


def publish():
    archive = Path.home() / "Desktop/CAUSALFADE/runs/unmodified_paths_20261113_14b"
    subprocess.run([sys.executable, str(ROOT / "tools/normalize_run_paths.py"),
                    "--archive", str(archive), str(COHORT)], cwd=ROOT, check=True)
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0")
    subprocess.run(["git", "add", "experiments/cohort_017"], cwd=ROOT, env=env, check=True)
    changed = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode != 0
    if changed:
        subprocess.run(["git", "commit", "-m", "results: archive unattended 14B follow-up"],
                       cwd=ROOT, env=env, check=True)
    for attempt in range(3):
        result = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT,
                                env=env, capture_output=True, text=True, timeout=180)
        print(f"push attempt {attempt + 1}: {result.returncode} {result.stderr}", flush=True)
        if result.returncode == 0:
            return
        time.sleep(30 * (attempt + 1))
    raise RuntimeError("Git push failed after three attempts; local commit is retained")


def main():
    COHORT.mkdir(parents=True, exist_ok=True)
    WEIGHTS.mkdir(parents=True, exist_ok=True)
    if shutil.disk_usage(WEIGHTS).free < 65_000_000_000:
        raise RuntimeError("Less than 65 GB free; cannot safely stage F16, Q8 and Q4")
    if not (QUANTIZER.is_file() and SERVER.is_file()):
        raise FileNotFoundError("Pinned llama.cpp b12176 tools missing")
    stage("downloading_f16")
    if not valid(F16, EXPECTED_F16_BYTES):
        partial = F16.with_name(F16.name + ".part")
        run(["wget", "--continue", "--tries=10", "--waitretry=30", "--timeout=120",
             "--progress=dot:giga", "-O", partial, SOURCE], COHORT / "download.log")
        if partial.stat().st_size != EXPECTED_F16_BYTES or not valid(partial, EXPECTED_F16_BYTES):
            raise RuntimeError("Downloaded F16 size or GGUF header mismatch")
        partial.replace(F16)
    provenance = {"source_repo": "second-state/Qwen2.5-14B-Instruct-GGUF",
                  "source_revision": REVISION, "source_file": F16.name,
                  "source_bytes": F16.stat().st_size, "source_sha256": sha(F16),
                  "quantizer_sha256": sha(QUANTIZER), "quantizer": "llama.cpp b12176 CPU",
                  "method": "GGUF weight-only quantization; no imatrix"}
    save(COHORT / "model_provenance.json", provenance)
    for label, fmt, minimum in (("q8_0", "Q8_0", 14_000_000_000),
                                ("q4_k_m", "Q4_K_M", 8_000_000_000)):
        target = WEIGHTS / f"qwen2.5-14b-instruct-{label}.gguf"
        stage("quantizing_" + label)
        if not valid(target, minimum):
            partial = target.with_name(target.name + ".part")
            if partial.exists():
                partial.unlink()
            run([QUANTIZER, "--max-buffer-size", "1024", F16, partial, fmt, "8"],
                COHORT / f"quantize_{label}.log")
            if not valid(partial, minimum):
                raise RuntimeError(f"Invalid {label} quantization")
            partial.replace(target)
        provenance[label] = {"file": target.name, "bytes": target.stat().st_size,
                             "sha256": sha(target), "format": fmt}
        save(COHORT / "model_provenance.json", provenance)
    for index, label in enumerate(("q8_0", "q4_k_m"), 1):
        stage("running_" + label)
        out = COHORT / f"run_00{index}_14b_{label}"
        if out.exists():
            raise FileExistsError(f"Run directory already exists: {out}")
        run([sys.executable, ROOT / "tools/run_direct_pilot.py", "--server", SERVER,
             "--model", WEIGHTS / f"qwen2.5-14b-instruct-{label}.gguf",
             "--dataset", DATASET, "--out", out, "--families", "96",
             "--seed", "20261126", "--threads", "8", "--max-tokens", "48"],
            COHORT / f"runner_{label}.log")
        if json.loads((out / "status.json").read_text())["status"] != "success":
            raise RuntimeError(f"{label} arm did not complete")
    stage("analyzing")
    run([sys.executable, ROOT / "tools/analyze_14b_followup.py",
         "--q8", COHORT / "run_001_14b_q8_0", "--q4", COHORT / "run_002_14b_q4_k_m",
         "--truth", DATASET / "oracle_truth.jsonl", "--out", COHORT / "analysis.json"],
        COHORT / "analysis.log")
    stage("complete", duration_seconds=round(time.monotonic() - START))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        stage("failed", error=repr(exc))
        raise
    finally:
        try:
            publish()
        except Exception as exc:
            print(f"Publication failed: {exc!r}", file=sys.stderr, flush=True)
            raise
