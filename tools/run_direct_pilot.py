"""Run one CPU GGUF direct-response pilot with durable, append-only evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import signal
import socket
import subprocess
import sys
import time
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from causalfade.score import score


def now():
    return datetime.now(timezone.utc).isoformat()


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def save(path, value):
    staging = path.with_suffix(".tmp")
    staging.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    staging.replace(path)


def request(port, path, body=None, timeout=2):
    data = None if body is None else json.dumps(body).encode()
    req = Request(f"http://127.0.0.1:{port}{path}", data,
                  {"Content-Type": "application/json"})
    with urlopen(req, timeout=timeout) as response:
        return json.load(response)


def interrupted(_signal, _frame):
    raise KeyboardInterrupt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("server", "model", "dataset", "out"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--families", type=int, default=16)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20261110)
    parser.add_argument("--max-tokens", type=int, default=160)
    parser.add_argument("--evidence", choices=("exact", "sampled"), default="exact")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupted)
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    metadata = {"start_utc": now(), "python": platform.python_version(),
                "system": platform.platform(), "logical_cpus": os.cpu_count(),
                "git_revision": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    save(args.out / "metadata.json", metadata)
    save(args.out / "status.json", {"status": "running"})
    server = None
    status = {"status": "failed"}
    predictions = []
    tasks = []
    try:
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        command = [str(args.server.resolve()), "-m", str(args.model.resolve()),
                   "--host", "127.0.0.1", "--port", str(port), "-ngl", "0",
                   "-c", "2048", "-np", "1", "-t", str(args.threads),
                   "--cache-type-k", "f16", "--cache-type-v", "f16"]
        sampling = {"temperature": 0, "seed": args.seed, "max_tokens": args.max_tokens,
                    "cache_prompt": False, "stream": False}
        save(args.out / "config.json", {**vars(args), "command": command,
                                      "sampling": sampling} | {
             key: str(getattr(args, key).resolve()) for key in ("server", "model", "dataset", "out")})
        with args.model.open("rb") as model:
            metadata["model_sha256"] = hashlib.file_digest(model, "sha256").hexdigest()
        manifest = json.loads((args.dataset / "manifest.json").read_text())
        for name, expected in manifest["file_sha256"].items():
            actual = hashlib.sha256((args.dataset / name).read_bytes()).hexdigest()
            if actual != expected:
                raise ValueError(f"Dataset digest mismatch: {name}")
        save(args.out / "dataset_manifest.json", manifest)
        public = read_rows(args.dataset / "public_tasks.jsonl")
        rng = random.Random(args.seed)
        families = sorted({row["family_id"] for row in public})
        chosen = set(rng.sample(families, args.families))
        tasks = [row for row in public if row["family_id"] in chosen
                 and row["evidence_mode"] == args.evidence]
        rng.shuffle(tasks)
        save(args.out / "schedule.json", tasks)
        with (args.out / "stdout.log").open("w") as stdout, (args.out / "stderr.log").open("w") as stderr:
            server = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            deadline = time.monotonic() + 180
            while True:
                if server.poll() is not None:
                    raise RuntimeError(f"Inference server exited: {server.returncode}")
                try:
                    request(port, "/health")
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        raise TimeoutError("Inference server startup exceeded 180 seconds")
                    time.sleep(0.5)
            with (args.out / "raw_responses.jsonl").open("x") as raw:
                for task in tasks:
                    started = time.monotonic()
                    record = {"task_id": task["task_id"], "started_utc": now()}
                    parsed = {}
                    try:
                        response = request(port, "/v1/chat/completions", {
                            **sampling, "messages": [{"role": "user", "content": task["prompt"]}]
                        }, timeout=180)
                        record["response"] = response
                        try:
                            value = json.loads(response["choices"][0]["message"]["content"])
                            if isinstance(value, dict):
                                parsed = {key: value[key] for key in
                                          ("activate", "ate_estimate", "adjustment_set") if key in value}
                            record["parse_status"] = "object" if isinstance(value, dict) else "non_object"
                        except (KeyError, IndexError, TypeError, ValueError):
                            record["parse_status"] = "invalid_json_or_response"
                    except (KeyboardInterrupt, Exception) as error:
                        record["execution_error"] = repr(error)
                        raise
                    finally:
                        record["duration_seconds"] = time.monotonic() - started
                        record["prediction"] = {**parsed, "task_id": task["task_id"]}
                        raw.write(json.dumps(record) + "\n")
                        raw.flush()
                        os.fsync(raw.fileno())
                    predictions.append(record["prediction"])
        status = {"status": "success"}
    except KeyboardInterrupt:
        status = {"status": "interrupted", "reason": "Signal received"}
        raise
    except Exception as error:
        status = {"status": "timeout" if isinstance(error, TimeoutError) else "failed",
                  "reason": repr(error)}
        raise
    finally:
        if server is not None and server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        try:
            ids = {row["task_id"] for row in tasks}
            if ids:
                truth = [r for r in read_rows(args.dataset / "oracle_truth.jsonl") if r["task_id"] in ids]
                rows = score(truth, predictions)
                save(args.out / "results.json", rows)
                save(args.out / "metrics.json", {
                    "scheduled": len(rows), "completed": len(predictions),
                    "valid_actions": sum(r["valid_action"] for r in rows),
                    **{label: sum(r["correct"] for r in rows if r["conflict"] == flag)
                       / sum(r["conflict"] == flag for r in rows)
                       for label, flag in (("aligned_accuracy", False), ("conflict_accuracy", True))}
                })
        except Exception as error:
            status = {"status": "failed", "reason": f"Scoring failed: {error!r}", "execution": status}
            raise
        finally:
            metadata.update(end_utc=now(), duration_seconds=time.monotonic() - start)
            save(args.out / "metadata.json", metadata)
            save(args.out / "status.json", status)


if __name__ == "__main__":
    main()
