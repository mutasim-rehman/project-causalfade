"use client";

import React, { createContext, useContext, useState } from "react";
import { X, ExternalLink, Download, ShieldCheck, FileCode2, AlertTriangle } from "lucide-react";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";

interface EvidenceContextValue {
  openEvidence: (meta: ProvenanceMeta, title?: string) => void;
  closeEvidence: () => void;
}

const EvidenceContext = createContext<EvidenceContextValue | null>(null);

export function useEvidence() {
  const ctx = useContext(EvidenceContext);
  if (!ctx) {
    throw new Error("useEvidence must be used inside EvidenceProvider");
  }
  return ctx;
}

export function EvidenceButton({
  meta,
  title,
  label = "View evidence",
  className = "",
}: {
  meta: ProvenanceMeta;
  title?: string;
  label?: string;
  className?: string;
}) {
  const { openEvidence } = useEvidence();
  return (
    <button
      type="button"
      onClick={() => openEvidence(meta, title)}
      className={`inline-flex items-center gap-1.5 rounded border border-obs-border bg-obs-elevated px-2.5 py-1 text-xs font-medium text-obs-secondary transition-colors hover:border-sci-causal/60 hover:text-obs-text ${className}`}
    >
      <ShieldCheck className="h-3.5 w-3.5 text-sci-causal" />
      <span>{label}</span>
    </button>
  );
}

export function EvidenceProvider({ children }: { children: React.ReactNode }) {
  const [active, setActive] = useState<{ meta: ProvenanceMeta; title?: string } | null>(null);

  const openEvidence = (meta: ProvenanceMeta, title?: string) => {
    setActive({ meta, title });
  };
  const closeEvidence = () => setActive(null);

  const downloadJson = () => {
    if (!active) return;
    const blob = new Blob([JSON.stringify(active.meta, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${active.meta.metric_id}_provenance.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <EvidenceContext.Provider value={{ openEvidence, closeEvidence }}>
      {children}
      {active && (
        <div
          className="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-[1px]"
          onClick={closeEvidence}
          role="dialog"
          aria-modal="true"
          aria-label="Evidence Inspector"
        >
          <aside
            className="flex h-full w-full max-w-lg flex-col border-l border-obs-border bg-obs-surface text-obs-text shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between border-b border-obs-border px-5 py-4">
              <div>
                <div className="flex items-center gap-2 text-xs font-mono uppercase tracking-wider text-sci-causal">
                  <ShieldCheck className="h-4 w-4" />
                  <span>Provenance & Evidence Inspector</span>
                </div>
                <h2 className="mt-0.5 text-sm font-semibold text-obs-text">
                  {active.title ?? active.meta.metric_id}
                </h2>
              </div>
              <button
                type="button"
                onClick={closeEvidence}
                className="rounded p-1.5 text-obs-secondary hover:bg-obs-elevated hover:text-obs-text"
                aria-label="Close evidence drawer"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 space-y-5 overflow-y-auto px-5 py-4 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded bg-sci-causal/15 px-2 py-0.5 font-mono text-xs text-sci-causal">
                  {active.meta.classification}
                </span>
                <span className="rounded bg-obs-elevated px-2 py-0.5 font-mono text-xs text-obs-secondary">
                  {active.meta.cohort_id}
                </span>
                <span className="rounded bg-obs-elevated px-2 py-0.5 font-mono text-xs text-obs-muted">
                  commit {active.meta.git_commit.slice(0, 7)}
                </span>
              </div>

              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-obs-muted">
                  Metric Definition
                </h3>
                <p className="mt-1 leading-relaxed text-obs-secondary">
                  {active.meta.definition}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-3 rounded border border-obs-border bg-obs-elevated/60 p-3 font-mono text-xs">
                <div>
                  <span className="text-obs-muted">Metric ID</span>
                  <div className="mt-0.5 text-obs-text">{active.meta.metric_id}</div>
                </div>
                <div>
                  <span className="text-obs-muted">Unit</span>
                  <div className="mt-0.5 text-obs-text">{active.meta.unit}</div>
                </div>
                <div>
                  <span className="text-obs-muted">Unit of Analysis</span>
                  <div className="mt-0.5 text-obs-text">{active.meta.unit_of_analysis}</div>
                </div>
                {active.meta.numerator != null && active.meta.denominator != null && (
                  <div>
                    <span className="text-obs-muted">Exact Ratio</span>
                    <div className="mt-0.5 text-obs-text tabular-nums">
                      {active.meta.numerator} / {active.meta.denominator}
                    </div>
                  </div>
                )}
              </div>

              {(active.meta.statistical_test || active.meta.ci_method) && (
                <div className="space-y-2">
                  <h3 className="text-xs font-semibold uppercase tracking-wider text-obs-muted">
                    Statistical Methodology
                  </h3>
                  {active.meta.statistical_test && (
                    <p className="text-xs text-obs-secondary">
                      <span className="font-semibold text-obs-text">Test / Estimator: </span>
                      {active.meta.statistical_test}
                    </p>
                  )}
                  {active.meta.ci_method && (
                    <p className="text-xs text-obs-secondary">
                      <span className="font-semibold text-obs-text">Interval Method: </span>
                      {active.meta.ci_method}
                    </p>
                  )}
                </div>
              )}

              {active.meta.limitations && (
                <div className="rounded border border-sci-caution/40 bg-sci-caution/10 p-3">
                  <div className="flex items-center gap-1.5 text-xs font-semibold text-sci-caution">
                    <AlertTriangle className="h-3.5 w-3.5" />
                    <span>Scope & Limitations</span>
                  </div>
                  <p className="mt-1 text-xs leading-relaxed text-obs-secondary">
                    {active.meta.limitations}
                  </p>
                </div>
              )}

              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-obs-muted">
                  Pinned Source Artifacts (SHA-256 Verified)
                </h3>
                <div className="mt-2 space-y-2">
                  {active.meta.sources.map((src) => (
                    <div
                      key={src.path}
                      className="rounded border border-obs-border bg-obs-elevated/50 p-2.5 text-xs"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="truncate font-mono text-obs-text" title={src.path}>
                          {src.path}
                        </span>
                        <a
                          href={src.github_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex shrink-0 items-center gap-1 text-sci-observational hover:underline"
                        >
                          <span>GitHub</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                      {src.sha256 && (
                        <div className="mt-1 truncate font-mono text-[11px] text-obs-muted">
                          sha256:{src.sha256}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs text-obs-muted">
                <FileCode2 className="h-3.5 w-3.5" />
                <span className="font-mono">{active.meta.analysis_script}</span>
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-obs-border px-5 py-3">
              <button
                type="button"
                onClick={downloadJson}
                className="inline-flex items-center gap-1.5 rounded border border-obs-border bg-obs-elevated px-3 py-1.5 text-xs font-medium text-obs-text hover:border-sci-causal"
              >
                <Download className="h-3.5 w-3.5" />
                <span>Download Provenance JSON</span>
              </button>
              <button
                type="button"
                onClick={closeEvidence}
                className="rounded bg-obs-elevated px-3 py-1.5 text-xs font-medium text-obs-secondary hover:text-obs-text"
              >
                Close
              </button>
            </div>
          </aside>
        </div>
      )}
    </EvidenceContext.Provider>
  );
}
