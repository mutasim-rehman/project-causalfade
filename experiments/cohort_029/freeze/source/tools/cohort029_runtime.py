"""Pinned deployment inventory and tokenizer-only preflight."""

import argparse
import contextlib
import hashlib
import http.client
import json
import os
import platform
import secrets
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from tools.cohort029_prepare import ROOT, write
from causalfade.target_transport import digest, encode

ARCHIVE = ROOT / "experiments/cohort_016"
SERVER_ARGS = ("-ngl", "0", "-c", "2048", "-np", "1", "-t", "8",
               "--cache-type-k", "f16", "--cache-type-v", "f16")
SAMPLING = dict(temperature=0, seed=20261126, max_tokens=48, cache_prompt=False, stream=False)
PORT = 48229
SERVER = ROOT / ".tools/llama-b12176/llama-server"
MODEL = Path.home() / "Desktop/CAUSALFADE/weights/gguf/qwen2.5-7b-instruct-q4_k_m.gguf"


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def rows(path):
    with path.open("rb") as f:
        return [json.loads(line) for line in f]


def inventory(server, model, scratch):
    frozen = load(ARCHIVE / "frozen_run_plan.json")
    metadata = load(ARCHIVE / "run_002_7b_q4_k_m/metadata.json")
    config = load(ARCHIVE / "run_002_7b_q4_k_m/config.json")
    if sys.version_info[:2] != (3, 13):
        raise ValueError("Formal deployment requires Python 3.13")
    model_hash, server_hash = sha(model), sha(server)
    if model_hash != frozen["model_q4_k_m"]["sha256"] or model_hash != metadata["model_sha256"]:
        raise ValueError("Model digest differs from archived cohort 016")
    if server_hash != frozen["runtime_sha256"] or tuple(config["command"][-12:]) != SERVER_ARGS:
        raise ValueError("Server or runtime differs from archived cohort 016")
    if config["sampling"] != SAMPLING:
        raise ValueError("Sampling differs from archived cohort 016")
    if (os.process_cpu_count() or 0) < 8 or shutil.disk_usage(scratch).free < 512*1024**2:
        raise ValueError("Need eight permitted CPUs and at least 512 MiB free for run data")
    libraries = {}
    for path in sorted(server.resolve().parent.glob("*.so*")):
        if path.is_file() and not path.is_symlink():
            libraries[path.name] = sha(path)
    if not libraries:
        raise ValueError("Archived server libraries are unavailable")
    return dict(model_sha256=model_hash, server_sha256=server_hash, libraries=libraries,
                python=platform.python_version(), dependencies={"python_stdlib_only": True},
                cpu=platform.machine(), cpu_allowed=os.process_cpu_count(),
                sampling=SAMPLING, server_args=list(SERVER_ARGS),
                source="Qwen/Qwen2.5-7B-Instruct", license="Apache-2.0",
                archive_freeze_sha256=sha(ARCHIVE / "frozen_run_plan.json"),
                archive_config_sha256=sha(ARCHIVE / "run_002_7b_q4_k_m/config.json"))


def request(port, token, endpoint, payload=None, timeout=120):
    with contextlib.closing(http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)) as conn:
        conn.request("POST" if payload is not None else "GET", endpoint,
                     None if payload is None else encode(payload),
                     {"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
        reply = conn.getresponse()
        raw = reply.read()
        if reply.status != 200:
            raise RuntimeError(f"{endpoint} returned HTTP {reply.status}")
        return json.loads(raw)


@contextlib.contextmanager
def serving(server, model, port, log):
    # A private API token identifies this process even if the port is taken.
    token = secrets.token_hex(32)
    env = {"PATH": os.defpath, "LANG": "C.UTF-8"}
    args = [str(server.resolve()), "-m", str(model.resolve()), "--host", "127.0.0.1",
            "--port", str(port), "--api-key", token, *SERVER_ARGS]
    with log.open("ab", buffering=0) as out:
        proc = subprocess.Popen(args, env=env, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=out)
        try:
            until = time.monotonic() + 180
            while time.monotonic() < until:
                if proc.poll() is not None:
                    raise RuntimeError(f"llama-server exited with status {proc.returncode}. See {log}")
                try:
                    props = request(port, token, "/props", timeout=2)
                    if Path(props.get("model_path", "")).resolve() == model.resolve():
                        # /props is public on some builds; /v1/models must require our private token.
                        request(port, token, "/v1/models", timeout=2)
                        break
                except (OSError, RuntimeError, ValueError, http.client.HTTPException):
                    pass
                time.sleep(0.5)
            else:
                raise RuntimeError(f"Archived server did not become ready. See {log}")
            yield token, props
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()


def template_identity(props):
    text = props.get("chat_template")
    if not isinstance(text, str) or not text:
        raise ValueError("Archived runtime did not expose its chat template")
    return digest(text.encode())


def chat_counts(port, token, tasks):
    def count(row):
        applied = request(port, token, "/apply-template", {"messages": row["messages"]})
        prompt = applied["prompt"]
        ids = request(port, token, "/tokenize",
                      {"content": prompt, "add_special": True, "parse_special": True})["tokens"]
        if not isinstance(ids, list) or not ids or any(type(i) is not int for i in ids):
            raise ValueError("Tokenizer returned malformed token IDs")
        return (row["task_id"], dict(tokens=len(ids), chat_sha256=digest(prompt.encode()),
                                     token_ids_sha256=digest(encode(ids))))
    with ThreadPoolExecutor(max_workers=4) as worker:
        return dict(worker.map(count, tasks))


def token_budget(candidate, out, server, model, port):
    out.mkdir(parents=True, exist_ok=False)
    local = inventory(server, model, out)
    write(out / "inventory.json", local)
    tasks = rows(candidate / "tasks.jsonl")
    with serving(server, model, port, out / "server.local.log") as (token, props):
        counts = chat_counts(port, token, tasks)
    if len(counts) != 4096 or any(value["tokens"] + 48 > 2048 for value in counts.values()):
        raise ValueError("Complete chat token budget failed")
    write(out / "token_budget.json", dict(context=2048, completion=48, counts=counts,
          template_sha256=template_identity(props), template=props["chat_template"],
          tasks_sha256=sha(candidate / "tasks.jsonl"), model_sha256=local["model_sha256"],
          server_sha256=local["server_sha256"]))


def deployment_args(cli):
    cli.add_argument("--server", type=Path, default=SERVER)
    cli.add_argument("--model", type=Path, default=MODEL)
    cli.add_argument("--port", type=int, default=PORT)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--candidate", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    deployment_args(cli)
    a = cli.parse_args()
    token_budget(a.candidate, a.out, a.server, a.model, a.port)
