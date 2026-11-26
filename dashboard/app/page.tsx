"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import type { EChartsOption } from "echarts";
import { ArrowRight, CheckCircle2, AlertTriangle, HelpCircle, FlaskConical } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { OverviewSchema, type OverviewData } from "@/lib/schemas/observatory";
import { PageHeader } from "@/components/ui/PageHeader";
import { EChartBox } from "@/components/charts/EChartBox";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import { fmtInt, fmtPP, fmtCI, fmtPct } from "@/lib/formatting/numbers";

export default function OverviewPage() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDataset("/data/overview.json", OverviewSchema)
      .then(setData)
      .catch((e) => setError(String(e)));
  }, []);

  const summaryChartOption = useMemo<EChartsOption>(() => {
    if (!data) return {};
    const { causal_pair_fidelity, arithmetic_pair_fidelity } = data.kpis;
    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "axis",
        backgroundColor: "#111827",
        borderColor: "#263142",
        textStyle: { color: "#F1F5F9", fontSize: 12 },
      },
      grid: { left: 56, right: 24, top: 36, bottom: 44 },
      xAxis: {
        type: "category",
        data: [
          `Causal transfer\n(${causal_pair_fidelity.correct}/${causal_pair_fidelity.total} pairs)`,
          `Arithmetic control\n(${arithmetic_pair_fidelity.correct}/${arithmetic_pair_fidelity.total} pairs)`,
        ],
        axisLabel: { color: "#94A3B8", fontSize: 11 },
        axisLine: { lineStyle: { color: "#263142" } },
      },
      yAxis: {
        type: "value",
        name: "Target-Pair Fidelity (%)",
        min: 0,
        max: 100,
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8", formatter: "{value}%" },
        splitLine: { lineStyle: { color: "#1E293B" } },
      },
      series: [
        {
          type: "bar",
          barWidth: 52,
          data: [
            {
              value: causal_pair_fidelity.pct,
              itemStyle: { color: "#55D6BE", borderRadius: [3, 3, 0, 0] },
            },
            {
              value: arithmetic_pair_fidelity.pct,
              itemStyle: { color: "#A78BFA", borderRadius: [3, 3, 0, 0] },
            },
          ],
          label: {
            show: true,
            position: "top",
            color: "#F1F5F9",
            fontFamily: "monospace",
            formatter: ({ value }) => `${Number(value).toFixed(2)}%`,
          },
        },
      ],
    };
  }, [data]);

  if (error) {
    return (
      <div className="rounded border border-sci-error/40 bg-sci-error/10 p-4 text-sm text-sci-error">
        Failed to load overview dataset: {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-4">
        <div className="h-24 animate-pulse rounded bg-obs-surface" />
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded bg-obs-surface" />
          ))}
        </div>
      </div>
    );
  }

  const { kpis } = data;

  return (
    <div className="space-y-8">
      <PageHeader
        eyebrow="Project CausalFade · Scientific Research Observatory"
        title={data.headline}
        subtitle="CausalFade investigates whether language models—and quantized deployments—use causal provenance and target-population standardization when choosing interventions, or whether apparent competence masks action biases, presentation sensitivity, and shortcut heuristics."
        provenance={data.provenance}
      >
        <Link
          href="/causal-lab/"
          className="inline-flex items-center gap-1.5 rounded bg-sci-causal px-3 py-1.5 text-xs font-semibold text-slate-950 transition-opacity hover:opacity-90"
        >
          <FlaskConical className="h-3.5 w-3.5" />
          <span>Open Causal Lab</span>
        </Link>
      </PageHeader>

      {/* Verified Scope-Labeled KPIs */}
      <section aria-label="Verified Repository Metrics">
        <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
          <h2 className="font-mono text-xs font-semibold uppercase tracking-wider text-obs-muted">
            Research archive and final evaluation
          </h2>
          <span className="font-mono text-[11px] text-obs-muted">
            Commit {data.git_commit.slice(0, 7)} · Tag {data.release_tag}
          </span>
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">Documented Cohorts</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-obs-text">
              {kpis.documented_cohorts}
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              {fmtInt(kpis.llm_cohort_units)} entries contain recorded model responses
            </div>
          </div>

          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">Experimental Runs</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-obs-text">
              {kpis.completed_runs}{" "}
              <span className="text-xs font-normal text-sci-caution">
                (+{kpis.interrupted_runs} int.)
              </span>
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              Cohort 008 Run 1 interrupted at 26/64
            </div>
          </div>

          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">Persisted Raw Responses</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-obs-text">
              {fmtInt(kpis.persisted_raw_responses)}
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              of {fmtInt(kpis.scheduled_requests)} scheduled across all cohorts
            </div>
          </div>

          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">CF-TP1 Final Responses</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-sci-verified">
              {fmtInt(kpis.final_eval_strict_valid)} / {fmtInt(kpis.final_eval_responses)}
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              {fmtPct(kpis.final_eval_strict_valid / kpis.final_eval_responses, 0)} strict-valid (Cohort 029)
            </div>
          </div>

          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">Independent Families</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-sci-causal">
              {kpis.independent_families_final}
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              8 design strata × 16 families (Cohort 029)
            </div>
          </div>

          <div className="rounded border border-obs-border bg-obs-surface p-3.5">
            <div className="text-[11px] font-mono uppercase text-obs-muted">Model Configurations</div>
            <div className="mt-1 font-mono text-2xl font-semibold tabular-nums text-obs-text">
              {kpis.model_config_entries}
            </div>
            <div className="mt-1 text-[11px] text-obs-secondary">
              Qwen2.5, Mistral-7B, Llama-3.1 (incl. prepared)
            </div>
          </div>
        </div>
      </section>

      {/* Main Results & Limitations Side-by-Side */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="min-w-0 rounded border border-obs-border bg-obs-surface p-5 lg:col-span-7">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-base font-semibold text-obs-text">
                Final Confirmatory Case Study (Cohort 029 · CF-TP1)
              </h2>
              <p className="text-xs text-obs-secondary">
                Qwen2.5-7B-Instruct Q4_K_M · Transfer form
              </p>
            </div>
            <EvidenceButton meta={data.provenance} title="Cohort 029 Primary Result" />
          </div>

          <EChartBox option={summaryChartOption} height={290} exportName="cohort-029-primary-fidelity" />

          <div className="mt-3 grid grid-cols-2 gap-3 border-t border-obs-border pt-3 text-xs sm:grid-cols-4">
            <div>
              <span className="text-obs-muted">Causal Reversals</span>
              <div className="mt-0.5 font-mono font-semibold text-sci-error tabular-nums">
                {kpis.causal_reversals_correct.correct} / {kpis.causal_reversals_correct.total}
              </div>
            </div>
            <div>
              <span className="text-obs-muted">Causal Activation</span>
              <div className="mt-0.5 font-mono font-semibold text-sci-caution tabular-nums">
                {kpis.causal_activation.count} / {fmtInt(kpis.causal_activation.total)}
              </div>
            </div>
            <div>
              <span className="text-obs-muted">Primary Δ (C − A)</span>
              <div className="mt-0.5 font-mono font-semibold text-obs-text tabular-nums">
                {fmtPP(kpis.delta_pp)}
              </div>
            </div>
            <div>
              <span className="text-obs-muted">95% Welch t CI</span>
              <div className="mt-0.5 font-mono font-semibold text-obs-text tabular-nums">
                {fmtCI(kpis.t_ci_pp[0], kpis.t_ci_pp[1])}
              </div>
            </div>
          </div>
        </div>

        {/* Scope of Inference & Limitations Placed Prominently Alongside */}
        <div className="flex flex-col justify-between rounded border border-obs-border bg-obs-surface p-5 lg:col-span-5">
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-mono font-semibold uppercase tracking-wider text-sci-caution">
              <AlertTriangle className="h-4 w-4" />
              <span>Scope of Inference & Remaining Uncertainty</span>
            </div>

            <div className="space-y-3 text-xs leading-relaxed text-obs-secondary">
              <div className="rounded border border-obs-border bg-obs-elevated/60 p-3">
                <div className="font-semibold text-obs-text">Observed Decision Failure</div>
                <p className="mt-1">
                  The model activated on {fmtInt(kpis.causal_activation.count)} of {fmtInt(kpis.causal_activation.total)} causal transfer prompts and correctly reversed its recommendation on {kpis.causal_reversals_correct.correct} of {kpis.causal_reversals_correct.total} required target-population switches.
                </p>
              </div>
              <div className="rounded border border-obs-border bg-obs-elevated/60 p-3">
                <div className="font-semibold text-obs-text">Matched-Control Result (Inconclusive)</div>
                <p className="mt-1">
                  Arithmetic fidelity was {kpis.arithmetic_pair_fidelity.correct} of {kpis.arithmetic_pair_fidelity.total} matched pairs. The approximate 95% interval for the contrast, {fmtCI(kpis.t_ci_pp[0], kpis.t_ci_pp[1])}, spans zero. Causal-specific impairment and equivalence remain unresolved.
                </p>
              </div>
              <div className="rounded border border-obs-border bg-obs-elevated/60 p-3">
                <div className="font-semibold text-obs-text">Quantization Claim Withheld</div>
                <p className="mt-1">
                  Cohort 029 evaluated a single quantized deployment (Qwen2.5-7B Q4_K_M) with no F16 arm. Across Cohorts 001–028, selective causal degradation under quantization was never established.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2 border-t border-obs-border pt-3">
            <Link
              href="/findings/"
              className="inline-flex items-center gap-1 text-xs font-medium text-sci-causal hover:underline"
            >
              <span>Read Final Findings</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
            <span className="text-obs-muted">·</span>
            <Link
              href="/reproducibility/"
              className="inline-flex items-center gap-1 text-xs font-medium text-sci-observational hover:underline"
            >
              <span>Inspect verification checks</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Research at a Glance */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-base font-semibold text-obs-text">
            Research at a Glance — How the Investigation Evolved
          </h2>
          <Link
            href="/journey/"
            className="inline-flex items-center gap-1 text-xs font-medium text-sci-causal hover:underline"
          >
            <span>Explore Full Timeline & Genealogy</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-5">
          {data.research_at_a_glance.map((item) => (
            <div
              key={item.step}
              className="flex flex-col justify-between rounded border border-obs-border bg-obs-elevated/40 p-3.5"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-sci-causal">
                    0{item.step}
                  </span>
                  <span className="rounded bg-obs-surface px-1.5 py-0.5 font-mono text-[10px] text-obs-muted">
                    {item.status}
                  </span>
                </div>
                <h3 className="mt-2 text-sm font-semibold text-obs-text">{item.title}</h3>
                <p className="mt-1.5 text-xs leading-relaxed text-obs-secondary">
                  {item.summary}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Established vs Unresolved */}
      <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="rounded border border-obs-border bg-obs-surface p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-sci-verified">
            <CheckCircle2 className="h-4 w-4" />
            <span>What the Research Established</span>
          </div>
          <ul className="space-y-2.5 text-xs leading-relaxed text-obs-secondary">
            {data.established.map((line, idx) => (
              <li key={idx} className="flex gap-2">
                <span className="font-mono text-sci-verified">•</span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded border border-obs-border bg-obs-surface p-5">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-sci-caution">
            <HelpCircle className="h-4 w-4" />
            <span>What Remains Scientifically Unresolved</span>
          </div>
          <ul className="space-y-2.5 text-xs leading-relaxed text-obs-secondary">
            {data.unresolved.map((line, idx) => (
              <li key={idx} className="flex gap-2">
                <span className="font-mono text-sci-caution">•</span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  );
}
