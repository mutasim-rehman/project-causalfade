"use client";

import React, { useEffect, useState } from "react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";

interface Hypothesis {
  hypothesis_id: string;
  original_formulation: string;
  earliest_documented_appearance: string;
  motivation: string;
  relevant_cohorts: string;
  supporting_evidence: string;
  contradicting_or_limiting_evidence: string;
  alternative_explanations: string;
  final_scientific_status: string;
}

const STATUS_STYLE: Record<string, string> = {
  "Supported within tested scope": "bg-sci-verified/15 text-sci-verified border-sci-verified/40",
  "Contradicted by available evidence": "bg-sci-error/15 text-sci-error border-sci-error/40",
  Inconclusive: "bg-sci-caution/15 text-sci-caution border-sci-caution/40",
  "Insufficiently identified": "bg-sci-caution/15 text-sci-caution border-sci-caution/40",
  Superseded: "bg-obs-elevated text-obs-muted border-obs-border",
  Untested: "bg-obs-elevated text-obs-secondary border-obs-border",
};

export default function HypothesesPage() {
  const [items, setItems] = useState<Hypothesis[]>([]);
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    loadDataset<{ hypotheses: Hypothesis[] }>("/data/hypotheses.json").then((d) =>
      setItems(d.hypotheses)
    );
  }, []);

  const statuses = ["ALL", ...Array.from(new Set(items.map((h) => h.final_scientific_status)))];
  const filtered =
    statusFilter === "ALL"
      ? items
      : items.filter((h) => h.final_scientific_status === statusFilter);

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Complete Research Hypothesis Registry (H01–H20)"
        title="Hypothesis Ledger"
        subtitle="Transparent tracking of every formal hypothesis tested across CausalFade. Inconclusive hypotheses are never mislabeled as disproven."
      />

      <div className="flex flex-wrap gap-2">
        {statuses.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setStatusFilter(s)}
            className={`rounded border px-2.5 py-1 text-xs ${
              statusFilter === s
                ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                : "border-obs-border bg-obs-surface text-obs-secondary"
            }`}
          >
            {s}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((h) => (
          <div key={h.hypothesis_id} className="rounded border border-obs-border bg-obs-surface p-4 text-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-bold text-sci-causal">
                  {h.hypothesis_id}
                </span>
                <span className="font-mono text-[11px] text-obs-muted">
                  {h.earliest_documented_appearance} · Cohorts: {h.relevant_cohorts}
                </span>
              </div>
              <span
                className={`rounded border px-2 py-0.5 font-mono text-[11px] font-medium ${
                  STATUS_STYLE[h.final_scientific_status] ?? "bg-obs-elevated text-obs-secondary"
                }`}
              >
                {h.final_scientific_status}
              </span>
            </div>

            <p className="mt-2 text-sm font-medium text-obs-text">{h.original_formulation}</p>
            <p className="mt-1 text-obs-muted">
              <strong>Motivation:</strong> {h.motivation}
            </p>

            <div className="mt-3 grid grid-cols-1 gap-3 border-t border-obs-border pt-3 md:grid-cols-3">
              <div>
                <span className="font-mono text-[10px] uppercase text-sci-verified">
                  Supporting Evidence
                </span>
                <p className="mt-1 leading-relaxed text-obs-secondary">{h.supporting_evidence}</p>
              </div>
              <div>
                <span className="font-mono text-[10px] uppercase text-sci-error">
                  Contradicting / Limiting Evidence
                </span>
                <p className="mt-1 leading-relaxed text-obs-secondary">
                  {h.contradicting_or_limiting_evidence}
                </p>
              </div>
              <div>
                <span className="font-mono text-[10px] uppercase text-sci-caution">
                  Alternative Explanations
                </span>
                <p className="mt-1 leading-relaxed text-obs-secondary">
                  {h.alternative_explanations}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
