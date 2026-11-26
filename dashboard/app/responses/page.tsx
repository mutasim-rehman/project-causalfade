"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { Download, Search, AlertTriangle } from "lucide-react";
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
  valid?: boolean;
  correct?: boolean;
  raw_response: string;
  user_prompt?: string;
  system_prompt?: string;
  arm?: string;
  family_id?: string;
  condition?: string;
  order?: string;
  status?: string;
  error?: string | null;
}

export default function ResponsesPage() {
  const [archives, setArchives] = useState<ArchiveEntry[]>([]);
  const [selectedArchive, setSelectedArchive] = useState("cohort_029");
  const [selectedChunkIdx, setSelectedChunkIdx] = useState(0);
  const [rows, setRows] = useState<RawRow[]>([]);
  const [loading, setLoading] = useState(false);

  const [search, setSearch] = useState("");
  const [taskFilter, setTaskFilter] = useState("ALL");
  const [correctFilter, setCorrectFilter] = useState("ALL");
  const [activeRow, setActiveRow] = useState<RawRow | null>(null);

  const parentRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    loadDataset<{ archives: ArchiveEntry[] }>("/data/responses/index.json").then((d) => {
      setArchives(d.archives);
    });
  }, []);

  const currentArchive = useMemo(
    () => archives.find((a) => a.id === selectedArchive),
    [archives, selectedArchive]
  );

  useEffect(() => {
    if (!currentArchive) return;
    const chunkPath = currentArchive.chunks[selectedChunkIdx] ?? currentArchive.chunks[0];
    if (!chunkPath) return;
    setLoading(true);
    loadDataset<RawRow[]>(chunkPath)
      .then((d) => {
        setRows(d);
        setActiveRow(d[0] ?? null);
      })
      .finally(() => setLoading(false));
  }, [currentArchive, selectedChunkIdx]);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    return rows.filter((r) => {
      if (taskFilter !== "ALL" && r.task_label !== taskFilter) return false;
      if (correctFilter === "CORRECT" && !r.correct) return false;
      if (correctFilter === "INCORRECT" && r.correct) return false;
      if (q) {
        const hay = `${r.task_id} ${r.slot ?? ""} ${r.family_id ?? ""} ${r.raw_response}`.toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }, [rows, taskFilter, correctFilter, search]);

  const rowVirtualizer = useVirtualizer({
    count: filtered.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 40,
    overscan: 12,
  });

  const exportCsv = () => {
    const header = ["task_id", "slot", "task_label", "form_label", "gold_action", "predicted_action", "correct", "raw_response"];
    const lines = [
      header.join(","),
      ...filtered.slice(0, 1000).map((r) =>
        [
          r.task_id,
          r.slot ?? "",
          r.task_label ?? "",
          r.form_label ?? "",
          r.gold_action ?? "",
          r.predicted_action ?? "",
          r.correct ?? "",
          `"${(r.raw_response ?? "").replace(/"/g, '""')}"`,
        ].join(",")
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
          className="inline-flex items-center gap-1.5 rounded border border-obs-border bg-obs-elevated px-3 py-1.5 text-xs font-medium text-obs-text hover:border-sci-causal"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export CSV</span>
        </button>
      </PageHeader>

      {/* Archive & Filter Controls */}
      <div className="grid grid-cols-1 gap-3 rounded border border-obs-border bg-obs-surface p-4 md:grid-cols-12">
        <div className="md:col-span-4">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Archive</label>
          <select
            value={selectedArchive}
            onChange={(e) => {
              setSelectedArchive(e.target.value);
              setSelectedChunkIdx(0);
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
            value={correctFilter}
            onChange={(e) => setCorrectFilter(e.target.value)}
            className="mt-1 w-full rounded border border-obs-border bg-obs-elevated px-2.5 py-1.5 font-mono text-xs text-obs-text"
          >
            <option value="ALL">All Outcomes</option>
            <option value="CORRECT">Correct Only</option>
            <option value="INCORRECT">Incorrect Only</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block font-mono text-[10px] uppercase text-obs-muted">Search</label>
          <div className="relative mt-1">
            <Search className="absolute left-2.5 top-2 h-3.5 w-3.5 text-obs-muted" />
            <input
              type="text"
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
        <div className="rounded border border-obs-border bg-obs-surface lg:col-span-6">
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
                    onClick={() => setActiveRow(r)}
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
                        r.correct
                          ? "bg-sci-verified/15 text-sci-verified"
                          : "bg-sci-error/15 text-sci-error"
                      }`}
                    >
                      {r.correct ? "PASS" : "FAIL"}
                    </span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Detail Inspector */}
        <div className="rounded border border-obs-border bg-obs-surface p-4 lg:col-span-6">
          {activeRow ? (
            <div className="space-y-4 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2 border-b border-obs-border pb-2.5">
                <span className="font-mono font-semibold text-sci-causal">
                  task_id: {activeRow.task_id}
                </span>
                <div className="flex gap-1.5 font-mono text-[11px]">
                  {activeRow.form_label && (
                    <span className="rounded bg-obs-elevated px-2 py-0.5">{activeRow.form_label}</span>
                  )}
                  {activeRow.role_label && (
                    <span className="rounded bg-obs-elevated px-2 py-0.5">{activeRow.role_label}</span>
                  )}
                </div>
              </div>

              <div>
                <div className="font-mono text-[10px] uppercase text-obs-muted">
                  Verbatim Raw Model Output (Untrusted Plain Text)
                </div>
                <pre className="mt-1 overflow-x-auto whitespace-pre-wrap rounded border border-obs-border bg-obs-bg p-3 font-mono text-xs text-obs-text">
                  {activeRow.raw_response || activeRow.error || "(empty)"}
                </pre>
              </div>

              {activeRow.user_prompt && (
                <div>
                  <div className="font-mono text-[10px] uppercase text-obs-muted">
                    Exact User Prompt
                  </div>
                  <pre className="mt-1 max-h-64 overflow-y-auto whitespace-pre-wrap rounded border border-obs-border bg-obs-bg p-3 font-mono text-[11px] leading-relaxed text-obs-secondary">
                    {activeRow.user_prompt}
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
