"use client";

import React, { useEffect, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, MarkerType, Position, type Node, type Edge, type OnNodesChange } from "@xyflow/react";
import type { EChartsOption } from "echarts";
import { AlertTriangle, RefreshCw } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { CausalLabDataSchema, type CausalLabData } from "@/lib/schemas/observatory";
import { PageHeader } from "@/components/ui/PageHeader";
import { MathBlock } from "@/components/ui/MathBlock";
import { EChartBox } from "@/components/charts/EChartBox";
import { fmtPP } from "@/lib/formatting/numbers";

export default function CausalLab() {
  const [data, setData] = useState<CausalLabData | null>(null);
  const [error, setError] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<number>(0);
  const [role, setRole] = useState<"L" | "R">("L");
  const [regime, setRegime] = useState<"randomized" | "historical">("randomized");
  const [weightPct, setWeightPct] = useState<number>(0);
  const [nodePositions, setNodePositions] = useState<Record<string, Node["position"]>>({});
  const onNodesChange: OnNodesChange = (changes) => {
    const moved = changes.flatMap((change) =>
      change.type === "position" && change.position ? [[change.id, change.position] as const] : []
    );
    if (moved.length) setNodePositions((positions) => ({ ...positions, ...Object.fromEntries(moved) }));
  };

  useEffect(() => {
    loadDataset("/data/causal_lab.json", CausalLabDataSchema).then((d) => {
      setData(d);
      const fam = d.families.find((f) => f.slot === d.featured_slot) ?? d.families[0];
      if (fam) {
        setSelectedSlot(fam.slot);
        setWeightPct(fam.weights_pct[0]);
      }
    }).catch(() => setError(true));
  }, []);

  const family = useMemo(() => {
    if (!data) return null;
    return data.families.find((f) => f.slot === selectedSlot) ?? data.families[0];
  }, [data, selectedSlot]);

  const isExactFrozenWeight = useMemo(() => {
    if (!family) return false;
    return weightPct === family.weights_pct[0] || weightPct === family.weights_pct[1];
  }, [family, weightPct]);

  const effects = useMemo(() => {
    if (!family) return null;
    const eff = role === "L" ? family.stratum_effects_pp.L : family.stratum_effects_pp.R;
    const tau = (weightPct * eff.delta_1 + (100 - weightPct) * eff.delta_0) / 100;
    const optimal = tau > 0 ? 1 : 0;
    // Threshold w* where w*delta_1 + (1-w)*delta_0 = 0 => w* = -delta_0 / (delta_1 - delta_0)
    const denom = eff.delta_1 - eff.delta_0;
    const thresholdPct = denom !== 0 ? (-eff.delta_0 / denom) * 100 : null;
    const historical = family.stratum_effects_pp[role === "L" ? "R" : "L"];
    return {
      delta_1: eff.delta_1,
      delta_0: eff.delta_0,
      tau,
      historicalGap: (weightPct * historical.delta_1 + (100 - weightPct) * historical.delta_0) / 100,
      optimal,
      thresholdPct,
    };
  }, [family, role, weightPct]);

  const dagNodes: Node[] = useMemo(() => {
    return [
      {
        id: "S",
        position: { x: 40, y: 20 },
        data: { label: `Stratum S\nP(S=1) = ${weightPct}%` },
        style: { background: "#162231", color: "#55D6BE", border: "1px solid #55D6BE", fontSize: 12, width: 150 },
      },
      {
        id: "U",
        position: { x: 40, y: 170 },
        data: { label: "Unmeasured Risk U\nP(U=1|S) = 0.5" },
        style: {
          background: "#162231",
          color: "#94A3B8",
          border: "1px solid #94A3B8",
          fontSize: 12,
          width: 150,
        },
      },
      {
        id: "A",
        position: { x: 280, y: 95 },
        data: {
          label:
            regime === "randomized"
              ? `Randomly assigned A\n(Table ${role})`
              : `Treatment Choice A\n(Table ${role === "L" ? "R" : "L"} Historical)`,
        },
        style: {
          background: "#111827",
          color: regime === "randomized" ? "#55D6BE" : "#60A5FA",
          border: `2px solid ${regime === "randomized" ? "#55D6BE" : "#60A5FA"}`,
          fontSize: 12,
          width: 180,
        },
      },
      {
        id: "Y",
        position: { x: 540, y: 95 },
        data: { label: "Outcome Y\nSuccess Rate (%)" },
        style: { background: "#111827", color: "#F1F5F9", border: "1px solid #F1F5F9", fontSize: 12, width: 150 },
      },
    ];
  }, [weightPct, regime, role]);

  const dagEdges: Edge[] = useMemo(() => {
    const edges: Edge[] = [
      { id: "s-y", source: "S", target: "Y", label: "Effect modifier", style: { stroke: "#55D6BE" } },
      { id: "u-y", source: "U", target: "Y", label: "Risk affects outcome", style: { stroke: "#94A3B8" } },
      {
        id: "a-y",
        source: "A",
        target: "Y",
        label: "Treatment affects outcome",
        style: { stroke: "#55D6BE", strokeWidth: 2 },
        labelStyle: { fill: "rgb(var(--sci-causal))", fontSize: 11 },
      },
    ];
    if (regime === "historical") {
      edges.push({
        id: "u-a",
        source: "U",
        target: "A",
        label: "Confounding (1+2U)/4",
        style: { stroke: "#60A5FA", strokeDasharray: "5 4", strokeWidth: 2 },
        labelStyle: { fill: "rgb(var(--sci-observational))", fontSize: 10 },
      });
    }
    return edges.map((edge) => ({
      ...edge,
      markerEnd: { type: MarkerType.ArrowClosed, color: String(edge.style?.stroke ?? "#94A3B8"), width: 16, height: 16 },
      labelStyle: { fill: "var(--text-secondary)", fontSize: 10, ...edge.labelStyle },
    }));
  }, [regime]);

  const curveOption = useMemo<EChartsOption>(() => {
    if (!family || !effects) return {};
    const xs = Array.from({ length: 101 }, (_, i) => i);
    const lLine = xs.map(
      (w) => +((w / 100) * family.stratum_effects_pp.L.delta_1 + (1 - w / 100) * family.stratum_effects_pp.L.delta_0).toFixed(3)
    );
    const rLine = xs.map(
      (w) => +((w / 100) * family.stratum_effects_pp.R.delta_1 + (1 - w / 100) * family.stratum_effects_pp.R.delta_0).toFixed(3)
    );
    return {
      backgroundColor: "transparent",
      tooltip: { trigger: "axis", backgroundColor: "#111827", borderColor: "#263142", textStyle: { color: "#F1F5F9", fontSize: 11 } },
      legend: { data: ["If L governs", "If R governs"], textStyle: { color: "#94A3B8", fontSize: 11 }, top: 4 },
      grid: { left: 50, right: 20, top: 38, bottom: 38 },
      xAxis: {
        type: "category",
        data: xs,
        name: "Target Stratum 1 Share w (%)",
        nameLocation: "middle",
        nameGap: 24,
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8", interval: 19 },
      },
      yAxis: {
        type: "value",
        name: "τ(w) (pp)",
        nameTextStyle: { color: "#94A3B8", fontSize: 11 },
        axisLabel: { color: "#94A3B8" },
        splitLine: { lineStyle: { color: "#1E293B" } },
      },
      series: [
        {
          name: "If L governs",
          type: "line",
          showSymbol: false,
          data: lLine,
          itemStyle: { color: "#55D6BE" },
          lineStyle: { color: "#55D6BE", width: role === "L" ? 3 : 1.5, type: role === "L" ? "solid" : "dashed" },
        },
        {
          name: "If R governs",
          type: "line",
          showSymbol: false,
          data: rLine,
          itemStyle: { color: "#A78BFA" },
          lineStyle: { color: "#A78BFA", width: role === "R" ? 3 : 1.5, type: role === "R" ? "solid" : "dashed" },
        },
        {
          name: "Current w",
          type: "scatter",
          symbolSize: 10,
          itemStyle: { color: "#FBBF24" },
          data: [[weightPct, +effects.tau.toFixed(3)]],
        },
      ],
    };
  }, [family, effects, role, weightPct]);

  if (error) return <p role="alert">The frozen causal lab dataset is unavailable.</p>;
  if (!data) return <p role="status">Loading the frozen causal lab families…</p>;
  if (!family || !effects) return <p role="status">No numerical families are available in this snapshot.</p>;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Interactive Mathematical & Causal Simulator"
        title="Causal Inference Laboratory"
        subtitle="Explore how CF-TP1 constructs two observationally feasible worlds from identical tables, why intervention severs the confounding edge U → A, and how changing target population composition w reverses the optimal action."
        provenance={data.provenance}
      />

      {/* Preset & Regime Controls */}
      <section className="grid grid-cols-1 gap-4 rounded border border-obs-border bg-obs-surface p-4 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <label htmlFor="lab-family" className="block font-mono text-[11px] uppercase text-obs-muted">
            Cohort 029 Family Preset ({data.families.length} available)
          </label>
          <select
            id="lab-family"
            value={selectedSlot}
            onChange={(e) => {
              const s = Number(e.target.value);
              setSelectedSlot(s);
              const f = data.families.find((x) => x.slot === s);
              if (f) setWeightPct(f.weights_pct[0]);
            }}
            className="mt-1.5 w-full rounded border border-obs-border bg-obs-elevated px-3 py-1.5 font-mono text-xs text-obs-text"
          >
            {data.families.map((f) => (
              <option key={f.slot} value={f.slot}>
                {f.family_id} (p={f.p}, g={f.g}, b={f.b > 0 ? "+1" : "-1"})
                {f.slot === data.featured_slot ? " · Manuscript Fig 1" : ""}
              </option>
            ))}
          </select>
        </div>

        <div className="lg:col-span-4">
          <span className="block font-mono text-[11px] uppercase text-obs-muted">
            Governing Randomized Table
          </span>
          <div className="mt-1.5 grid grid-cols-2 gap-2">
            {(["L", "R"] as const).map((r) => (
              <button
                key={r}
                type="button"
                aria-pressed={role === r}
                onClick={() => setRole(r)}
                className={`rounded border px-3 py-1.5 font-mono text-xs font-medium ${
                  role === r
                    ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                    : "border-obs-border bg-obs-elevated text-obs-secondary"
                }`}
              >
                Table {r} Governs
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-4">
          <span className="block font-mono text-[11px] uppercase text-obs-muted">
            Causal DAG Regime
          </span>
          <div className="mt-1.5 grid grid-cols-2 gap-2">
            <button
              type="button"
              aria-pressed={regime === "randomized"}
              onClick={() => setRegime("randomized")}
              className={`rounded border px-3 py-1.5 font-mono text-xs font-medium ${
                regime === "randomized"
                  ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                  : "border-obs-border bg-obs-elevated text-obs-secondary"
              }`}
            >
              Randomized trial
            </button>
            <button
              type="button"
              aria-pressed={regime === "historical"}
              onClick={() => setRegime("historical")}
              className={`rounded border px-3 py-1.5 font-mono text-xs font-medium ${
                regime === "historical"
                  ? "border-sci-observational bg-sci-observational/15 text-sci-observational"
                  : "border-obs-border bg-obs-elevated text-obs-secondary"
              }`}
            >
              Historical (Confounded)
            </button>
          </div>
        </div>
      </section>

      {/* DAG + Population Simulator */}
      <section className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="rounded border border-obs-border bg-obs-surface p-4 lg:col-span-6">
          <div className="mb-2 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-obs-text">
              Causal Structure (DAG) — {regime === "randomized" ? "Incoming U → A Severed" : "Confounded by Unmeasured U"}
            </h2>
          </div>
          <div className="h-72 w-full rounded border border-obs-border bg-obs-bg">
            <ReactFlow
              nodes={dagNodes.map((node) => ({
                ...node,
                sourcePosition: Position.Right,
                targetPosition: Position.Left,
                position: nodePositions[node.id] ?? node.position,
              }))}
              edges={dagEdges}
              onNodesChange={onNodesChange}
              nodesConnectable={false}
              fitView
              minZoom={0.2}
            >
              <Background color="#1E293B" gap={20} />
              <Controls />
            </ReactFlow>
          </div>
          <div className="mt-3 rounded border border-obs-border bg-obs-elevated/50 p-3 text-xs text-obs-secondary">
            <div className="mb-1 font-mono text-[11px] uppercase text-obs-muted">
              Standardization Estimand (Equation 1)
            </div>
            <div className="py-1 text-center text-obs-text">
              <MathBlock tex={data.equation} display />
            </div>
            <div className="mt-1 font-mono text-[11px] text-obs-secondary">
              Substituted ({role} governs, w = {(weightPct / 100).toFixed(2)}):{" "}
              <span className="text-sci-causal">
                ({(weightPct / 100).toFixed(2)})({effects.delta_1.toFixed(2)}) + (
                {(1 - weightPct / 100).toFixed(2)})({effects.delta_0.toFixed(2)}) ={" "}
                {effects.tau > 0 ? "+" : ""}
                {effects.tau.toFixed(3)} pp
              </span>
            </div>
          </div>
        </div>

        <div className="flex flex-col justify-between rounded border border-obs-border bg-obs-surface p-4 lg:col-span-6">
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-sm font-semibold text-obs-text">
                Target Population Composition Simulator
              </h2>
              <div className="flex gap-1.5">
                {family.weights_pct.map((w, idx) => (
                  <button
                    key={idx}
                    type="button"
                    aria-pressed={weightPct === w}
                    onClick={() => setWeightPct(w)}
                    className={`rounded border px-2 py-0.5 font-mono text-[11px] ${
                      weightPct === w
                        ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                        : "border-obs-border bg-obs-elevated text-obs-secondary"
                    }`}
                  >
                    Frozen w{idx}={w}%
                  </button>
                ))}
              </div>
            </div>

            {!isExactFrozenWeight && (
              <div className="flex items-center gap-2 rounded border border-sci-caution/40 bg-sci-caution/10 px-3 py-2 text-xs text-sci-caution">
                <AlertTriangle className="h-4 w-4 shrink-0" />
                <span>
                  Illustrative example — not an experimental observation. The LLM was evaluated only at frozen weights w₀={family.weights_pct[0]}% and w₁={family.weights_pct[1]}%.
                </span>
              </div>
            )}

            <div>
              <div className="flex justify-between font-mono text-xs">
                <span className="text-obs-secondary">Stratum 1 Share (w)</span>
                <span className="font-semibold text-sci-causal tabular-nums">
                  {weightPct}% (Stratum 0: {100 - weightPct}%)
                </span>
              </div>
              <input
                type="range"
                aria-label="Target stratum 1 share"
                min={0}
                max={100}
                value={weightPct}
                onChange={(e) => setWeightPct(Number(e.target.value))}
                className="mt-2 w-full accent-[#55D6BE]"
              />
            </div>

            <div className="grid grid-cols-3 gap-3 rounded border border-obs-border bg-obs-elevated/60 p-3 font-mono text-xs">
              <div>
                <span className="text-obs-muted">Weighted Effect τ(w)</span>
                <div className="mt-0.5 text-base font-semibold tabular-nums text-sci-causal">
                  {effects.tau > 0 ? "+" : ""}
                  {effects.tau.toFixed(3)} pp
                </div>
              </div>
              <div>
                <span className="text-obs-muted">Optimal Action a*</span>
                <div className="mt-0.5 text-base font-semibold text-obs-text">
                  {effects.optimal === 1 ? "ACTIVATE (1)" : "LEAVE OFF (0)"}
                </div>
              </div>
              <div>
                <span className="text-obs-muted">Reversal Threshold w*</span>
                <div className="mt-0.5 text-base font-semibold text-sci-caution tabular-nums">
                  {effects.thresholdPct !== null &&
                  effects.thresholdPct >= 0 &&
                  effects.thresholdPct <= 100
                    ? `${effects.thresholdPct.toFixed(1)}%`
                    : "No sign flip"}
                </div>
              </div>
            </div>

            <p className="text-xs leading-relaxed text-obs-secondary">
              The weighted historical association is <strong className="text-sci-observational">{fmtPP(effects.historicalGap, 3)}</strong> at the same target weight. Historical treatment assignment depends on unmeasured risk, so the randomized table determines the target intervention effect.
            </p>

            <EChartBox option={curveOption} height={220} exportName={`causal-lab-${family.family_id}`} />
          </div>
        </div>
      </section>

      {/* Displayed Tables L and R */}
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {(["L", "R"] as const).map((tbl) => {
          const rows = family.tables_pct[tbl];
          const eff = tbl === "L" ? family.stratum_effects_pp.L : family.stratum_effects_pp.R;
          const isGov = role === tbl;
          return (
            <div
              key={tbl}
              className={`rounded border p-4 ${
                isGov ? "border-sci-causal bg-obs-surface" : "border-obs-border bg-obs-surface/70"
              }`}
            >
              <div className="mb-2 flex items-center justify-between">
                <h3 className="font-mono text-xs font-semibold uppercase text-obs-text">
                  Table {tbl} — {isGov ? "Governing Randomized Trial" : "Historical Observational Study"}
                </h3>
                <span
                  className={`rounded px-2 py-0.5 font-mono text-[10px] ${
                    isGov ? "bg-sci-causal/15 text-sci-causal" : "bg-sci-observational/15 text-sci-observational"
                  }`}
                >
                  {isGov ? "Causal Source" : "Confounded Source"}
                </span>
              </div>
              <table className="w-full text-left font-mono text-xs tabular-nums">
                <thead>
                  <tr className="border-b border-obs-border text-obs-muted">
                    <th className="py-1.5">Stratum</th>
                    <th className="py-1.5">Off (A=0)</th>
                    <th className="py-1.5">On (A=1)</th>
                    <th className="py-1.5">Contrast (On − Off)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-obs-border/50">
                    <td className="py-1.5 text-obs-secondary">Stratum 1 (Amber)</td>
                    <td className="py-1.5">{rows[0][0].toFixed(1)}%</td>
                    <td className="py-1.5">{rows[0][1].toFixed(1)}%</td>
                    <td className="py-1.5 font-semibold text-obs-text">
                      {eff.delta_1 > 0 ? "+" : ""}
                      {eff.delta_1.toFixed(1)} pp
                    </td>
                  </tr>
                  <tr>
                    <td className="py-1.5 text-obs-secondary">Stratum 0 (Blue)</td>
                    <td className="py-1.5">{rows[1][0].toFixed(1)}%</td>
                    <td className="py-1.5">{rows[1][1].toFixed(1)}%</td>
                    <td className="py-1.5 font-semibold text-obs-text">
                      {eff.delta_0 > 0 ? "+" : ""}
                      {eff.delta_0.toFixed(1)} pp
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          );
        })}
      </section>
    </div>
  );
}
