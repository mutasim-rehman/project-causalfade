import { z } from "zod";

export const SourceArtifactSchema = z.object({
  path: z.string(),
  sha256: z.string().nullable(),
  github_url: z.string(),
});

export const ProvenanceSchema = z.object({
  metric_id: z.string(),
  definition: z.string(),
  value: z.unknown(),
  numerator: z.number().nullable().optional(),
  denominator: z.number().nullable().optional(),
  unit: z.string(),
  unit_of_analysis: z.string(),
  cohort_id: z.string(),
  ci_method: z.string().nullable().optional(),
  statistical_test: z.string().nullable().optional(),
  sources: z.array(SourceArtifactSchema),
  git_commit: z.string(),
  analysis_script: z.string(),
  classification: z.string(),
  limitations: z.string().nullable().optional(),
});

export type ProvenanceMeta = z.infer<typeof ProvenanceSchema>;

export const OverviewSchema = z.object({
  product_name: z.string(),
  subtitle: z.string(),
  headline: z.string(),
  git_commit: z.string(),
  release_tag: z.string(),
  release_commit: z.string(),
  extraction_timestamp: z.string(),
  kpis: z.object({
    documented_cohorts: z.number(),
    llm_cohort_units: z.number(),
    run_directories: z.number(),
    completed_runs: z.number(),
    interrupted_runs: z.number(),
    scheduled_requests: z.number(),
    persisted_raw_responses: z.number(),
    final_eval_responses: z.number(),
    final_eval_strict_valid: z.number(),
    independent_families_final: z.number(),
    model_config_entries: z.number(),
    causal_pair_fidelity: z.object({ correct: z.number(), total: z.number(), pct: z.number() }),
    arithmetic_pair_fidelity: z.object({ correct: z.number(), total: z.number(), pct: z.number() }),
    delta_pp: z.number(),
    t_ci_pp: z.array(z.number()),
    bounded_ci_pp: z.array(z.number()),
    causal_reversals_correct: z.object({ correct: z.number(), total: z.number() }),
    causal_activation: z.object({ count: z.number(), total: z.number() }),
  }),
  research_at_a_glance: z.array(
    z.object({
      step: z.number(),
      title: z.string(),
      summary: z.string(),
      status: z.string(),
    })
  ),
  established: z.array(z.string()),
  unresolved: z.array(z.string()),
  provenance: ProvenanceSchema,
});

export type OverviewData = z.infer<typeof OverviewSchema>;

export const CohortRunSchema = z.object({
  run_id: z.string(),
  run_path: z.string(),
  model_artifact: z.string(),
  model_sha256: z.string(),
  scheduled_requests: z.number(),
  persisted_raw_records: z.number(),
  strict_valid_count: z.number().nullable(),
  strict_correct_count: z.number().nullable(),
  status: z.string(),
  max_tokens: z.string().nullable(),
  seed: z.string(),
  raw_sha256: z.string(),
});

export const CohortSchema = z.object({
  cohort_id: z.string(),
  dates: z.string(),
  title: z.string(),
  models_and_formats: z.string(),
  sample_and_design: z.string(),
  persisted_llm_responses: z.number(),
  scheduled_requests: z.number(),
  persisted_from_runs: z.number(),
  inferential_classification: z.string(),
  comparability_group: z.string(),
  principal_finding: z.string(),
  primary_artifact: z.string(),
  key_commits: z.string(),
  runs: z.array(CohortRunSchema),
  artifacts: z.array(SourceArtifactSchema),
  has_interrupted_run: z.boolean(),
});

export type CohortRecord = z.infer<typeof CohortSchema>;

export const CausalLabFamilySchema = z.object({
  slot: z.number(),
  family_id: z.string(),
  h: z.number(),
  p: z.number(),
  g: z.number(),
  b: z.number(),
  weights_pct: z.array(z.number()),
  tables_pct: z.object({
    L: z.array(z.array(z.number())),
    R: z.array(z.array(z.number())),
  }),
  stratum_effects_pp: z.object({
    L: z.object({ delta_1: z.number(), delta_0: z.number() }),
    R: z.object({ delta_1: z.number(), delta_0: z.number() }),
  }),
  target_effects_pp: z.object({
    L_governs: z.object({ w0: z.number(), w1: z.number() }),
    R_governs: z.object({ w0: z.number(), w1: z.number() }),
  }),
  oracle_actions: z.object({
    L_governs: z.array(z.number()),
    R_governs: z.array(z.number()),
  }),
  scm_surfaces_pct: z.array(z.array(z.array(z.array(z.number())))),
});

export type CausalLabFamily = z.infer<typeof CausalLabFamilySchema>;

export const CausalLabDataSchema = z.object({
  git_commit: z.string(),
  cohort_id: z.string(),
  featured_slot: z.number(),
  equation: z.string(),
  families: z.array(CausalLabFamilySchema),
  provenance: ProvenanceSchema,
});

export type CausalLabData = z.infer<typeof CausalLabDataSchema>;
