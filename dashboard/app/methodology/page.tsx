"use client";

import React, { useEffect, useState } from "react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";

interface Methodology {
  methodology_id: string;
  name: string;
  purpose: string;
  mathematical_or_technical_foundation: string;
  cohorts_used: string;
  problem_addressed: string;
  empirical_outcome_and_limitations: string;
  final_disposition: string;
}

export default function MethodologyPage() {
  const [items, setItems] = useState<Methodology[]>([]);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    loadDataset<{ methodologies: Methodology[] }>("/data/methodologies.json").then((d) =>
      setItems(d.methodologies)
    );
  }, []);

  const filtered = items.filter(
    (m) =>
      m.name.toLowerCase().includes(filter.toLowerCase()) ||
      m.methodology_id.toLowerCase().includes(filter.toLowerCase()) ||
      m.final_disposition.toLowerCase().includes(filter.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Construct Validity & Controls Encyclopedia"
        title="Methodology & Controls"
        subtitle="Every experimental, statistical, and parsing methodology introduced in CausalFade—what problem it solved, what it revealed, and whether it was retained, modified, or abandoned."
      />

      <input
        type="text"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
        placeholder="Filter methodologies by name, ID, or disposition..."
        className="w-full max-w-md rounded border border-obs-border bg-obs-surface px-3 py-1.5 text-xs text-obs-text outline-none focus:border-sci-causal"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        {filtered.map((m) => (
          <div key={m.methodology_id} className="rounded border border-obs-border bg-obs-surface p-4 text-xs">
            <div className="flex items-center justify-between gap-2">
              <span className="font-mono font-bold text-sci-causal">{m.methodology_id}</span>
              <span className="rounded bg-obs-elevated px-2 py-0.5 font-mono text-[10px] text-obs-secondary">
                {m.cohorts_used}
              </span>
            </div>
            <h2 className="mt-1 text-sm font-semibold text-obs-text">{m.name}</h2>
            <p className="mt-1.5 text-obs-secondary">{m.purpose}</p>
            <div className="mt-3 space-y-2 border-t border-obs-border pt-2.5">
              <div>
                <span className="font-mono text-[10px] uppercase text-obs-muted">Mathematical / Technical Foundation: </span>
                <span className="font-mono text-[11px] text-obs-text">{m.mathematical_or_technical_foundation}</span>
              </div>
              <div>
                <span className="font-mono text-[10px] uppercase text-obs-muted">Outcome & Limitations: </span>
                <span className="text-obs-secondary">{m.empirical_outcome_and_limitations}</span>
              </div>
              <div>
                <span className="font-mono text-[10px] uppercase text-obs-muted">Disposition: </span>
                <span className="font-semibold text-sci-caution">{m.final_disposition}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
