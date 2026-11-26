"use client";

import React, { useEffect, useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { Info } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import { EChartBox } from "@/components/charts/EChartBox";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import { MathBlock } from "@/components/ui/MathBlock";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";
import { fmtCI, fmtPP, fmtPValue } from "@/lib/formatting/numbers";

interface StatsData {
  cohort_029: {
    primary: {
      delta_percentage_points: number;
      se: number;
      welch_df: number;
      interval_t: number[];
      interval_bounded: number[];
      causal: { both_correct: number; scheduled: number; fidelity: number };
      control: { both_correct: number; scheduled: number; fidelity: number };
    };
    intervals: { measure: string; mean: string; low: string; high: string; se: string; df: string }[];
    families: { slot: number; h: number; form: number; causal: number; arithmetic: number; diff: number }[];
  };
  cohort_016: {
    primary: {
      families: number;
      primary_q4_conflict_order_effect: {
        mean_difference: number;
        standard_error: number;
        t_statistic: number;
        degrees_of_freedom: number;
        two_sided_p_value: number;
        t_interval_95: number[];
        family_percentile_bootstrap_95_interval: number[];
      };
      secondary_order_results: {
        f16: { conflict: { historical_first_minus_randomized_first: number } };
        q4_k_m: { conflict: { historical_first_minus_randomized_first: number } };
      };
    };
    power: {
      families: number;
      replicates: number;
      smallest_effect_of_interest_pp?: number;
      simulated_power?: number;
    } | null;
    family_effects: { arm: string; family: string; conflict_order_diff_pp: number }[];
  };
  cohort_017: {
    analysis: {
      results: { q8_0?: { conflict: { historical_first_minus_randomized_first: {
        mean_difference: number;
        t_interval_95: [number, number] | null;
      } } } };
    } | null;
  };
  provenance: ProvenanceMeta;
}

export default function StatisticsPage() {
  const [data, setData] = useState<StatsData | null>(null);
  const [error, setError] = useState(false);
  const [mode, setMode] = useState<"intuitive" | "technical">("intuitive");

  useEffect(() => {
    loadDataset<StatsData>("/data/statistics.json").then(setData).catch(() => setError(true));
  }, []);

  const forestOption = useMemo<EChartsOption>(() => {
    if (!data) return {};
    const c29 = data.cohort_029.primary;
    const c16 = data.cohort_016.primary.primary_q4_conflict_order_effect;
    const c17 = data.cohort_017.analysis?.results.q8_0?.conflict.historical_first_minus_randomized_first;
    const rows = [
      {
        label: "029 · Contrast\nWelch 95% t CI",
        est: c29.delta_percentage_points,
        low: c29.interval_t[0] * 100,
        high: c29.interval_t[1] * 100,
        color: "#55D6BE",
      },
      {
        label: "029 · Contrast\nBounded 95% CI",
        est: c29.delta_percentage_points,
        low: c29.interval_bounded[0] * 100,
        high: c29.interval_bounded[1] * 100,
        color: "#FBBF24",
      },
      {
        label: "016 · Q4 conflict\nHistorical − trial first",
        est: c16.mean_difference * 100,
        low: c16.t_interval_95[0] * 100,
        high: c16.t_interval_95[1] * 100,
        color: "#60A5FA",
      },
      {
        label: "016 · F16 conflict\nDescriptive",
        est: data.cohort_016.primary.secondary_order_results.f16.conflict.historical_first_minus_randomized_first * 100,
        low: data.cohort_016.primary.secondary_order_results.f16.conflict.historical_first_minus_randomized_first * 100,
        high: data.cohort_016.primary.secondary_order_results.f16.conflict.historical_first_minus_randomized_first * 100,
        color: "#94A3B8",
      },
      ...(c17?.t_interval_95 ? [{
        label: "017 · Q8 conflict\nExploratory",
        est: c17.mean_difference * 100,
        low: c17.t_interval_95[0] * 100,
        high: c17.t_interval_95[1] * 100,
        color: "#A78BFA",
      }] : []),
    ];

    return {
      backgroundColor: "transparent",
      tooltip: {
        trigger: "item",
        formatter: (params) => {
          if (Array.isArray(params) || !Array.isArray(params.value)) return "";
          const [index, estimate, low, high] = params.value.map(Number);
          const label = rows[rows.length - 1 - index]?.label.replace("\n", " · ") ?? "";
          return `${label}<br>${fmtPP(estimate)}${low === high ? "" : ` · ${fmtCI(low, high)}`}`;
        },
        backgroundColor: "#111827",
        borderColor: "#263142",
        textStyle: { color: "#F1F5F9", fontSize: 11 },
      },
      grid: { left: 125, right: 26, top: 22, bottom: 44 },
      xAxis: {
        type: "value",
        name: "Percentage Point Contrast (pp)",
        nameLocation: "middle",
        nameGap: 25,
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8" },
        splitLine: { lineStyle: { color: "#1E293B" } },
      },
      yAxis: {
        type: "category",
        data: rows.map((r) => r.label).reverse(),
        axisLabel: { color: "#94A3B8", fontSize: 11 },
      },
      series: [
        {
          type: "custom",
          encode: { x: [1, 2, 3], y: 0 },
          renderItem: (_params, api) => {
            const yIdx = api.value(0) as number;
            const est = api.coord([api.value(1) as number, yIdx]);
            const low = api.coord([api.value(2) as number, yIdx]);
            const high = api.coord([api.value(3) as number, yIdx]);
            const color = rows[rows.length - 1 - yIdx].color;
            return {
              type: "group",
              children: [
                {
                  type: "line",
                  shape: { x1: low[0], y1: low[1], x2: high[0], y2: high[1] },
                  style: { stroke: color, lineWidth: 2 },
                },
                {
                  type: "circle",
                  shape: { cx: est[0], cy: est[1], r: 5 },
                  style: { fill: color },
                },
              ],
            };
          },
          data: rows
            .slice()
            .reverse()
            .map((r, idx) => [idx, r.est, r.low, r.high]),
          markLine: {
            silent: true,
            lineStyle: { color: "#64748B", type: "dashed" },
            data: [{ xAxis: 0 }],
          },
        },
      ],
    };
  }, [data]);

  const familyHistOption = useMemo<EChartsOption>(() => {
    if (!data) return {};
    const transfer = data.cohort_029.families.filter((f) => f.form === 1);
    const buckets: Record<string, number> = {};
    for (const f of transfer) {
      const key = `${(f.diff * 100).toFixed(0)} pp`;
      buckets[key] = (buckets[key] || 0) + 1;
    }
    const sortedKeys = Object.keys(buckets).sort((a, b) => parseFloat(a) - parseFloat(b));
    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis", backgroundColor: "#111827", borderColor: "#263142", textStyle: { color: "#F1F5F9", fontSize: 11 } },
      grid: { left: 48, right: 20, top: 24, bottom: 42 },
      xAxis: {
        type: "category",
        data: sortedKeys,
        name: "Within-Family Difference D_i (Causal − Arithmetic)",
        nameLocation: "middle",
        nameGap: 26,
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8", fontSize: 10 },
      },
      yAxis: {
        type: "value",
        name: "Families (N=128)",
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8" },
        splitLine: { lineStyle: { color: "#1E293B" } },
      },
      series: [
        {
          type: "bar",
          data: sortedKeys.map((k) => ({
            value: buckets[k],
            itemStyle: {
              color: parseFloat(k) === 0 ? "#64748B" : parseFloat(k) > 0 ? "#55D6BE" : "#A78BFA",
            },
          })),
        },
      ],
    };
  }, [data]);

  const order016HistOption = useMemo<EChartsOption>(() => {
    if (!data) return {};
    const q4 = data.cohort_016.family_effects.filter((f) => f.arm === "Q4_K_M");
    const buckets: Record<string, number> = {};
    for (const f of q4) {
      const key = `${f.conflict_order_diff_pp.toFixed(0)} pp`;
      buckets[key] = (buckets[key] || 0) + 1;
    }
    const sortedKeys = Object.keys(buckets).sort((a, b) => parseFloat(a) - parseFloat(b));
    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis", backgroundColor: "#111827", borderColor: "#263142", textStyle: { color: "#F1F5F9", fontSize: 11 } },
      grid: { left: 48, right: 20, top: 24, bottom: 42 },
      xAxis: {
        type: "category",
        data: sortedKeys,
        name: "Q4 Conflict Order Shift (Hist-First − Rand-First)",
        nameLocation: "middle",
        nameGap: 26,
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8", fontSize: 10 },
      },
      yAxis: {
        type: "value",
        name: "Families (N=96)",
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8" },
        splitLine: { lineStyle: { color: "#1E293B" } },
      },
      series: [
        {
          type: "bar",
          data: sortedKeys.map((k) => ({
            value: buckets[k],
            itemStyle: { color: "#60A5FA" },
          })),
        },
      ],
    };
  }, [data]);

  if (error) return <p role="alert">The frozen statistical dataset is unavailable.</p>;
  if (!data) return <p role="status">Loading family-level results…</p>;
  const primary = data.cohort_029.primary;
  const order = data.cohort_016.primary.primary_q4_conflict_order_effect;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Inferential & Descriptive Analysis"
        title="Statistical Observatory"
        subtitle="Family-clustered inference, Welch-Satterthwaite and Hoeffding-bounded intervals, and distribution-level diagnostics. Prompt-level responses within a numerical family are never treated as independent."
        provenance={data.provenance}
      >
        <div className="flex rounded border border-obs-border bg-obs-elevated p-0.5 text-xs">
          <button
            type="button"
            aria-pressed={mode === "intuitive"}
            onClick={() => setMode("intuitive")}
            className={`rounded px-2.5 py-1 font-medium ${
              mode === "intuitive" ? "bg-sci-causal text-slate-950" : "text-obs-secondary"
            }`}
          >
            Intuitive Mode
          </button>
          <button
            type="button"
            aria-pressed={mode === "technical"}
            onClick={() => setMode("technical")}
            className={`rounded px-2.5 py-1 font-medium ${
              mode === "technical" ? "bg-sci-causal text-slate-950" : "text-obs-secondary"
            }`}
          >
            Technical Mode
          </button>
        </div>
      </PageHeader>

      {/* Explanation Banner */}
      <section className="rounded border border-obs-border bg-obs-surface p-4 text-xs leading-relaxed text-obs-secondary">
        <div className="mb-1 flex items-center gap-1.5 font-mono text-[11px] font-semibold uppercase text-sci-causal">
          <Info className="h-3.5 w-3.5" />
          <span>{mode === "intuitive" ? "Intuitive Statistical Summary" : "Technical Estimand & Variance Specification"}</span>
        </div>
        {mode === "intuitive" ? (
          <p>
            Prompts generated from the same numerical family reuse the same numbers. The primary analysis uses the family as the independent unit. In Cohort 029 the causal-minus-arithmetic difference was {fmtPP(primary.delta_percentage_points)}. Its approximate 95% interval, {fmtCI(primary.interval_t[0] * 100, primary.interval_t[1] * 100)}, spans zero. The comparison leaves causal-specific impairment and equivalence unresolved.
          </p>
        ) : (
          <div className="space-y-1.5">
            <p>
              <strong>Estimand:</strong> Stratified mean of within-family paired fidelity differences{" "}
              <MathBlock tex="\widehat{\Delta} = \frac{1}{8}\sum_{h=0}^{7} \bar{D}_h" /> across 8 design strata (16 families each).{" "}
              <strong>Variance:</strong>{" "}
              <MathBlock tex={`\\mathrm{SE} = \\sqrt{\\sum_{h=0}^{7} s_h^2 / (64 \\cdot 16)} = ${(primary.se * 100).toFixed(4)}\\text{ pp}`} /> with Welch-Satterthwaite{" "}
              <MathBlock tex={`\\nu = ${primary.welch_df.toFixed(2)}`} />.{" "}
              <strong>Bounded Interval:</strong> Distribution-free radius{" "}
              <MathBlock tex="\sqrt{2\log(40)/128}" />. The archived bounded interval is {fmtCI(primary.interval_bounded[0] * 100, primary.interval_bounded[1] * 100)}.
            </p>
          </div>
        )}
      </section>

      {/* Forest Plot */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <div>
            <h2 className="text-sm font-semibold text-obs-text">
              Forest Plot — Key Prespecified & Exploratory Family-Level Contrasts
            </h2>
            <p className="text-xs text-obs-secondary">
              The dashed line marks zero difference. Each row reports a separate estimand. The F16 descriptive row shows a point estimate.
            </p>
          </div>
          <EvidenceButton meta={data.provenance} title="Forest Plot Contrasts" />
        </div>
        <EChartBox option={forestOption} height={280} exportName="statistical-forest-plot" />
      </section>

      {/* Distribution Plots */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded border border-obs-border bg-obs-surface p-5">
          <h2 className="text-sm font-semibold text-obs-text">
            Cohort 029: Within-Family Difference Distribution (N = 128)
          </h2>
          <p className="mb-3 text-xs text-obs-secondary">
            Distribution of D_i = Causal Fidelity − Arithmetic Fidelity across all 128 independent families (Transfer form).
          </p>
          <EChartBox option={familyHistOption} height={260} exportName="cohort-029-family-diffs" />
        </div>

        <div className="rounded border border-obs-border bg-obs-surface p-5">
          <h2 className="text-sm font-semibold text-obs-text">
            Cohort 016: Q4_K_M Conflict Order Shift Distribution (N = 96)
          </h2>
          <p className="mb-3 text-xs text-obs-secondary">
            Historical-first minus randomized-first mean {fmtPP(order.mean_difference * 100)}. t({order.degrees_of_freedom}) = {order.t_statistic.toFixed(2)}, p = {fmtPValue(order.two_sided_p_value)}.
          </p>
          <EChartBox option={order016HistOption} height={260} exportName="cohort-016-family-order-diffs" />
        </div>
      </section>
    </div>
  );
}
