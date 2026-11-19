"""Reproduce cohort 025 and register the supplied cross-disciplinary proposals."""
import hashlib
import json
import math
from pathlib import Path
from analyze_cohort025_archive import analyze

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('/home/i242514/Desktop/CausalFade_Cross_Disciplinary_Research_Investigation.docx')
EXPECTED_SOURCE_SHA256 = 'd060db47408d520cdee345940dd4b00e75cd1805d62655ffe7b2b1e81aa5c1d7'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equivalent(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(equivalent(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(equivalent(x, y) for x, y in zip(a, b))
    if isinstance(a, float) and isinstance(b, float):
        return math.isclose(a, b, rel_tol=0, abs_tol=1e-12)
    return a == b


def build():
    if digest(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise ValueError('Investigation document differs from the reviewed source')
    reproduced = analyze()
    saved_path = ROOT / 'experiments/cohort_025/archive_methods_screen.json'
    if not equivalent(reproduced, json.loads(saved_path.read_text(encoding='utf-8'))):
        raise ValueError('Cohort 025 archive analysis did not reproduce')
    return {
        'classification': 'post-outcome retrospective reproduction and applicability audit',
        'source_document_sha256': EXPECTED_SOURCE_SHA256,
        'cohort_025_analysis_sha256': digest(saved_path),
        'reproduced_run_count': sum(map(len, reproduced['inventory'].values())),
        'reproduced_source_cohorts': len(reproduced['source_cohorts']),
        'proposals': {
            'A_graph_switch': {'status': 'unavailable', 'reason': 'No observationally identical alternate-graph pairs or no-change graph controls'},
            'B_grading': {'status': 'limited', 'reason': 'Only a two-point causal strength pilot with fixed observational magnitude'},
            'C_rescue': {'status': 'limited', 'reason': 'Source-guidance prompts exist; no complete source-by-calculation factorial or matched placebo'},
            'signal_detection': {'status': 'descriptive_reproduced', 'reason': 'Scheduled validity and binary response counts exist; latent parameters not identified'},
            'information_dependence': {'status': 'descriptive_reproduced', 'reason': 'Plug-in estimates exist; eight families and post-outcome selection'},
            'transportability': {'status': 'unavailable', 'reason': 'No target-population switches'},
            'neural_and_timing': {'status': 'unavailable', 'reason': 'No precision restoration, logits, activations or validated cognitive timing'},
        },
    }


if __name__ == '__main__':
    target = ROOT / 'experiments/cohort_025_1/archive_investigation.json'
    target.write_text(json.dumps(build(), indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(target)
