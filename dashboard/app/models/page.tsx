"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";
import { fmtPct } from "@/lib/formatting/numbers";

const comparisonCells = [
  ["decision|semantic", "Causal decision · semantic"],
  ["decision|neutral", "Causal decision · neutral"],
  ["noncausal_control|semantic", "Noncausal control · semantic"],
  ["noncausal_control|neutral", "Noncausal control · neutral"],
  ["numerical_control|semantic", "Numeric effect control"],
  ["randomized_only|semantic", "Randomized-only decision"],
  ["source_selection|semantic", "Governing source selection"],
] as const;

interface ModelsData {
  inventory: {
    model_family: string;
    source_revision: string;
    formats: string;
    size_notes: string;
    quantization_provenance: string;
    cohorts_used: string;
    evidence_path: string;
  }[];
  cohort_024_summary: {
    lineage: string;
    format: string;
    summary: { cells: Record<string, { correct: number; scheduled: number; valid: number; accuracy: number }> };
  }[];
  provenance: ProvenanceMeta;
}

export default function ModelsPage() {
  const [data, setData] = useState<ModelsData | null>(null);
  const [error, setError] = useState(false);
  const [cell, setCell] = useState<string>(comparisonCells[0][0]);
  const [inventoryFilter, setInventoryFilter] = useState("");

  useEffect(() => {
    loadDataset<ModelsData>("/data/models_quantization.json").then(setData).catch(() => setError(true));
  }, []);

  if (error) return <p role="alert">The frozen model comparison dataset is unavailable.</p>;
  if (!data) return <p role="status">Loading evaluated model configurations…</p>;

  const lineages = [...new Set(data.cohort_024_summary.map((row) => row.lineage))];
  const formats = [...new Set(data.cohort_024_summary.map((row) => row.format))];
  const inventory = data.inventory.filter((row) =>
    `${row.model_family} ${row.formats} ${row.cohorts_used}`.toLowerCase().includes(inventoryFilter.trim().toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Model Lineages & GGUF Precision Ladder"
        title="Model & Quantization Analysis"
        subtitle="Complete inventory of prepared, protocol-included, and actually evaluated model configurations across Qwen2.5 (0.5B–14B), Mistral-7B-v0.3, and Llama-3.1-8B."
        provenance={data.provenance}
      />

      <div className="flex items-start gap-2.5 rounded border border-sci-caution/40 bg-sci-caution/10 p-4 text-xs text-sci-caution">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
        <div>
          <strong>Selective degradation remains unresolved.</strong> Precision effects in Cohort 024 varied by checkpoint and task. Compare precision levels within the same checkpoint and fixture. Parsing validity and task correctness are shown separately.
        </div>
      </div>

      <section className="space-y-3 rounded border border-obs-border bg-obs-surface p-4 sm:p-5">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div>
            <h2 className="text-sm font-semibold">Cohort 024 · within-checkpoint comparison</h2>
            <p className="mt-1 text-xs leading-relaxed text-obs-secondary">Exploratory archive results on the shared development fixture. Counts use the archived scorer and scheduled denominators.</p>
          </div>
          <EvidenceButton meta={data.provenance} title="Cohort 024 model and precision matrix" />
        </div>
        <label className="flex flex-wrap items-center gap-2 text-xs text-obs-secondary">
          Task and prompt condition
          <select value={cell} onChange={(event) => setCell(event.target.value)} className="max-w-full rounded border border-obs-border bg-obs-elevated p-1.5 text-obs-text">
            {comparisonCells.map(([key, label]) => <option key={key} value={key}>{label}</option>)}
          </select>
        </label>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-obs-border text-obs-muted">
              <tr><th scope="col" className="p-2">Checkpoint</th>{formats.map((format) => <th key={format} scope="col" className="whitespace-nowrap p-2 font-mono">{format.toUpperCase()}</th>)}</tr>
            </thead>
            <tbody className="divide-y divide-obs-border">
              {lineages.map((lineage) => (
                <tr key={lineage}>
                  <th scope="row" className="whitespace-nowrap p-2 font-mono">{lineage}</th>
                  {formats.map((format) => {
                    const result = data.cohort_024_summary.find((row) => row.lineage === lineage && row.format === format)?.summary.cells[cell];
                    return result?.scheduled ? (
                      <td key={format} className="whitespace-nowrap p-2 tabular-nums" style={{ backgroundColor: `rgb(var(--sci-observational) / ${result.accuracy * 0.16})` }}>
                        <strong className="block">{fmtPct(result.accuracy, 1)}</strong>
                        <span className="block text-obs-secondary">{result.correct}/{result.scheduled} correct</span>
                        <span className="block text-obs-muted">{result.valid}/{result.scheduled} valid</span>
                      </td>
                    ) : <td key={format} className="p-2 text-obs-muted">Unavailable</td>;
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Model Inventory Table */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-sm font-semibold text-obs-text">
            Model & Precision Inventory (Prepared vs. Evaluated)
          </h2>
          <EvidenceButton meta={data.provenance} title="Model Inventory" />
        </div>
        <label className="mb-3 block text-xs text-obs-secondary">
          Search model inventory
          <input type="search" value={inventoryFilter} onChange={(event) => setInventoryFilter(event.target.value)} className="ml-2 max-w-full rounded border border-obs-border bg-obs-elevated p-1.5" />
        </label>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obs-border font-mono text-[11px] uppercase text-obs-muted">
                <th className="py-2 pr-3">Model Family</th>
                <th className="py-2 pr-3">Formats</th>
                <th className="py-2 pr-3">Size / Notes</th>
                <th className="py-2 pr-3">Quantization Provenance</th>
                <th className="py-2">Cohorts Used / Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              {inventory.map((m, idx) => {
                const neverQueried = m.cohorts_used.toLowerCase().includes("never queried") || m.cohorts_used.toLowerCase().includes("prepared only");
                return (
                  <tr key={idx}>
                    <td className="py-2.5 pr-3 font-mono font-medium text-obs-text">
                      {m.model_family}
                    </td>
                    <td className="py-2.5 pr-3 font-mono text-sci-causal">{m.formats}</td>
                    <td className="py-2.5 pr-3">{m.size_notes}</td>
                    <td className="py-2.5 pr-3 text-obs-muted">{m.quantization_provenance}</td>
                    <td className="py-2.5">
                      <span
                        className={`inline-block rounded px-1.5 py-0.5 font-mono text-[11px] ${
                          neverQueried
                            ? "bg-obs-elevated text-obs-muted"
                            : "bg-sci-verified/15 text-sci-verified"
                        }`}
                      >
                        {m.cohorts_used}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        {inventory.length === 0 && <p className="mt-2 text-sm text-obs-secondary">No model entries match this search.</p>}
      </section>
    </div>
  );
}
