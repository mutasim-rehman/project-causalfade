"use client";

import React, { useEffect, useMemo, useState } from "react";
import { ReactFlow, Background, Controls, type Node, type Edge } from "@xyflow/react";
import { ChevronDown, ChevronRight, GitCommit, AlertCircle } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";

interface TimelineEvent {
  event_id: string;
  timestamp: string;
  commit: string;
  phase: string;
  investigating: string;
  understood_at_time: string;
  available_evidence: string;
  decision_made: string;
  documented_rationale: string;
  subsequent_impact: string;
  retrospective_assessment: string;
}

const GENEALOGY_NODES: Node[] = [
  { id: "T01", position: { x: 0, y: 80 }, data: { label: "T01 · Literature & H01\n(Quantization vs Confounding)" }, style: { background: "#111827", color: "#F1F5F9", border: "1px solid #55D6BE", fontSize: 11, width: 190 } },
  { id: "T02", position: { x: 230, y: 80 }, data: { label: "T02 · SCM + C/A/B\n(Synthetic Validation)" }, style: { background: "#111827", color: "#F1F5F9", border: "1px solid #263142", fontSize: 11, width: 175 } },
  { id: "T04", position: { x: 440, y: 10 }, data: { label: "001–004 · 3B/7B Pilots\n(Fences, Q2_K Cap, Bias)" }, style: { background: "#111827", color: "#F87171", border: "1px solid #F87171", fontSize: 11, width: 185 } },
  { id: "T05", position: { x: 440, y: 150 }, data: { label: "002,005–007 · Controls\n(Sign vs Action Split)" }, style: { background: "#111827", color: "#A78BFA", border: "1px solid #A78BFA", fontSize: 11, width: 185 } },
  { id: "T08", position: { x: 670, y: 80 }, data: { label: "008–016 · Order Effect\n(+62.5 pp Q4 Confirmed)" }, style: { background: "#111827", color: "#60A5FA", border: "1px solid #60A5FA", fontSize: 11, width: 185 } },
  { id: "T10", position: { x: 900, y: 10 }, data: { label: "018–024 · Controls & 3x7\n(Source ID 100%, Controls Fail)" }, style: { background: "#111827", color: "#FBBF24", border: "1px solid #FBBF24", fontSize: 11, width: 195 } },
  { id: "T11", position: { x: 900, y: 150 }, data: { label: "025 / 025.1 · Archive Audit\n(016 Magnitude Shortcut Found)" }, style: { background: "#111827", color: "#FBBF24", border: "1px solid #FBBF24", fontSize: 11, width: 195 } },
  { id: "T12", position: { x: 1140, y: 80 }, data: { label: "026–028 · Graph-Switch\n(0/8 Fidelity; Calc C Fails)" }, style: { background: "#111827", color: "#F87171", border: "1px solid #F87171", fontSize: 11, width: 185 } },
  { id: "T14", position: { x: 1370, y: 80 }, data: { label: "029 · CF-TP1 Final\n(Feasible Role Swap + Target)" }, style: { background: "#162231", color: "#55D6BE", border: "2px solid #55D6BE", fontSize: 11, width: 190 } },
];

const GENEALOGY_EDGES: Edge[] = [
  { id: "e1", source: "T01", target: "T02", animated: true, style: { stroke: "#55D6BE" } },
  { id: "e2", source: "T02", target: "T04", style: { stroke: "#64748B" } },
  { id: "e3", source: "T02", target: "T05", style: { stroke: "#A78BFA" } },
  { id: "e4", source: "T04", target: "T08", style: { stroke: "#60A5FA" } },
  { id: "e5", source: "T05", target: "T08", style: { stroke: "#60A5FA" } },
  { id: "e6", source: "T08", target: "T10", style: { stroke: "#FBBF24" } },
  { id: "e7", source: "T08", target: "T11", style: { stroke: "#FBBF24" } },
  { id: "e8", source: "T10", target: "T12", style: { stroke: "#F87171" } },
  { id: "e9", source: "T11", target: "T12", style: { stroke: "#F87171" } },
  { id: "e10", source: "T12", target: "T14", animated: true, style: { stroke: "#55D6BE" } },
  { id: "e11", source: "T11", target: "T14", style: { stroke: "#55D6BE", strokeDasharray: "4 4" } },
];

