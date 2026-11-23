"""Operational checkpoint amendment for the frozen cohort 028 runner.

Scientific fixture, requests, scorer, calculator, gates and resume keys remain in
cohort028_run.py. This launcher changes Git commit cadence only.
"""
import argparse
import json
import time
from pathlib import Path
import cohort028_run as original

BASE = original.BASE
AMENDMENT = BASE / 'amendments' / 'hourly_checkpoint_2026-11-23.json'
HOUR_SECONDS = 3600
_last_commit_mono = time.monotonic()


def due(now, last, finished):
    """Commit only after one hour or after a complete analyzed model arm."""
    return finished or now - last >= HOUR_SECONDS


def verify_amendment():
    policy = json.loads(AMENDMENT.read_text(encoding='utf-8'))
    if policy['policy'] != 'hourly_or_model_complete' or policy['interval_seconds'] != HOUR_SECONDS:
        raise ValueError('Unknown checkpoint amendment')
    if original.sha(original.BASE / 'plan.json') != policy['original_plan_sha256']:
        raise ValueError('Scientific plan changed')
    if original.sha(original.BASE / 'manifest.json') != policy['original_manifest_sha256']:
        raise ValueError('Frozen manifest changed')
    if original.sha(original.ROOT / 'tools/cohort028_run.py') != policy['original_runner_sha256']:
        raise ValueError('Scientific runner changed')
    if original.sha(Path(__file__)) != policy['hourly_launcher_sha256']:
        raise ValueError('Hourly launcher changed')
    original.verify()
    return policy


def commit_snapshot(message, push, include_live=True):
    paths = [BASE / 'runs', BASE / 'pipeline_status.json']
    if (BASE / 'token_preflight.json').exists():
        paths.append(BASE / 'token_preflight.json')
    if include_live and (BASE / 'live.log').exists():
        paths.append(BASE / 'live.log')
    original.commit_paths([p for p in paths if p.exists()], message, push)


def checkpoint(out, arm, split, done, total, push):
    global _last_commit_mono
    original.atomic(out / 'progress.json', {
        'arm': arm, 'split': split, 'completed': done,
        'total': total, 'utc': original.utc(),
    })
    finished = done == total and (out / 'analysis.json').exists()
    if done == total and not finished:
        return  # The final request is saved; wait for the model analysis.
    now = time.monotonic()
    if not due(now, _last_commit_mono, finished):
        return
    reason = 'model_complete' if finished else 'hourly'
    original.event(out, 'git_checkpoint', completed=done, total=total,
                   policy='hourly_or_model_complete', reason=reason)
    commit_snapshot(f'Cohort 028 {reason} {split} {arm} {done}/{total}', push)
    _last_commit_mono = time.monotonic()
    print(f'Git checkpoint ({reason}): {split} {arm} {done}/{total}', flush=True)


def pipeline_checkpoint(push=True):
    # The original runner calls this at start, interruption and terminal state.
    # Start/interruption are locally durable and await the next hourly/model
    # commit. A terminal status is saved once all model work has finished.
    status = json.loads((BASE / 'pipeline_status.json').read_text())['status']
    if status in ('validation_complete', 'stopped_by_gate'):
        commit_snapshot('Cohort 028 final pipeline status', push)


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    arm = sub.add_parser('run-arm')
    arm.add_argument('split', choices=('development', 'validation'))
    arm.add_argument('model_id')
    sub.add_parser('run-all')
    parser.add_argument('--no-push', action='store_true')
    args = parser.parse_args()
    verify_amendment()
    original.checkpoint = checkpoint
    original.pipeline_checkpoint = pipeline_checkpoint
    if args.command == 'run-arm':
        print(json.dumps(original.run_arm(args.split, args.model_id,
                                         not args.no_push), indent=2))
    else:
        original.run_all(not args.no_push)


if __name__ == '__main__':
    main()
