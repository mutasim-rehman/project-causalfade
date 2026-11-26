"use client";

import React from "react";
import { ReactFlow, Background, Controls, type Node, type Edge } from "@xyflow/react";
import { PageHeader } from "@/components/ui/PageHeader";

const PIPELINE_NODES: Node[] = [
  { id: "1", position: { x: 0, y: 40 }, data: { label: "1. Causal World Gen\ncausalfade/target_transport.py\n128 SCM Families (Seed 290431)" }, style: { background: "#111827", color: "#55D6BE", border: "1px solid #55D6BE", fontSize: 11, width: 200 } },
  { id: "2", position: { x: 240, y: 40 }, data: { label: "2. Evidence & Role Swap\nFeasible L/R Worlds + 2 Targets\nExact Rational m_{SUA} in (0,1)" }, style: { background: "#111827", color: "#F1F5F9", border: "1px solid #263142", fontSize: 11, width: 200 } },
  { id: "3", position: { x: 480, y: 40 }, data: { label: "3. Prompt & Assignment\n2^5 = 32 Prompts / Family\nCausal vs Arithmetic Control" }, style: { background: "#111827", color: "#A78BFA", border: "1px solid #A78BFA", fontSize: 11, width: 200 } },
  { id: "4", position: { x: 720, y: 40 }, data: { label: "4. Model Inference\nllama.cpp b12176 CPU\nTemp=0, Cap=48 tokens" }, style: { background: "#111827", color: "#60A5FA", border: "1px solid #60A5FA", fontSize: 11, width: 190 } },
  { id: "5", position: { x: 720, y: 170 }, data: { label: "5. Durable Collection\nevents.jsonl (Intent->Response)\n4,096 Base64 Envelopes" }, style: { background: "#111827", color: "#F1F5F9", border: "1px solid #263142", fontSize: 11, width: 190 } },
  { id: "6", position: { x: 480, y: 170 }, data: { label: "6. Strict JSON Parser\nExact {activate: 0|1}\n4,096 / 4,096 Valid" }, style: { background: "#111827", color: "#34D399", border: "1px solid #34D399", fontSize: 11, width: 200 } },
  { id: "7", position: { x: 240, y: 170 }, data: { label: "7. Dual-Oracle Scoring\nPrivate SCM vs Public Parser\nPair Fidelity F_pair = I_0 * I_1" }, style: { background: "#111827", color: "#55D6BE", border: "1px solid #55D6BE", fontSize: 11, width: 200 } },
  { id: "8", position: { x: 0, y: 170 }, data: { label: "8. Stratified Inference\n8 Strata Welch t CI +\nHoeffding Bounded CI" }, style: { background: "#162231", color: "#FBBF24", border: "1px solid #FBBF24", fontSize: 11, width: 200 } },
];

const PIPELINE_EDGES: Edge[] = [
  { id: "p1", source: "1", target: "2", animated: true, style: { stroke: "#55D6BE" } },
  { id: "p2", source: "2", target: "3", animated: true, style: { stroke: "#55D6BE" } },
  { id: "p3", source: "3", target: "4", animated: true, style: { stroke: "#A78BFA" } },
  { id: "p4", source: "4", target: "5", animated: true, style: { stroke: "#60A5FA" } },
  { id: "p5", source: "5", target: "6", animated: true, style: { stroke: "#34D399" } },
  { id: "p6", source: "6", target: "7", animated: true, style: { stroke: "#34D399" } },
  { id: "p7", source: "7", target: "8", animated: true, style: { stroke: "#FBBF24" } },
];

