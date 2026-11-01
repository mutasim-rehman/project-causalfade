"""Reproducible synthetic parameter recovery and model-misspecification checks."""
import argparse
import csv
import json
import platform
from pathlib import Path
import numpy as np
from .processing import probabilities, fit_counts, bootstrap_fit_test, fit_logistic

SCENARIOS = {
    'interior': (.65, .45, .50),
    'lower_causal_sensitivity': (.35, .45, .50),
    'higher_conditional_association': (.65, .75, .50),
    'action_bias': (.65, .45, .80),
    'near_causal_boundary': (.98, .45, .50),
    'near_association_boundary': (.40, .98, .50),
}


def run(out, seed=20261101, repetitions=200, bootstrap=500):
    if repetitions < 2 or bootstrap < 1:
        raise ValueError('Need at least two repetitions and one bootstrap replicate.')
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    rows, summaries = [], []
    for name, theta in SCENARIOS.items():
        for n in (50, 200, 1000):
            y = rng.binomial(n, probabilities(*theta), size=(repetitions, 4))
            fits = fit_counts(y, n)
            est = fits['parameters']
            summary = dict(scenario=name, n_per_cell=n, repetitions=repetitions,
                           truth=dict(zip(('C','A','B'), theta)),
                           nonconverged=int(np.sum(~fits['converged'])),
                           near_simplex_boundary=int(np.sum(np.min(fits['weights'], axis=1) < 1e-5)),
                           parameters={})
            for j, label in enumerate(('C','A','B')):
                finite = np.isfinite(est[:, j]) & fits['converged']
                summary['parameters'][label] = dict(
                    bias=float(np.mean(est[finite, j]-theta[j])) if np.any(finite) else None,
                    rmse=float(np.sqrt(np.mean((est[finite, j]-theta[j])**2))) if np.any(finite) else None,
                    undefined_count=int(np.sum(~np.isfinite(est[:, j]))),
                    excluded_nonconverged_count=int(np.sum(~fits['converged'])),
                    used_repetitions=int(np.sum(finite)))
            summaries.append(summary)
            for i in range(repetitions):
                rows.append(dict(scenario=name, n_per_cell=n, replicate=i,
                                 true_C=theta[0],true_A=theta[1],true_B=theta[2],
                                 estimated_C=float(est[i,0]), estimated_A=float(est[i,1]),estimated_B=float(est[i,2]),
                                 converged=bool(fits['converged'][i])))
    # Recovery alone is not enough: test behavior generated outside the model.
    integration_p = 1/(1+np.exp(-(np.array([0., 1., 1., 2.])*3-3)))
    asymmetric_p = 1/(1+np.exp(-np.array([-2., 1., 2., 5.])))
    validation = {}
    for name, p in [('tree_generated', probabilities(.65,.45,.5)),
                    ('observationally_equivalent_logistic', integration_p),
                    ('incompatible_logistic', asymmetric_p)]:
        n = 2000
        y = rng.binomial(n, p)
        test_y = rng.binomial(n, p)
        tree = fit_counts(y,n)
        logistic = fit_logistic(y,np.full(4,n))
        validation[name] = dict(
            generating_probabilities=p.tolist(),
            fit_test=bootstrap_fit_test(y,n,rng,bootstrap),
            logistic_converged=logistic['converged'],
            heldout_log_loss={key: float(-np.sum(test_y*np.log(np.clip(q,1e-14,1-1e-14))+(n-test_y)*np.log1p(-np.clip(q,1e-14,1-1e-14)))/(4*n))
                              for key,q in [('processing_tree',tree['probabilities'][0]),('logistic_integration',logistic['probabilities'])]})
    # Bootstrap intervals for one illustrative interior fit, not a coverage study.
    y = rng.binomial(500, probabilities(.65,.45,.5))
    fitted = fit_counts(y,500)
    by = rng.binomial(500,fitted['probabilities'][0],size=(bootstrap,4))
    bf = fit_counts(by,500)
    intervals={}
    for j,k in enumerate(('C','A','B')):
        finite=np.isfinite(bf['parameters'][:,j])
        intervals[k] = dict(estimate=float(fitted['parameters'][0,j]),
                           percentile_95_interval=np.quantile(bf['parameters'][finite,j],[.025,.975]).tolist() if np.any(finite) else None,
                           undefined_bootstrap_count=int(np.sum(~finite)))
    result=dict(status='synthetic_parameter_recovery_not_LLM_or_quantization_results',seed=seed,
                python_version=platform.python_version(),numpy_version=np.__version__,
                repetitions=repetitions,bootstrap_replicates=bootstrap,
                sample_size_note='n_per_cell; each replicate has four times that many independent synthetic responses',
                recovery=summaries,model_checks=validation,illustrative_intervals=intervals,
                interval_nonconverged=int(np.sum(~bf['converged'])),
                limitations=['Pooled homogeneous MLE, not hierarchical Bayesian inference.',
                             'No empirical LLM trials, power calculation, or interval-coverage validation.',
                             'A/B recovery is intrinsically weak near boundaries; parameters are model-dependent.',
                             'Model-generated independent binomial trials are not a model of independent LLM checkpoints.'])
    (out/'parameter_recovery.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    with (out/'recovery_replicates.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    lines=['# Synthetic validation results','',
           '**These results contain no LLM responses and no quantized-model measurements.**','',
           f'Seed: {seed}. Independent simulation repetitions per scenario/sample-size: {repetitions}. Bootstrap replicates per diagnostic: {bootstrap}.','',
           '## Parameter recovery','',
           'Each n is the number of simulated responses per cell (four cells per repetition). Bias and RMSE use only finite, converged estimates; exclusions and used counts are disclosed in the JSON. Near-boundary exclusions can themselves bias the retained summaries, so these are diagnostics rather than proof of uniform recovery.','']
    for s in summaries:
        desc='; '.join(f"{k} bias {v['bias']:.4f}, RMSE {v['rmse']:.4f}" if v['bias'] is not None else f'{k} undefined' for k,v in s['parameters'].items())
        lines.append(f"- **{s['scenario']}, n={s['n_per_cell']}**: {desc}. Nonconverged: {s['nonconverged']}; near-boundary fits: {s['near_simplex_boundary']}.")
    lines+=['','## Deliberate model misspecification','',
            'Binomial parametric-bootstrap goodness-of-fit tests compare tree predictions against four unrestricted cell probabilities. An initial symmetric logistic generator was found to be observationally equivalent to the tree and is retained explicitly. The asymmetric incompatible generator was added after that diagnostic finding. These demonstrations are exploratory, not preregistered tests or estimates of test size or power.','']
    for name,v in validation.items():
        lines.append(f"- **{name}**: deviance {v['fit_test']['deviance']:.3f}; bootstrap p={v['fit_test']['bootstrap_p']:.4f}; held-out negative log loss: tree {v['heldout_log_loss']['processing_tree']:.4f}, logistic {v['heldout_log_loss']['logistic_integration']:.4f}. Bootstrap nonconverged: {v['fit_test']['nonconverged']}.")
    lines+=['','## What this establishes','',
            'The implementation can be checked against known generating parameters and a competing response generator. Boundary diagnostics determine where interpretation is fragile. Recovery under the assumed tree does not establish that LLMs use that tree.','',
            'The observationally equivalent logistic generator is deliberately retained: a passing fit test cannot distinguish those response mechanisms from these four cells alone. The asymmetric generator checks whether a detectable violation can be rejected. Neither result proves test calibration.','',
            'See [the methodology](../../docs/RESEARCH_METHODOLOGY.md) for the proposed LLM experiment and the distinction between implemented validation and planned inferential analyses.','']
    (out/'VALIDATION_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='results/design_validation')
    parser.add_argument('--seed',type=int,default=20261101)
    parser.add_argument('--repetitions',type=int,default=200)
    parser.add_argument('--bootstrap',type=int,default=500)
    args=parser.parse_args()
    result=run(args.out,args.seed,args.repetitions,args.bootstrap)
    print(json.dumps({'recovery_cells':len(result['recovery']),
                      'nonconverged':sum(s['nonconverged'] for s in result['recovery']),
                      'model_checks':result['model_checks']},indent=2))
