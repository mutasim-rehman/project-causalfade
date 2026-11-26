"use client";

import React, { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { AlertTriangle, ExternalLink, Search, GitCompare } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { CohortSchema, type CohortRecord } from "@/lib/schemas/observatory";
import { z } from "zod";
import { PageHeader } from "@/components/ui/PageHeader";
import { fmtInt } from "@/lib/formatting/numbers";

const cohortDataset = z.object({ cohorts: z.array(CohortSchema) });

export function CohortExplorer({ initialCohort = "cohort_029" }: { initialCohort?: string }) {
  const [cohorts, setCohorts] = useState<CohortRecord[]>([]);
  const [loadFailed, setLoadFailed] = useState(false);
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState(initialCohort);
  const [compareId, setCompareId] = useState<string>("");
  const [classification, setClassification] = useState("");

  useEffect(() => {
    loadDataset("/data/cohorts.json", cohortDataset)
      .then((d) => setCohorts(d.cohorts))
      .catch(() => setLoadFailed(true));
  }, []);

  useEffect(() => {
    const sync = () => {
      const query = new URLSearchParams(window.location.search);
      setSelectedId(query.get("cohort") || initialCohort);
      setCompareId(query.get("compare") || "");
    };
    sync();
    window.addEventListener("popstate", sync);
    return () => window.removeEventListener("popstate", sync);
  }, [initialCohort]);

  function updateSelection(cohort: string, compare: string) {
    const url = new URL(window.location.href);
    url.searchParams.set("cohort", cohort);
    if (compare) url.searchParams.set("compare", compare);
    else url.searchParams.delete("compare");
    window.history.replaceState(null, "", url);
    setSelectedId(cohort);
    setCompareId(compare);
  }

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return cohorts.filter(
      (c) => (!classification || c.inferential_classification === classification) &&
        [c.cohort_id, c.cohort_id.replaceAll("_", " "), c.title, c.models_and_formats, c.principal_finding]
          .some((value) => value.toLowerCase().includes(q))
    );
  }, [classification, cohorts, search]);

  const active = useMemo(
    () => cohorts.find((c) => c.cohort_id === selectedId) ?? cohorts[0],
    [cohorts, selectedId]
  );

  const compareCohort = useMemo(
    () => (compareId && active?.cohort_id !== compareId ? cohorts.find((c) => c.cohort_id === compareId) ?? null : null),
    [active, cohorts, compareId]
  );

  const comparable =
    active && compareCohort
      ? active.comparability_group === compareCohort.comparability_group
      : true;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow={cohorts.length ? `${cohorts.length} documented cohort entries` : "Cohort archive"}
        title="Cohort Explorer"
        subtitle="Inspect every documented cohort from synthetic design validation through Cohort 029 (CF-TP1), including interrupted runs, failed gates, and retrospective audits."
      />
      {loadFailed && <p role="alert">The frozen cohort archive could not be loaded.</p>}
      {!loadFailed && !cohorts.length && <p role="status">Loading the frozen cohort archive…</p>}

      {/* Search & Side-by-Side Selector */}
      <div className="grid grid-cols-1 gap-3 rounded border border-obs-border bg-obs-surface p-4 md:grid-cols-12">
        <div className="relative md:col-span-4">
          <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-obs-muted" />
          <input
            type="text"
            aria-label="Filter cohorts"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Filter cohorts by ID, model, or finding..."
            className="w-full rounded border border-obs-border bg-obs-elevated py-1.5 pl-8 pr-3 text-xs text-obs-text outline-none focus:border-sci-causal"
          />
        </div>
        <select
          aria-label="Filter scientific classification"
          value={classification}
          onChange={(e) => setClassification(e.target.value)}
          className="min-w-0 w-full rounded border border-obs-border bg-obs-elevated px-3 py-1.5 text-xs md:col-span-4"
        >
          <option value="">All scientific classifications</option>
          {Array.from(new Set(cohorts.map((c) => c.inferential_classification))).filter(Boolean).sort().map((value) => (
            <option key={value}>{value}</option>
          ))}
        </select>
        <div className="flex min-w-0 items-center gap-2 md:col-span-4">
          <GitCompare className="h-4 w-4 shrink-0 text-obs-muted" />
          <select
            aria-label="Compare with another cohort"
            value={compareCohort?.cohort_id ?? ""}
            onChange={(e) => updateSelection(active?.cohort_id ?? selectedId, e.target.value)}
            className="min-w-0 w-full rounded border border-obs-border bg-obs-elevated px-3 py-1.5 font-mono text-xs text-obs-text"
          >
            <option value="">Compare with another cohort (optional)...</option>
            {cohorts.filter((c) => c !== active).map((c) => (
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
          {cohorts.length > 0 && filtered.length === 0 && <p role="status" className="p-3 text-sm text-obs-muted">No cohorts match these filters.</p>}
          {filtered.map((c) => {
            const isSel = c.cohort_id === active?.cohort_id;
            return (
              <button
                key={c.cohort_id}
                type="button"
                aria-pressed={isSel}
                onClick={() => updateSelection(c.cohort_id, c.cohort_id === compareId ? "" : compareId)}
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
        <div className={`min-w-0 space-y-4 lg:col-span-8 ${compareCohort ? "grid grid-cols-1 gap-4 md:grid-cols-2 md:space-y-0" : ""}`}>
          {[active, compareCohort].filter(Boolean).map((cohort) => {
            if (!cohort) return null;
            return (
              <div
                key={cohort.cohort_id}
                className="min-w-0 space-y-4 rounded border border-obs-border bg-obs-surface p-5"
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
                  {cohort.cohort_id !== initialCohort && <Link prefetch={false} href={`/cohorts/${cohort.cohort_id}/`} className="mt-2 inline-block text-xs text-sci-causal hover:underline">
                    Open cohort report
                  </Link>}
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
