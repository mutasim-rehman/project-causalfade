"use client";

import React, { useEffect, useMemo, useState } from "react";
import type { EChartsOption } from "echarts";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import { EChartBox } from "@/components/charts/EChartBox";
import { TransitionMatrix } from "@/components/charts/TransitionMatrix";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";

interface DecisionsData {
  cohort_029_pairs: {
    axis: string;
    form: string;
    task: string;
    switch: string;
    pairs: string;
    both: string;
    one: string;
    neither: string;
    changed: string;
  }[];
  cohort_029_policies: {
    policy: string;
    items: string;
    target_switch: string;
    target_stable: string;
    role_switch: string;
    role_stable: string;
    families_wrong: string;
  }[];
  provenance: ProvenanceMeta;
}

export default function DecisionsPage() {
  const [data, setData] = useState<DecisionsData | null>(null);

  useEffect(() => {
    loadDataset<DecisionsData>("/data/decision_behavior.json").then(setData);
  }, []);

  const jointOption = useMemo<EChartsOption>(() => {
    if (!data) return {};
    // Transfer form (form === "1") target switch & invariant
    const rows = data.cohort_029_pairs.filter(
      (p) => p.form === "1" && p.axis === "target"
    );
    const labels = rows.map(
      (r) =>
        `${r.task === "0" ? "Causal" : "Arithmetic"}\n${
          r.switch === "1" ? "Required Switch" : "Required Invariant"
        }`
    );
    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, backgroundColor: "#111827", borderColor: "#263142", textStyle: { color: "#F1F5F9", fontSize: 11 } },
      legend: { data: ["Both Correct (2/2)", "One Correct (1/2)", "Neither Correct (0/2)"], textStyle: { color: "#94A3B8", fontSize: 11 }, top: 4 },
      grid: { left: 48, right: 20, top: 40, bottom: 48 },
      xAxis: { type: "category", data: labels, axisLabel: { color: "#94A3B8", fontSize: 11 } },
      yAxis: { type: "value", max: 256, name: "Pairs (out of 256)", nameTextStyle: { color: "#94A3B8", fontSize: 11 }, axisLabel: { color: "#94A3B8" }, splitLine: { lineStyle: { color: "#1E293B" } } },
      series: [
        { name: "Both Correct (2/2)", type: "bar", stack: "total", itemStyle: { color: "#34D399" }, data: rows.map((r) => Number(r.both)) },
        { name: "One Correct (1/2)", type: "bar", stack: "total", itemStyle: { color: "#FBBF24" }, data: rows.map((r) => Number(r.one)) },
        { name: "Neither Correct (0/2)", type: "bar", stack: "total", itemStyle: { color: "#F87171" }, data: rows.map((r) => Number(r.neither)) },
      ],
    };
  }, [data]);

  if (!data) return <div className="h-96 animate-pulse rounded bg-obs-surface" />;

  const transferPairs = data.cohort_029_pairs.filter((p) => p.form === "1");

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Action Transitions, Biases & Rival Policies"
        title="Decision Behavior (Cohort 029)"
        subtitle="Why aggregate accuracy misleads: decomposing target switches, invariant stability, directional activation bias (995/1,024 causal), and deterministic shortcut policies."
        provenance={data.provenance}
      />

      <TransitionMatrix />

      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-obs-text">
              Joint Pair-Member Correctness (Transfer Form, N = 256 pairs per bar)
            </h2>
            <p className="text-xs text-obs-secondary">
              Causal target-switch pairs achieved 3/256 both correct (248 one correct, 5 neither). Arithmetic achieved 27/256 both correct.
            </p>
          </div>
          <EvidenceButton meta={data.provenance} title="Joint Pair Correctness" />
        </div>
        <EChartBox option={jointOption} height={300} exportName="cohort-029-joint-pair-correctness" />
      </section>

      {/* Paired Consistency Table (Table 2 Panel A of Manuscript) */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <h2 className="mb-3 text-sm font-semibold text-obs-text">
          Transfer-Form Paired Consistency & Action Changes
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs tabular-nums">
            <thead>
              <tr className="border-b border-obs-border text-obs-muted">
                <th className="py-2 pr-4">Pair Axis</th>
                <th className="py-2 pr-4">Task</th>
                <th className="py-2 pr-4">Condition</th>
                <th className="py-2 pr-4">Both Correct</th>
                <th className="py-2 pr-4">Changed Action</th>
                <th className="py-2">Total Pairs</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              {transferPairs.map((r, i) => (
                <tr key={i}>
                  <td className="py-2 pr-4 text-obs-text">{r.axis}</td>
                  <td className={`py-2 pr-4 ${r.task === "0" ? "text-sci-causal" : "text-sci-arithmetic"}`}>
                    {r.task === "0" ? "Causal" : "Arithmetic"}
                  </td>
                  <td className="py-2 pr-4">{r.switch === "1" ? "Switch Required" : "Invariant"}</td>
                  <td className="py-2 pr-4 font-semibold text-obs-text">{r.both} / {r.pairs}</td>
                  <td className="py-2 pr-4">{r.changed} / {r.pairs}</td>
                  <td className="py-2">{r.pairs}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Deterministic Rival Policies */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <h2 className="mb-1 text-sm font-semibold text-obs-text">
          Deterministic Rival Policies vs. True Oracle (Table 3)
        </h2>
        <p className="mb-3 text-xs text-obs-secondary">
          Selected pre-registered shortcut policies evaluated across all 4,096 Cohort 029 items. Constant-on achieves 25% pair fidelity—matching the causal aggregate—but solves 0/1,024 switch pairs.
        </p>
        <div className="max-h-72 overflow-y-auto rounded border border-obs-border">
          <table className="w-full text-left font-mono text-xs tabular-nums">
            <thead className="sticky top-0 bg-obs-elevated text-obs-muted">
              <tr>
                <th className="px-3 py-2">Policy</th>
                <th className="px-3 py-2">Items / 4,096</th>
                <th className="px-3 py-2">Target Switch / 1,024</th>
                <th className="px-3 py-2">Role Switch / 1,024</th>
                <th className="px-3 py-2">Families Wrong / 128</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              {data.cohort_029_policies.slice(0, 15).map((p, i) => (
                <tr key={i} className={p.policy === "positive" ? "bg-sci-causal/10 text-obs-text" : ""}>
                  <td className="px-3 py-1.5 font-semibold">{p.policy}</td>
                  <td className="px-3 py-1.5">{p.items}</td>
                  <td className="px-3 py-1.5">{p.target_switch}</td>
                  <td className="px-3 py-1.5">{p.role_switch}</td>
                  <td className="px-3 py-1.5">{p.families_wrong}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
