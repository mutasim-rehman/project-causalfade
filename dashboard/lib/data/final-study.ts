import overview from "@/public/data/overview.json";
import transitions from "@/public/data/target_transitions.json";
import { OverviewSchema, ProvenanceSchema } from "@/lib/schemas/observatory";
import { fmtCI, fmtInt, fmtPP } from "@/lib/formatting/numbers";

export function getFinalStudy() {
  const { kpis, provenance, git_commit } = OverviewSchema.parse(overview);
  const transitionProvenance = ProvenanceSchema.parse(transitions.provenance);
  const ratio = (count: number, total: number) => `${fmtInt(count)} / ${fmtInt(total)}`;
  return {
    commit: git_commit,
    families: kpis.independent_families_final,
    reversals: ratio(kpis.causal_reversals_correct.correct, kpis.causal_reversals_correct.total),
    activation: ratio(kpis.causal_activation.count, kpis.causal_activation.total),
    causalPairs: ratio(kpis.causal_pair_fidelity.correct, kpis.causal_pair_fidelity.total),
    arithmeticPairs: ratio(kpis.arithmetic_pair_fidelity.correct, kpis.arithmetic_pair_fidelity.total),
    contrast: fmtPP(kpis.delta_pp),
    interval: fmtCI(kpis.t_ci_pp[0], kpis.t_ci_pp[1]),
    boundedInterval: fmtCI(kpis.bounded_ci_pp[0], kpis.bounded_ci_pp[1]),
    provenance,
    reversalEvidence: {
      ...transitionProvenance,
      metric_id: "cohort_029_transfer_causal_reversals",
      definition: "Correctly oriented reversals among causal transfer-form pairs whose oracle action changes from target 0 to target 1.",
      value: kpis.causal_reversals_correct,
      numerator: kpis.causal_reversals_correct.correct,
      denominator: kpis.causal_reversals_correct.total,
    },
  };
}
