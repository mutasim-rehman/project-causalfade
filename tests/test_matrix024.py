import json
import argparse
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from causalfade.matrix024 import prepare, validate, score, render
from causalfade.sensitivity import read_jsonl, digest, write_json, write_jsonl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cohort024 import model_inventory, analysis, source_hashes, build_models


class Matrix024Tests(unittest.TestCase):
    def test_fixture_and_strict_score(self):
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "fixture"
            prepare(dataset)
            self.assertEqual(validate(dataset)["tasks"], 1472)
            truth = read_jsonl(dataset / "oracle_truth.jsonl")
            self.assertEqual(sum(r["task_type"] == "decision" and r["contract"] == "neutral" for r in truth), 256)
            neutral = next(r for r in truth if r["task_type"] == "decision" and r["contract"] == "neutral")
            self.assertIn('{"choice":"X=1"}', render(neutral))
            raw = []
            for r in truth:
                target = r["randomized_name"] if r["task_type"] == "source_selection" else ("X=1" if r["causal_positive"] else "X=0") if r["task_type"] == "numerical_control" or r["contract"] == "neutral" else ("activate" if r["optimal_action"] else "leave_off")
                key = "governing_study" if r["task_type"] == "source_selection" else "larger" if r["task_type"] == "numerical_control" else "choice" if r["contract"] == "neutral" else "decision"
                raw.append({"task_id": r["task_id"], "response": {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({key: target})}}]}})
            rows = score(truth, raw)
            self.assertEqual(sum(r["correct"] for r in rows), 1472)
            raw[0]["response"]["choices"][0]["message"]["content"] = '{"decision":"activate","decision":"leave_off"}'
            self.assertFalse(score(truth, raw)[0]["valid_answer"])

    def test_model_inventory_rejects_mixed_revisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            a, b = base / "f16.gguf", base / "q4.gguf"
            a.write_bytes(b"f16"); b.write_bytes(b"q4")
            spec = [{"id": "mistral_f16", "lineage": "mistral", "precision": "F16", "path": str(a), "source_revision": "v1", "sha256": digest(a)},
                    {"id": "mistral_q4", "lineage": "mistral", "precision": "Q4_K_M", "path": str(b), "source_revision": "v2", "sha256": digest(b)}]
            path = base / "models.json"; path.write_text(json.dumps(spec))
            with self.assertRaisesRegex(ValueError, "one source revision"):
                model_inventory(path)
            spec[1]["source_revision"] = "v1"; path.write_text(json.dumps(spec))
            self.assertEqual(len(model_inventory(path)), 2)

    def test_archived_two_arm_analysis(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); dataset = base / "input"; prepare(dataset)
            tasks = read_jsonl(dataset / "public_tasks.jsonl")
            truth = read_jsonl(dataset / "oracle_truth.jsonl")
            server = base / "server"; server.write_bytes(b"server")
            models = []
            for precision in ("F16", "Q4_K_M"):
                path = base / (precision + ".gguf"); path.write_bytes(precision.encode())
                models.append({"id": "one_" + precision.lower(), "lineage": "one", "precision": precision,
                               "path": str(path), "source_revision": "r1", "sha256": digest(path)})
            runtime = {"threads": 1, "context": 2048, "gpu_layers": 0, "kv_precision": "f16",
                       "max_tokens": 64, "temperature": 0, "seed": 20261120, "request_timeout": 180}
            plan = {"dataset": str(dataset), "dataset_hashes": {n: digest(dataset / n) for n in ("manifest.json", "public_tasks.jsonl", "oracle_truth.jsonl")},
                    "source_hashes": source_hashes(), "server": str(server), "server_sha256": digest(server),
                    "models": models, "runtime": runtime}
            plan_path = base / "plan.json"; write_json(plan_path, plan)
            runs = base / "runs"
            raw = []
            for r in truth:
                target = r["randomized_name"] if r["task_type"] == "source_selection" else ("X=1" if r["causal_positive"] else "X=0") if r["task_type"] == "numerical_control" or r["contract"] == "neutral" else ("activate" if r["optimal_action"] else "leave_off")
                key = "governing_study" if r["task_type"] == "source_selection" else "larger" if r["task_type"] == "numerical_control" else "choice" if r["contract"] == "neutral" else "decision"
                raw.append({"task_id": r["task_id"], "response": {"choices": [{"finish_reason": "stop", "message": {"content": json.dumps({key: target})}}]}})
            for model in models:
                out = runs / model["id"]; out.mkdir(parents=True)
                write_json(out / "config.json", {"model": model, "dataset_hash": plan["dataset_hashes"]["manifest.json"],
                           "server_sha256": plan["server_sha256"], "source_hashes": plan["source_hashes"], "runtime": runtime})
                write_json(out / "schedule.json", tasks)
                write_jsonl(out / "raw_responses.jsonl", raw)
                write_json(out / "results.json", score(truth, raw))
                write_json(out / "status.json", {"status": "success"})
            target = base / "analysis.json"
            analysis(argparse.Namespace(plan=plan_path, runs=runs, out=target))
            result = json.loads(target.read_text())
            self.assertEqual(result["arms"][models[0]["id"]]["valid"], 1472)
            self.assertEqual(result["paired_precision"][models[1]["id"]]["effects"]["decision|neutral|0"]["estimate"], 0)

    def test_quant_builder_provenance_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp); f16 = base / "source-f16.gguf"; f16.write_bytes(b"GGUFsource")
            quantizer = base / "llama-quantize"; quantizer.write_bytes(b"binary")
            sources = base / "sources.json"
            sources.write_text(json.dumps([{"lineage": "one", "path": str(f16), "source_revision": "r1"}]))
            args = argparse.Namespace(sources=sources, quantizer=quantizer, out=base / "quants",
                                      models_out=base / "models.json", levels="Q8_0,Q4_K_M")
            def fake_run(command, **_kwargs):
                Path(command[2]).write_bytes(b"GGUF" + command[3].encode())
                return argparse.Namespace(returncode=0)
            with patch("cohort024.subprocess.run", side_effect=fake_run):
                build_models(args)
            inventory = model_inventory(args.models_out)
            self.assertEqual(len(inventory), 3)
            args.models_out = base / "models-second.json"
            with patch("cohort024.subprocess.run", side_effect=AssertionError("should reuse")):
                build_models(args)
            self.assertEqual(model_inventory(args.models_out), inventory)