export default function ExperimentalDesignPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Protocol Architecture & Factorial Structure"
        title="Experimental Design (CF-TP1)"
        subtitle="How CausalFade constructs exact-rational causal worlds, crosses provenance and target-population mixtures, enforces matched arithmetic controls, and prevents shortcut solutions."
      />

      {/* Pipeline Diagram */}
      <section className="rounded border border-obs-border bg-obs-surface p-4">
        <h2 className="mb-2 text-sm font-semibold text-obs-text">
          Verified CF-TP1 Execution & Verification Pipeline
        </h2>
        <div className="h-72 w-full rounded border border-obs-border bg-obs-bg">
          <ReactFlow nodes={PIPELINE_NODES} edges={PIPELINE_EDGES} fitView>
            <Background color="#1E293B" gap={20} />
            <Controls />
          </ReactFlow>
        </div>
      </section>

      {/* Design Table (Table 1 of Manuscript) */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <h2 className="mb-3 text-sm font-semibold text-obs-text">
          CF-TP1 Factorial Design Factors (128 Independent Numerical Families × 32 Prompts = 4,096 Calls)
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-obs-border font-mono text-[11px] uppercase text-obs-muted">
                <th className="py-2 pr-4">Factor</th>
                <th className="py-2">Levels, Counterbalancing, and Scientific Purpose</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Family Sample (Unit)</td>
                <td className="py-2.5">128 independent numerical draws across 8 equal sign strata (p, g, b) ∈ {'{0,1}×{0,1}×{-1,+1}'} (16 families/stratum). Only families are independent sampling units.</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Form</td>
                <td className="py-2.5">Archive-compatible (Form 0) vs. Transfer wording (Form 1, primary). Both frozen and interleaved.</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Task</td>
                <td className="py-2.5">Causal study interpretation (Task 0) vs. Matched explicit-scorecard weighted arithmetic (Task 1). Identical numbers, target weights, answer options, and parser.</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Physical Source Order</td>
                <td className="py-2.5">Table L displayed first vs. Table R displayed first. Crossed within family; evaluator keys remain fixed.</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Governing Role</td>
                <td className="py-2.5">Table L supplies randomized rates vs. Table R supplies randomized rates (or designated scorecard). Both worlds are exact-rational feasible under latent risk U.</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Target Mixture</td>
                <td className="py-2.5">Two stratum-1 shares w₀ ∈ [54, 62]%, w₁ ∈ [76, 84]%. Depending on stratum p, the target change either requires a decision reversal (p=1) or invariance (p=0).</td>
              </tr>
              <tr>
                <td className="py-2.5 pr-4 font-mono font-semibold text-obs-text">Administration Bits</td>
                <td className="py-2.5">Public source names (A/B), stratum names (Amber/Blue), answer-alternative order (0/1 first), and within-table stratum order balanced across slots within each stratum.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* Planned vs Executed */}
      <section className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div className="rounded border border-obs-border bg-obs-surface p-4">
          <h3 className="font-mono text-xs font-semibold uppercase text-sci-verified">
            Executed & Verified Protections
          </h3>
          <ul className="mt-2 space-y-1.5 text-xs text-obs-secondary">
            <li>• Dual-oracle verification: private SCM enumerator vs. independent public-text parser (0/4,096 mismatches).</li>
            <li>• Rival shortcut gate: constant-rivals-v1 verified 0/128 families solved by source-blind or target-blind heuristics.</li>
            <li>• Strict bare-JSON parser with 48-token cap: 4,096/4,096 normal stop and valid JSON.</li>
          </ul>
        </div>
        <div className="rounded border border-obs-border bg-obs-surface p-4">
          <h3 className="font-mono text-xs font-semibold uppercase text-sci-caution">
            Planned vs. Actual Provenance Limits
          </h3>
          <ul className="mt-2 space-y-1.5 text-xs text-obs-secondary">
            <li>• CF-TP1 v1.0 specified pre-inference human authorship & blind review; production freeze recorded both as undocumented (signed records reconciled post-freeze).</li>
            <li>• Single quantized deployment (Qwen2.5-7B Q4_K_M); F16 reference arm was not part of Cohort 029.</li>
          </ul>
        </div>
      </section>
    </div>
  );
}
