"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { Download, Search, AlertTriangle, ExternalLink } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";

interface ArchiveEntry {
  id: string;
  title: string;
  total_responses: number;
  chunks: string[];
}

interface RawRow {
  task_id: string;
  slot?: number;
  form_label?: string;
  task_label?: string;
  order_label?: string;
  role_label?: string;
  target?: number;
  gold_action?: number;
  predicted_action?: number | null;
  valid?: boolean | null;
  correct?: boolean | null;
  raw_response: string | null;
  user_prompt?: string;
  system_prompt?: string;
  arm?: string;
  family_id?: string;
  condition?: string;
  order?: string;
  status?: string;
  error?: string | null;
  source_path?: string;
  finish_reason?: string;
}

function csvCell(value: string | number | boolean | null | undefined) {
  const text = String(value ?? "");
  const formulaSafe = /^[\s\uFEFF]*[=+\-@]|^[\t\r\n]/.test(text) ? `'${text}` : text;
  return `"${formulaSafe.replaceAll('"', '""')}"`;
}

export default function ResponsesPage() {
  const [archives, setArchives] = useState<ArchiveEntry[]>([]);
  const [gitCommit, setGitCommit] = useState("");
  const [archiveError, setArchiveError] = useState(false);
  const [selectedArchive, setSelectedArchive] = useState("cohort_029");
  const [selectedChunkIdx, setSelectedChunkIdx] = useState(0);
  const [rows, setRows] = useState<RawRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [chunkError, setChunkError] = useState(false);

  const [search, setSearch] = useState("");
  const [taskFilter, setTaskFilter] = useState("ALL");
  const [correctFilter, setCorrectFilter] = useState("ALL");
  const [validityFilter, setValidityFilter] = useState("ALL");
  const [activeRow, setActiveRow] = useState<RawRow | null>(null);
  const [pairState, setPairState] = useState<{ id: string; row?: RawRow; state: "loading" | "unavailable" | "loaded" } | null>(null);

  const parentRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    loadDataset<{ archives: ArchiveEntry[]; git_commit: string }>("/data/responses/index.json")
      .then((d) => {
        setArchives(d.archives);
        setGitCommit(d.git_commit);
      })
      .catch(() => setArchiveError(true));
  }, []);

  const currentArchive = useMemo(
    () => archives.find((a) => a.id === selectedArchive),
    [archives, selectedArchive]
  );

  useEffect(() => {
    if (!currentArchive) return;
    const chunkPath = currentArchive.chunks[selectedChunkIdx] ?? currentArchive.chunks[0];
    if (!chunkPath) return;
    let current = true;
    setLoading(true);
    setChunkError(false);
    setRows([]);
    setActiveRow(null);
    setPairState(null);
    loadDataset<RawRow[]>(chunkPath)
      .then((d) => {
        if (current) setRows(d);
      })
      .catch(() => { if (current) setChunkError(true); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [currentArchive, selectedChunkIdx]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter((r) => {
      if (taskFilter !== "ALL" && r.task_label !== taskFilter) return false;
      if (correctFilter === "CORRECT" && r.correct !== true) return false;
      if (correctFilter === "INCORRECT" && r.correct !== false) return false;
      if (correctFilter === "UNAVAILABLE" && r.correct != null) return false;
      if (validityFilter === "VALID" && r.valid !== true) return false;
      if (validityFilter === "INVALID" && r.valid !== false) return false;
      if (validityFilter === "UNAVAILABLE" && r.valid != null) return false;
      if (q) {
        const hay = [r.task_id, r.slot, r.family_id, r.arm, r.form_label, r.order_label, r.order, r.condition, r.status, r.raw_response].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [rows, taskFilter, correctFilter, search, validityFilter]);
  const inspected = activeRow && filtered.includes(activeRow) ? activeRow : null;
  const sourcePath = inspected?.source_path ?? (selectedArchive === "cohort_029" ? "experiments/cohort_029/runs/confirmatory/events.jsonl" : null);
  const pair = pairState?.id === inspected?.task_id ? pairState : null;

  async function compareTargetPair(row: RawRow) {
    const target = row.target;
    if (!currentArchive || target == null) return;
    setPairState({ id: row.task_id, state: "loading" });
    try {
      const matches = (candidate: RawRow) => candidate.slot === row.slot
        && candidate.task_label === row.task_label && candidate.form_label === row.form_label
        && candidate.order_label === row.order_label && candidate.role_label === row.role_label
        && candidate.target === 1 - target;
      const localMatch = rows.find(matches);
      const counterpart = localMatch ?? (await Promise.all(currentArchive.chunks.map((chunk) => loadDataset<RawRow[]>(chunk)))).flat().find(matches);
      setPairState((current) => current?.id === row.task_id
        ? { id: row.task_id, state: counterpart ? "loaded" : "unavailable", row: counterpart } : current);
    } catch {
      setPairState((current) => current?.id === row.task_id ? { id: row.task_id, state: "unavailable" } : current);
    }
  }

  const rowVirtualizer = useVirtualizer({
    count: filtered.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 12,
  });

  const exportCsv = () => {
    const header = ["task_id", "slot", "task_label", "form_label", "gold_action", "predicted_action", "valid", "correct", "raw_response"];
    const lines = [
      header.join(","),
      ...filtered.map((r) =>
        [
          r.task_id,
          r.slot ?? "",
          r.task_label ?? "",
          r.form_label ?? "",
          r.gold_action ?? "",
          r.predicted_action ?? "",
          r.valid,
          r.correct ?? "",
          r.raw_response,
        ].map(csvCell).join(",")
      ),
    ];
    const blob = new Blob([lines.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${selectedArchive}_filtered_responses.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Lazy-Loaded Verbatim Archive"
        title="Raw Response Explorer"
        subtitle="Inspect verbatim model prompts and raw completions without HTML interpretation or post-hoc rewriting. Chunks load on demand to keep startup lightweight."
      >
        <button
          type="button"
          onClick={exportCsv}
          disabled={!filtered.length || loading}
          className="inline-flex items-center gap-1.5 rounded border border-obs-border bg-obs-elevated px-3 py-1.5 text-xs font-medium text-obs-text hover:border-sci-causal disabled:opacity-40"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export filtered chunk (CSV)</span>
        </button>
      </PageHeader>
      {archiveError && <p role="alert">The response archive index is unavailable.</p>}
      {chunkError && <p role="alert">The selected response chunk could not be loaded.</p>}

      {/* Archive & Filter Controls */}
      <div className="grid grid-cols-1 gap-3 rounded border border-obs-border bg-obs-surface p-4 md:grid-cols-12">
        <div className="md:col-span-4">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Archive</label>
          <select
            aria-label="Archive"
            value={selectedArchive}
            onChange={(e) => {
              setSelectedArchive(e.target.value);
              setSelectedChunkIdx(0);
              setTaskFilter("ALL");
              setCorrectFilter("ALL");
              setValidityFilter("ALL");
              setSearch("");
            }}
            className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text"
          >
            {archives.map((a) => (
              <option key={a.id} value={a.id}>
                {a.title} ({a.total_responses})
              </option>
            ))}
          </select>
        </div>

        {currentArchive && currentArchive.chunks.length > 1 && (
          <div className="md:col-span-2">
            <label className="block font-mono text-[10px] uppercase text-obs-muted">Chunk</label>
            <select
              aria-label="Response chunk"
              value={selectedChunkIdx}
              onChange={(e) => setSelectedChunkIdx(Number(e.target.value))}
              className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text"
            >
              {currentArchive.chunks.map((_, idx) => (
                <option key={idx} value={idx}>
                  Part {idx + 1} / {currentArchive.chunks.length}
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="md:col-span-2">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Task</label>
          <select
            aria-label="Task type"
            disabled={selectedArchive !== "cohort_029"}
            value={taskFilter}
            onChange={(e) => setTaskFilter(e.target.value)}
            className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text"
          >
            <option value="ALL">All Tasks</option>
            <option value="causal">Causal</option>
            <option value="arithmetic">Arithmetic</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Outcome</label>
          <select
            aria-label="Scoring outcome"
            value={correctFilter}
            onChange={(e) => setCorrectFilter(e.target.value)}
            className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text"
          >
            <option value="ALL">All Outcomes</option>
            <option value="CORRECT">Correct Only</option>
            <option value="INCORRECT">Incorrect Only</option>
            <option value="UNAVAILABLE">Unscored or unavailable</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">
            Validity
            <select value={validityFilter} onChange={(e) => setValidityFilter(e.target.value)} className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text">
              <option value="ALL">All records</option>
              <option value="VALID">Valid</option>
              <option value="INVALID">Invalid</option>
              <option value="UNAVAILABLE">Unavailable</option>
            </select>
          </label>
        </div>

        <div className="md:col-span-4">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Search</label>
          <div className="relative mt-1">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-obs-muted" />
            <input
              type="text"
              aria-label="Search selected chunk"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="ID, slot, text..."
              className="w-full rounded border border-obs-border bg-obs-elevated py-1.5 pl-8 pr-2 font-mono text-xs text-obs-text outline-none"
            />
          </div>
        </div>
      </div>

      {selectedArchive === "cohort_008_interrupted" && (
        <div className="flex items-center gap-2 rounded border border-sci-caution/40 bg-sci-caution/10 p-3 text-xs text-sci-caution">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>
            Interrupted Run Artifact: Cohort 008 Run 1 stopped at user PC-shutdown request with 26/64 persisted lines (25 completed + 1 interrupted).
          </span>
        </div>
      )}

      {/* Virtualized Table + Detail Inspector */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <div className="min-w-0 rounded border border-obs-border bg-obs-surface lg:col-span-6">
          <div className="flex items-center justify-between border-b border-obs-border px-3 py-2 font-mono text-[11px] text-obs-muted">
            <span>Showing {filtered.length} records {loading ? "(loading...)" : ""}</span>
            <span>Click row to inspect verbatim</span>
          </div>
          <div ref={parentRef} className="h-[520px] overflow-auto">
            <div style={{ height: `${rowVirtualizer.getTotalSize()}px`, position: "relative" }}>
              {rowVirtualizer.getVirtualItems().map((vRow) => {
                const r = filtered[vRow.index];
                const isSel = activeRow?.task_id === r.task_id && activeRow?.arm === r.arm;
                return (
                  <button
                    key={vRow.key}
                    type="button"
                    aria-pressed={isSel}
                    onClick={() => {
                      if (r !== activeRow) setPairState(null);
                      setActiveRow(r);
                    }}
                    style={{
                      position: "absolute",
                      top: 0,
                      left: 0,
                      width: "100%",
                      height: `${vRow.size}px`,
                      transform: `translateY(${vRow.start}px)`,
                    }}
                    className={`flex items-center justify-between border-b border-obs-border/50 px-3 text-left font-mono text-xs ${
                      isSel ? "bg-sci-causal/15 text-obs-text" : "hover:bg-obs-elevated/50 text-obs-secondary"
                    }`}
                  >
                    <span className="truncate w-28">{r.task_id.slice(0, 10)}…</span>
                    <span className="w-20 truncate">{r.task_label ?? r.arm ?? r.status}</span>
                    <span className="w-20">
                      Gold:{r.gold_action ?? "?"} Pred:{r.predicted_action ?? "—"}
                    </span>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[10px] ${
                        r.correct === true
                          ? "bg-sci-verified/15 text-sci-verified"
                          : r.correct === false ? "bg-sci-error/15 text-sci-error" : "text-obs-muted"
                      }`}
                    >
                      {r.correct === true ? "Correct" : r.correct === false ? "Incorrect" : "Unscored"}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Detail Inspector */}
        <div className="min-w-0 rounded border border-obs-border bg-obs-surface p-4 lg:col-span-6">
          {inspected ? (
            <div className="space-y-4 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-obs-border pb-2.5">
                <span className="min-w-0 break-all font-mono font-semibold text-sci-causal">
                  {inspected.task_id}
                </span>
                <div className="flex gap-1.5 font-mono text-[11px]">
                  {inspected.form_label && (
                    <span className="rounded bg-obs-elevated px-2 py-0.5">{inspected.form_label}</span>
                  )}
                  {inspected.role_label && (
                    <span className="rounded bg-obs-elevated px-2 py-0.5">{inspected.role_label}</span>
                  )}
                </div>
              </div>

              <dl className="grid grid-cols-2 gap-2 text-obs-secondary">
                <div><dt>Oracle action</dt><dd className="font-mono">{inspected.gold_action ?? "Unavailable"}</dd></div>
                <div><dt>Parsed action</dt><dd className="font-mono">{inspected.predicted_action ?? "Unavailable"}</dd></div>
                <div><dt>Action validity</dt><dd>{inspected.valid == null ? "Unavailable" : inspected.valid ? "Valid" : "Invalid"}</dd></div>
                <div><dt>Recorded status</dt><dd>{inspected.status ?? inspected.finish_reason ?? "Unavailable"}</dd></div>
              </dl>
              {gitCommit && sourcePath && <a href={`https://github.com/mutasim-rehman/project-causalfade/blob/${gitCommit}/${sourcePath}`} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-sci-observational hover:underline">
                Open pinned response artifact <ExternalLink size={12} />
              </a>}
              {selectedArchive === "cohort_029" && inspected.target != null && (
                <div>
                  <button type="button" disabled={pair?.state === "loading"} onClick={() => {
                    if (pair?.state === "loaded") setPairState(null);
                    else void compareTargetPair(inspected);
                  }} className="rounded border border-obs-border bg-obs-elevated px-2 py-1.5 hover:border-sci-causal">
                    {pair?.state === "loaded" ? "Hide matched target" : "Compare matched target"}
                  </button>
                  {pair?.state === "loading" && <p role="status" className="mt-1 text-obs-secondary">Finding the matching decision in the frozen archive…</p>}
                  {pair?.state === "unavailable" && <p role="status" className="mt-1 text-sci-caution">The matching archived response is unavailable.</p>}
                  {pair?.row && (
                    <div className="mt-2 grid gap-2 sm:grid-cols-2">
                      {[inspected, pair.row].sort((a, b) => (a.target ?? 0) - (b.target ?? 0)).map((member) => (
                        <div className="min-w-0 space-y-1 rounded border border-obs-border bg-obs-bg p-2" key={member.task_id}>
                          <h3 className="font-semibold">Target {member.target}</h3>
                          <p>Oracle {member.gold_action ?? "unavailable"} · Parsed {member.predicted_action ?? "unavailable"}</p>
                          <pre className="whitespace-pre-wrap break-words font-mono">{member.raw_response ?? "(No recorded model output)"}</pre>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
              <div>
                <div className="font-mono text-[10px] uppercase text-obs-muted">
                  Verbatim Raw Model Output (Untrusted Plain Text)
                </div>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded border border-obs-border bg-obs-bg p-3 font-mono text-xs text-obs-text">
                  {inspected.raw_response || "(No recorded model output)"}
                </pre>
                {inspected.error && <p className="mt-1 whitespace-pre-wrap text-sci-caution">{inspected.error}</p>}
              </div>

              {inspected.system_prompt && <details>
                <summary className="cursor-pointer font-mono text-[10px] uppercase text-obs-muted">Exact system prompt</summary>
                <pre className="mt-1 whitespace-pre-wrap rounded border border-obs-border bg-obs-bg p-3 font-mono text-[11px]">{inspected.system_prompt}</pre>
              </details>}
              {inspected.user_prompt && (
                <div>
                  <div className="font-mono text-[10px] uppercase text-obs-muted">
                    Exact User Prompt
                  </div>
                  <pre className="mt-1 max-h-64 overflow-y-auto whitespace-pre-wrap rounded border border-obs-border bg-obs-bg p-3 font-mono text-[11px] leading-relaxed text-obs-secondary">
                    {inspected.user_prompt}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="py-20 text-center text-xs text-obs-muted">
              Select a response row to inspect its verbatim prompt and raw completion.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
