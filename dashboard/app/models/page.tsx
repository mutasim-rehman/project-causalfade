"use client";

import React, { useEffect, useState } from "react";
import { AlertTriangle } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";

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
  provenance: ProvenanceMeta;
}

export default function ModelsPage() {
  const [data, setData] = useState<ModelsData | null>(null);

  useEffect(() => {
    loadDataset<ModelsData>("/data/models_quantization.json").then(setData);
  }, []);

  if (!data) return <div className="h-96 animate-pulse rounded bg-obs-surface" />;

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
          <strong>Core Scientific Finding on Quantization:</strong> Selective causal reasoning degradation under post-training quantization was <strong>NOT established</strong>. In Cohort 024 (3 lineages × 7 formats, 30,912 attempts), precision effects were heterogeneous and non-monotone: no F16 reference passed all component/control diagnostics, and Llama Q4_K_M suffered 448 length-capped invalids concentrated in noncausal controls while its semantic causal score (150/256) remained essentially unchanged from F16 (151/256).
        </div>
      </div>

      {/* Model Inventory Table */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-obs-text">
            Model & Precision Inventory (Prepared vs. Evaluated)
          </h2>
          <EvidenceButton meta={data.provenance} title="Model Inventory" />
        </div>
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
              {data.inventory.map((m, idx) => {
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
      </section>
    </div>
  );
}
