"use client";

import React, { useEffect, useState } from "react";
import { ExternalLink } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import { MathBlock } from "@/components/ui/MathBlock";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";

interface LiteratureData {
  initial_literature_review: {
    slug: string;
    title: string;
    authors: string[];
    year: string;
    theme: string;
    publication_status: string;
    source_url: string;
    sha256: string;
    abstract: string;
    influence_role: string;
  }[];
  manuscript_references: {
    key: string;
    title: string;
    year: string;
    edition: string;
    primary_record: string;
  }[];
  glossary: {
    term: string;
    symbol: string;
    category: string;
    definition: string;
  }[];
  provenance: ProvenanceMeta;
}

export default function LiteraturePage() {
  const [data, setData] = useState<LiteratureData | null>(null);
  const [tab, setTab] = useState<"initial" | "manuscript" | "glossary">("initial");

  useEffect(() => {
    loadDataset<LiteratureData>("/data/literature.json").then(setData);
  }, []);

  if (!data) return <div className="h-96 animate-pulse rounded bg-obs-surface" />;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Theoretical Foundations & Verified Sources"
        title="Literature & Foundations"
        subtitle="Distinguishes the 14 papers from the initial October 2026 review from methodological citations introduced during manuscript positioning. Third-party PDFs are never redistributed."
        provenance={data.provenance}
      />

      <div className="flex flex-wrap gap-2">
        {[
          { id: "initial", label: `Initial Review (${data.initial_literature_review.length} papers)` },
          { id: "manuscript", label: `Manuscript Positioning (${data.manuscript_references.length} refs)` },
          { id: "glossary", label: `Causal & Statistical Glossary (${data.glossary.length} terms)` },
        ].map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id as typeof tab)}
            className={`rounded border px-3 py-1.5 text-xs font-medium ${
              tab === t.id
                ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                : "border-obs-border bg-obs-surface text-obs-secondary"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "initial" && (
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {data.initial_literature_review.map((p) => (
            <div key={p.slug} className="rounded border border-obs-border bg-obs-surface p-4 text-xs">
              <div className="flex items-center justify-between gap-2">
                <span className="rounded bg-sci-observational/15 px-2 py-0.5 font-mono text-[10px] text-sci-observational">
                  {p.theme}
                </span>
                <a
                  href={p.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 font-mono text-[11px] text-sci-causal hover:underline"
                >
                  <span>Source</span>
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
              <h2 className="mt-2 text-sm font-semibold text-obs-text">{p.title}</h2>
              <div className="mt-1 font-mono text-[11px] text-obs-muted">
                {p.authors.slice(0, 3).join(", ")} ({p.year}) · {p.publication_status}
              </div>
              <p className="mt-2 line-clamp-3 leading-relaxed text-obs-secondary">{p.abstract}</p>
              <div className="mt-2 border-t border-obs-border pt-2 font-mono text-[10px] text-obs-muted">
                sha256: {p.sha256.slice(0, 24)}… · {p.influence_role}
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "manuscript" && (
        <div className="rounded border border-obs-border bg-obs-surface p-5">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obs-border font-mono text-[11px] uppercase text-obs-muted">
                <th className="py-2 pr-3">BibTeX Key</th>
                <th className="py-2 pr-3">Title</th>
                <th className="py-2 pr-3">Year / Venue</th>
                <th className="py-2">Primary Record</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              {data.manuscript_references.map((r) => (
                <tr key={r.key}>
                  <td className="py-2 pr-3 font-mono font-semibold text-sci-causal">{r.key}</td>
                  <td className="py-2 pr-3 text-obs-text">{r.title}</td>
                  <td className="py-2 pr-3">{r.year} · {r.edition}</td>
                  <td className="py-2">
                    <a
                      href={r.primary_record}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-sci-observational hover:underline"
                    >
                      <span>Link</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {tab === "glossary" && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {data.glossary.map((g) => (
            <div key={g.term} className="rounded border border-obs-border bg-obs-surface p-4 text-xs">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-obs-text">{g.term}</h3>
                <span className="rounded bg-obs-elevated px-2 py-0.5 font-mono text-[10px] text-obs-muted">
                  {g.category}
                </span>
              </div>
              <div className="my-2 rounded bg-obs-elevated/60 p-2 text-center text-obs-text">
                <MathBlock tex={g.symbol} />
              </div>
              <p className="leading-relaxed text-obs-secondary">{g.definition}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
