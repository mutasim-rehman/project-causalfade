"use client";

import React, { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ExternalLink, Search, GitCompare } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import type { CohortRecord } from "@/lib/schemas/observatory";
import { PageHeader } from "@/components/ui/PageHeader";
import { fmtInt } from "@/lib/formatting/numbers";

export default function CohortsPage() {
  const [cohorts, setCohorts] = useState<CohortRecord[]>([]);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<string>("cohort_029");
  const [compareId, setCompareId] = useState<string>("");

  useEffect(() => {
    loadDataset<{ cohorts: CohortRecord[] }>("/data/cohorts.json").then((d) => {
      setCohorts(d.cohorts);
    });
  }, []);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return cohorts.filter(
      (c) =>
        c.cohort_id.toLowerCase().includes(q) ||
        c.title.toLowerCase().includes(q) ||
        c.models_and_formats.toLowerCase().includes(q) ||
        c.principal_finding.toLowerCase().includes(q)
    );
  }, [cohorts, search]);

  const active = useMemo(
    () => cohorts.find((c) => c.cohort_id === selectedId) ?? cohorts[0],
    [cohorts, selectedId]
  );

  const compareCohort = useMemo(
    () => (compareId ? cohorts.find((c) => c.cohort_id === compareId) ?? null : null),
    [cohorts, compareId]
  );

  const comparable =
    active && compareCohort
      ? active.comparability_group === compareCohort.comparability_group
      : true;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Complete Cohort Archive (30 Units)"
        title="Cohort Explorer"
        subtitle="Inspect every documented cohort from synthetic design validation through Cohort 029 (CF-TP1), including interrupted runs, failed gates, and retrospective audits."
      />

      {/* Search & Side-by-Side Selector */}
      <div className="grid grid-cols-1 gap-3 rounded border border-obs-border bg-obs-surface p-4 md:grid-cols-12">
        <div className="relative md:col-span-6">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-obs-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter cohorts by ID, model, or finding..."
            className="w-full rounded border border-obs-border bg-obs-elevated py-1.5 pl-8 pr-3 text-xs text-obs-text outline-none focus:border-sci-causal"
          />
        </div>
        <div className="flex items-center gap-2 md:col-span-6">
          <GitCompare className="h-4 w-4 shrink-0 text-obs-muted" />
          <select
            value={compareId}
            onChange={(e) => setCompareId(e.target.value)}
            className="w-full rounded border border-obs-border bg-obs-elevated px-3 py-1.5 font-mono text-xs text-obs-text"
          >
            <option value="">Compare with another cohort (optional)...</option>
            {cohorts.map((c) => (
              <option key={c.cohort_id} value={c.cohort_id}>
                {c.cohort_id} — {c.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Comparability Warning */}
      {compareCohort && !comparable && (
        <div className="flex items-start gap-2.5 rounded border border-sci-caution/50 bg-sci-caution/10 p-3.5 text-xs text-sci-caution">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <strong>Incompatible Experimental Designs:</strong>{" "}
            <span className="font-mono">{active?.cohort_id}</span> ({active?.comparability_group}) and{" "}
            <span className="font-mono">{compareCohort.cohort_id}</span> ({compareCohort.comparability_group}) use different tasks, scoring rules, or fixtures. Direct numerical subtraction is withheld to prevent misleading cross-cohort comparisons.
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Cohort List */}
        <div className="max-h-[680px] space-y-1.5 overflow-y-auto pr-1 lg:col-span-4">
          {filtered.map((c) => {
            const isSel = c.cohort_id === active?.cohort_id;
            return (
              <button
                key={c.cohort_id}
                type="button"
                onClick={() => setSelectedId(c.cohort_id)}
                className={`w-full rounded border p-3 text-left transition-colors ${
                  isSel
                    ? "border-sci-causal bg-sci-causal/10"
                    : "border-obs-border bg-obs-surface hover:bg-obs-elevated/60"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-mono text-xs font-semibold text-sci-causal">
                    {c.cohort_id}
                  </span>
                  <span className="font-mono text-[10px] text-obs-muted">
                    {fmtInt(c.persisted_llm_responses)} resp.
                  </span>
                </div>
                <div className="mt-1 text-xs font-medium text-obs-text">{c.title}</div>
                <div className="mt-1 flex flex-wrap gap-1">
                  <span className="rounded bg-obs-elevated px-1.5 py-0.5 font-mono text-[10px] text-obs-secondary">
                    {c.inferential_classification}
                  </span>
                  {c.has_interrupted_run && (
                    <span className="rounded bg-sci-caution/15 px-1.5 py-0.5 font-mono text-[10px] text-sci-caution">
                      Interrupted run
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>

        {/* Cohort Report Panel (and optional Side-by-Side) */}
        <div className={`space-y-4 lg:col-span-8 ${compareCohort ? "grid grid-cols-1 gap-4 md:grid-cols-2 md:space-y-0" : ""}`}>
          {[active, compareCohort].filter(Boolean).map((cohort) => {
            if (!cohort) return null;
            return (
              <div
                key={cohort.cohort_id}
                className="space-y-4 rounded border border-obs-border bg-obs-surface p-5"
              >
                <div className="border-b border-obs-border pb-3">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <span className="font-mono text-xs font-bold uppercase text-sci-causal">
                      {cohort.cohort_id} · {cohort.dates}
                    </span>
                    <span className="rounded bg-obs-elevated px-2 py-0.5 font-mono text-[11px] text-obs-secondary">
                      {cohort.inferential_classification}
                    </span>
                  </div>
                  <h2 className="mt-1 text-lg font-semibold text-obs-text">{cohort.title}</h2>
                </div>

                <div className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-2">
                  <div className="rounded border border-obs-border bg-obs-elevated/40 p-2.5">
                    <span className="font-mono text-[10px] uppercase text-obs-muted">Models & Formats</span>
                    <div className="mt-0.5 text-obs-text">{cohort.models_and_formats}</div>
                  </div>
                  <div className="rounded border border-obs-border bg-obs-elevated/40 p-2.5">
                    <span className="font-mono text-[10px] uppercase text-obs-muted">Sample & Design</span>
                    <div className="mt-0.5 text-obs-text">{cohort.sample_and_design}</div>
                  </div>
                </div>

                <div className="text-xs">
                  <div className="font-mono text-[11px] uppercase text-obs-muted">
                    Principal Finding & Interpretation
                  </div>
                  <p className="mt-1 leading-relaxed text-obs-secondary">
                    {cohort.principal_finding}
                  </p>
                </div>

                {cohort.runs.length > 0 && (
                  <div>
                    <div className="mb-1.5 font-mono text-[11px] uppercase text-obs-muted">
                      Recorded Runs ({cohort.runs.length})
                    </div>
                    <div className="max-h-48 overflow-y-auto rounded border border-obs-border">
                      <table className="w-full text-left font-mono text-[11px] tabular-nums">
                        <thead className="bg-obs-elevated text-obs-muted">
                          <tr>
                            <th className="px-2.5 py-1.5">Run ID</th>
                            <th className="px-2.5 py-1.5">Status</th>
                            <th className="px-2.5 py-1.5">Persisted / Sched</th>
                            <th className="px-2.5 py-1.5">Strict Valid</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-obs-border/60">
                          {cohort.runs.map((r) => (
                            <tr key={r.run_id}>
                              <td className="px-2.5 py-1.5 text-obs-text">{r.run_id}</td>
                              <td
                                className={`px-2.5 py-1.5 ${
                                  r.status === "interrupted" ? "text-sci-caution" : "text-sci-verified"
                                }`}
                              >
                                {r.status}
                              </td>
                              <td className="px-2.5 py-1.5 text-obs-secondary">
                                {r.persisted_raw_records} / {r.scheduled_requests}
                              </td>
                              <td className="px-2.5 py-1.5 text-obs-secondary">
                                {r.strict_valid_count ?? "N/A"}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div>
                  <div className="mb-1.5 font-mono text-[11px] uppercase text-obs-muted">
                    Pinned Source Artifacts (SHA-256)
                  </div>
                  <div className="space-y-1.5">
                    {cohort.artifacts.map((a) => (
                      <div
                        key={a.path}
                        className="flex items-center justify-between gap-2 rounded border border-obs-border bg-obs-elevated/40 px-2.5 py-1.5 font-mono text-[11px]"
                      >
                        <span className="truncate text-obs-secondary" title={a.path}>
                          {a.path}
                        </span>
                        <a
                          href={a.github_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex shrink-0 items-center gap-1 text-sci-observational hover:underline"
                        >
                          <span>GitHub</span>
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