export default function JourneyPage() {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [phaseFilter, setPhaseFilter] = useState<string>("ALL");
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadDataset<{ events: TimelineEvent[] }>("/data/timeline.json").then((d) => {
      setEvents(d.events);
      if (d.events.length > 0) {
        setExpanded({ [d.events[0].event_id]: true, [d.events[d.events.length - 1].event_id]: true });
      }
    });
  }, []);

  const phases = useMemo(
    () => ["ALL", ...Array.from(new Set(events.map((e) => e.phase)))],
    [events]
  );

  const filtered = useMemo(
    () => (phaseFilter === "ALL" ? events : events.filter((e) => e.phase === phaseFilter)),
    [events, phaseFilter]
  );

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Research Chronology & Genealogy"
        title="Research Journey"
        subtitle="How CausalFade evolved from an initial quantization-vs-confounding hypothesis through 29 empirical cohorts, failed gates, shortcut discoveries, and retrospective audits to the CF-TP1 evaluation framework."
      />

      {/* Documented Genealogy Graph */}
      <section className="rounded border border-obs-border bg-obs-surface p-4">
        <div className="mb-2 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-obs-text">
              Documented Scientific Dependency Genealogy
            </h2>
            <p className="text-xs text-obs-secondary">
              Edges reflect documented methodological dependencies from DECISIONS.md and retrospective audits—not invented links.
            </p>
          </div>
        </div>
        <div className="h-64 w-full rounded border border-obs-border bg-obs-bg">
          <ReactFlow nodes={GENEALOGY_NODES} edges={GENEALOGY_EDGES} fitView>
            <Background color="#1E293B" gap={20} />
            <Controls />
          </ReactFlow>
        </div>
      </section>

      {/* Phase Filters */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs uppercase text-obs-muted">Filter Phase:</span>
        {phases.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPhaseFilter(p)}
            className={`rounded border px-2.5 py-1 text-xs transition-colors ${
              phaseFilter === p
                ? "border-sci-causal bg-sci-causal/15 text-sci-causal"
                : "border-obs-border bg-obs-surface text-obs-secondary hover:text-obs-text"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      {/* Chronological Timeline */}
      <div className="space-y-3">
        {filtered.map((ev) => {
          const isOpen = !!expanded[ev.event_id];
          return (
            <div
              key={ev.event_id}
              className="rounded border border-obs-border bg-obs-surface"
            >
              <button
                type="button"
                onClick={() => setExpanded((prev) => ({ ...prev, [ev.event_id]: !isOpen }))}
                className="flex w-full items-start justify-between gap-4 p-4 text-left hover:bg-obs-elevated/40"
              >
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded bg-sci-causal/15 px-2 py-0.5 font-mono text-xs font-semibold text-sci-causal">
                      {ev.event_id}
                    </span>
                    <span className="font-mono text-xs text-obs-muted">{ev.timestamp}</span>
                    <span className="inline-flex items-center gap-1 rounded bg-obs-elevated px-2 py-0.5 font-mono text-[11px] text-obs-secondary">
                      <GitCommit className="h-3 w-3" />
                      {ev.commit}
                    </span>
                  </div>
                  <h3 className="text-sm font-semibold text-obs-text">{ev.phase}</h3>
                  <p className="text-xs text-obs-secondary">{ev.investigating}</p>
                </div>
                {isOpen ? (
                  <ChevronDown className="mt-1 h-4 w-4 shrink-0 text-obs-muted" />
                ) : (
                  <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-obs-muted" />
                )}
              </button>

              {isOpen && (
                <div className="grid grid-cols-1 gap-4 border-t border-obs-border bg-obs-elevated/30 p-4 text-xs md:grid-cols-2">
                  <div>
                    <div className="font-mono text-[11px] uppercase text-obs-muted">
                      Understood at the Time
                    </div>
                    <p className="mt-1 leading-relaxed text-obs-secondary">
                      {ev.understood_at_time}
                    </p>
                  </div>
                  <div>
                    <div className="font-mono text-[11px] uppercase text-obs-muted">
                      Available Evidence
                    </div>
                    <p className="mt-1 leading-relaxed text-obs-secondary">
                      {ev.available_evidence}
                    </p>
                  </div>
                  <div>
                    <div className="font-mono text-[11px] uppercase text-obs-muted">
                      Decision Made & Rationale
                    </div>
                    <p className="mt-1 font-medium text-obs-text">{ev.decision_made}</p>
                    <p className="mt-1 leading-relaxed text-obs-secondary">
                      {ev.documented_rationale}
                    </p>
                  </div>
                  <div className="space-y-2">
                    <div>
                      <div className="font-mono text-[11px] uppercase text-obs-muted">
                        Subsequent Impact
                      </div>
                      <p className="mt-1 leading-relaxed text-obs-secondary">
                        {ev.subsequent_impact}
                      </p>
                    </div>
                    <div className="rounded border border-sci-caution/30 bg-sci-caution/10 p-2.5">
                      <div className="flex items-center gap-1 font-mono text-[11px] font-semibold text-sci-caution">
                        <AlertCircle className="h-3.5 w-3.5" />
                        <span>Retrospective Assessment</span>
                      </div>
                      <p className="mt-1 leading-relaxed text-obs-secondary">
                        {ev.retrospective_assessment}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
