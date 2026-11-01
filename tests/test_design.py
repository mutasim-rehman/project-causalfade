import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
from causalfade.worlds import World, make_families, backdoor_estimate, exact_evidence, prompt
from causalfade.generate import generate
from causalfade.processing import probabilities, fit_counts, bootstrap_fit_test, fit_logistic
from causalfade.score import score
from causalfade.analyze import paired_contrast


class CausalWorldTests(unittest.TestCase):
    def test_orthogonality_positivity_and_oracle(self):
        worlds=list(make_families(100,42))
        for w in worlds:
            self.assertTrue(np.all((w.outcome>0)&(w.outcome<1)))
            self.assertTrue(np.all((w.propensity>0)&(w.propensity<1)))
            self.assertAlmostEqual(w.do_means[1]-w.do_means[0],w.tau)
            self.assertEqual(w.observational_difference>0,bool(w.association_positive))
            # Exact backdoor adjustment, distinct from the observational contrast.
            adjusted=.5*sum(w.outcome[z,1]-w.outcome[z,0] for z in (0,1))
            self.assertAlmostEqual(adjusted,w.tau)
        for i in range(0,len(worlds),4):
            self.assertEqual(worlds[i].tau,worlds[i+1].tau)
            self.assertEqual(worlds[i+2].tau,worlds[i+3].tau)

    def test_sampled_adjustment_converges(self):
        w=World('test',1,0,.1,.6,.8)
        estimate=backdoor_estimate(w.sample_counts(200000,np.random.default_rng(2)))
        self.assertAlmostEqual(estimate,w.tau,delta=.015)

    def test_empty_stratum_not_fabricated(self):
        self.assertIsNone(backdoor_estimate([dict(z=0,x=0,n=0,successes=0)]))

    def test_no_oracle_labels_in_prompt(self):
        w=next(make_families(1,4))
        text=prompt(w,exact_evidence(w))
        for prohibited in ['causal_positive','association_positive','optimal_action','effect_size','conflict']:
            self.assertNotIn(prohibited,text)

    def test_reproducible_export_and_complete_cells(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            m=generate(a,3,8,100)
            generate(b,3,8,100)
            self.assertEqual(m['tasks'],24)
            for name in m['file_sha256']:
                self.assertEqual((Path(a)/name).read_bytes(),(Path(b)/name).read_bytes())
            tasks=[json.loads(s) for s in (Path(a)/'public_tasks.jsonl').read_text().splitlines()]
            self.assertEqual(len({t['task_id'] for t in tasks}),24)
            self.assertFalse(any('causal_positive' in t for t in tasks))

    def test_invalid_design_rejected(self):
        with self.assertRaises(ValueError):
            World('bad',1,0,.8,.6,.5)


class ProcessingTests(unittest.TestCase):
    def test_expected_frequency_recovery(self):
        for theta in [(.65,.45,.5),(.35,.45,.5),(.65,.75,.8)]:
            p=probabilities(*theta)
            fit=fit_counts(p*10000,10000)
            self.assertTrue(fit['converged'][0])
            np.testing.assert_allclose(fit['parameters'][0],theta,atol=2e-5)

    def test_boundary_is_not_reported_as_identified(self):
        fit=fit_counts(np.array([0,0,1000,1000]),1000)
        self.assertGreater(fit['parameters'][0,0],.99999)
        self.assertTrue(np.isnan(fit['parameters'][0,1]))

    def test_negative_evidence_sensitivity_rejected_by_fit(self):
        y=np.array([900,100,100,900])
        test=bootstrap_fit_test(y,1000,np.random.default_rng(1),99)
        self.assertLessEqual(test['bootstrap_p'],.02)

    def test_logistic_rival_recovers_expected_probabilities(self):
        p=1/(1+np.exp(-np.array([-3,0,0,3])))
        fit=fit_logistic(p*1000,np.full(4,1000))
        self.assertTrue(fit['converged'])
        np.testing.assert_allclose(fit['probabilities'],p,atol=1e-7)

    def test_invalid_counts(self):
        for counts in [[1,2,3],[1,2,3,11],[1,2,3,float('nan')]]:
            with self.assertRaises(ValueError):
                fit_counts(counts,10)

    def test_symmetric_logistic_is_observationally_equivalent(self):
        p=1/(1+np.exp(-np.array([-3.,0.,0.,3.])))
        fitted=fit_counts(p*10000,10000)
        np.testing.assert_allclose(fitted['probabilities'][0],p,atol=2e-6)

    def test_asymmetric_logistic_violates_tree(self):
        p=1/(1+np.exp(-np.array([-2.,1.,2.,5.])))
        test=bootstrap_fit_test(np.round(p*2000),2000,np.random.default_rng(7),99)
        self.assertLessEqual(test['bootstrap_p'],.02)


class ScoringTests(unittest.TestCase):
    def setUp(self):
        self.truth=[dict(task_id='a',evidence_mode='exact',**next(make_families(1,3)).truth())]

    def test_missing_and_invalid_not_silently_dropped(self):
        row=score(self.truth,[])[0]
        self.assertEqual(row['correct'],0)
        self.assertTrue(row['missing_prediction'])
        self.assertIsNone(row['regret'])
        row=score(self.truth,[dict(task_id='a',activate=True,ate_estimate=float('nan'))])[0]
        self.assertFalse(row['valid_action'])
        self.assertFalse(row['numeric_estimate_valid'])

    def test_correct_negative_effect_and_regret(self):
        tau=self.truth[0]['ate']
        row=score(self.truth,[dict(task_id='a',activate=0,ate_estimate=tau,adjustment_set=['Z'])])[0]
        self.assertEqual(row['correct'],1)
        self.assertEqual(row['ate_error'],0)
        self.assertEqual(row['regret'],0)
        self.assertTrue(row['adjustment_valid'])

    def test_duplicate_and_unknown_ids_rejected(self):
        for records in [[dict(task_id='b')],[dict(task_id='a'),dict(task_id='a')]]:
            with self.assertRaises(ValueError):
                score(self.truth,records)


class PairedAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.truth=[dict(task_id=str(i),evidence_mode='exact',**w.truth()) for i,w in enumerate(make_families(5,7))]
        self.ref=score(self.truth,[dict(task_id=t['task_id'],activate=t['optimal_action']) for t in self.truth])
        self.comp=score(self.truth,[dict(task_id=t['task_id'],activate=t['association_positive']) for t in self.truth])

    def test_blocked_contrast_retains_all_four_cells(self):
        result=paired_contrast(self.ref,self.comp,bootstrap=100)
        self.assertEqual(result['delta_conflict_penalty'],1)
        self.assertEqual(result['families'],5)
        self.assertEqual(result['paired_family_bootstrap_percentile_95_interval'],[1,1])
        reverse=paired_contrast(self.comp,self.ref,bootstrap=100)
        self.assertEqual(reverse['delta_conflict_penalty'],-1)

    def test_unpaired_or_incomplete_data_rejected(self):
        for reference,comparison in [(self.ref,self.comp[:-1]),(self.ref[:-1],self.comp[:-1]),(self.ref+[self.ref[0]],self.comp)]:
            with self.assertRaises(ValueError):
                paired_contrast(reference,comparison,bootstrap=10)


if __name__=='__main__':
    unittest.main()
