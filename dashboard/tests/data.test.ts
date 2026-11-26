import { describe, expect, it } from "vitest";
import { z } from "zod";
import overview from "../public/data/overview.json";
import lab from "../public/data/causal_lab.json";
import cohorts from "../public/data/cohorts.json";
import transitions from "../public/data/target_transitions.json";
import { CausalLabDataSchema, CohortSchema, OverviewSchema } from "../lib/schemas/observatory";

describe("frozen snapshot", () => {
  it("loads the overview and all cohort records with consistent inventory counts", () => {
    const { kpis, git_commit } = OverviewSchema.parse(overview);
    const rows = z.array(CohortSchema).parse(cohorts.cohorts);
    expect(cohorts.git_commit).toBe(git_commit);
    expect(new Set(rows.map((row) => row.cohort_id)).size).toBe(kpis.documented_cohorts);
    expect(rows.filter((row) => row.has_interrupted_run).map((row) => row.cohort_id)).toContain("cohort_008");
  });

  it("reconstructs frozen causal oracle actions from each randomized table", () => {
    const { families, featured_slot } = CausalLabDataSchema.parse(lab);
    expect(families).toHaveLength(overview.kpis.independent_families_final);
    expect(families.some((family) => family.slot === featured_slot)).toBe(true);
    for (const family of families) {
      for (const table of ["L", "R"] as const) {
        const { delta_1, delta_0 } = family.stratum_effects_pp[table];
        const expected = family.weights_pct.map((w) => (w * delta_1 + (100 - w) * delta_0) / 100);
        const reported = family.target_effects_pp[`${table}_governs`];
        expect(expected[0]).toBeCloseTo(reported.w0, 4);
        expect(expected[1]).toBeCloseTo(reported.w1, 4);
        expect(expected.map((value) => Number(value > 0))).toEqual(family.oracle_actions[`${table}_governs`]);
      }
    }
  });

  it("reconciles the reversal denominator and correct direction against the overview", () => {
    const required = transitions.rows.filter((row) => row.form === "transfer" && row.task === "causal"
      && row.expected[0] !== row.expected[1]);
    expect(required.length).toBe(overview.kpis.causal_reversals_correct.total);
    expect(required.filter((row) => row.expected.every((action, index) => action === row.observed[index])).length)
      .toBe(overview.kpis.causal_reversals_correct.correct);
  });
});
