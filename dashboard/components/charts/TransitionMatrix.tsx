"use client";

import { useEffect, useMemo, useState } from "react";
import { z } from "zod";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import { loadDataset } from "@/lib/data/loader";
import { ProvenanceSchema } from "@/lib/schemas/observatory";

const action = z.union([z.literal(0), z.literal(1)]);
const transitionDataset = z.object({
  provenance: ProvenanceSchema,
  rows: z.array(z.object({
    family: z.number().int(),
    form: z.enum(["transfer", "archive_compatible"]),
    task: z.enum(["causal", "arithmetic"]),
    order: z.enum(["L_first", "R_first"]),
    role: z.enum(["L_governs", "R_governs"]),
    expected: z.tuple([action, action]),
    observed: z.tuple([action.nullable(), action.nullable()]),
  })),
});

const labels = ["OFF → OFF", "OFF → ON", "ON → OFF", "ON → ON", "Unavailable"];

function transitionIndex(actions: [number | null, number | null]) {
  const [initial, final] = actions;
  return initial === null || final === null ? 4 : initial * 2 + final;
}

export function TransitionMatrix() {
  const [data, setData] = useState<z.infer<typeof transitionDataset> | null>(null);
  const [failed, setFailed] = useState(false);
  const [form, setForm] = useState("transfer");
  const [family, setFamily] = useState("");
  const [order, setOrder] = useState("");
  const [role, setRole] = useState("");
  const [expected, setExpected] = useState("");
  const [observed, setObserved] = useState("");

  useEffect(() => {
    loadDataset("/data/target_transitions.json", transitionDataset).then(setData).catch(() => setFailed(true));
  }, []);

  const families = useMemo(() => Array.from(new Set(data?.rows.map((row) => row.family))).sort((a, b) => a - b), [data]);
  const matrices = useMemo(() => {
    const result = {
      causal: { total: 0, cells: Array.from({ length: 4 }, () => [0, 0, 0, 0, 0]) },
      arithmetic: { total: 0, cells: Array.from({ length: 4 }, () => [0, 0, 0, 0, 0]) },
    };
    for (const row of data?.rows ?? []) {
      if (row.form !== form || (family && row.family !== Number(family)) || (order && row.order !== order) || (role && row.role !== role)) continue;
      const oracle = transitionIndex(row.expected);
      const prediction = transitionIndex(row.observed);
      if ((expected && oracle !== Number(expected)) || (observed && prediction !== Number(observed))) continue;
      result[row.task].total++;
      result[row.task].cells[oracle][prediction]++;
    }
    return result;
  }, [data, expected, family, form, observed, order, role]);

  const filters: { label: string; value: string; set: (value: string) => void; options: [string, string][] }[] = [
    { label: "Prompt form", value: form, set: setForm, options: [["transfer", "Transfer"], ["archive_compatible", "Archive compatible"]] },
    { label: "Numerical family", value: family, set: setFamily, options: [["", "All families"], ...families.map((slot): [string, string] => [String(slot), `Family ${String(slot).padStart(3, "0")}`])] },
    { label: "Evidence order", value: order, set: setOrder, options: [["", "Both orders"], ["L_first", "L first"], ["R_first", "R first"]] },
    { label: "Governing table", value: role, set: setRole, options: [["", "Both tables"], ["L_governs", "L governs"], ["R_governs", "R governs"]] },
    { label: "Expected transition", value: expected, set: setExpected, options: [["", "All expected"], ...labels.slice(0, 4).map((label, i): [string, string] => [String(i), label])] },
    { label: "Observed transition", value: observed, set: setObserved, options: [["", "All observed"], ...labels.map((label, i): [string, string] => [String(i), label])] },
  ];

  return (
    <section className="space-y-4 rounded border border-obs-border bg-obs-surface p-4 sm:p-5">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold">Target decision transitions</h2>
          <p className="mt-1 text-xs leading-relaxed text-obs-secondary">Each pair follows the same family from target 0 to target 1. Rows show the oracle transition and columns show the model transition. Filters change these descriptive counts only.</p>
        </div>
        {data && <EvidenceButton meta={data.provenance} title="Frozen target pairs" />}
      </div>
      {failed && <p role="alert">The frozen transition records are unavailable.</p>}
      {!data && !failed && <p role="status">Loading target pairs…</p>}
      {data && <>
        <div className="grid grid-cols-2 gap-2 md:grid-cols-3 xl:grid-cols-6">
          {filters.map(({ label, value, set, options }) => (
            <label key={label} className="min-w-0 text-xs text-obs-secondary">
              {label}
              <select value={value} onChange={(event) => set(event.target.value)} className="mt-1 w-full rounded border border-obs-border bg-obs-elevated p-1.5 text-obs-text">
                {options.map(([key, text]) => <option key={key} value={key}>{text}</option>)}
              </select>
            </label>
          ))}
        </div>
        <div className="grid gap-3 xl:grid-cols-2" aria-live="polite">
          {(["causal", "arithmetic"] as const).map((task) => {
            const { cells, total } = matrices[task];
            return (
              <div key={task} className="min-w-0 overflow-x-auto rounded border border-obs-border">
                <table className="w-full text-left font-mono text-[11px] tabular-nums">
                  <caption className={`bg-obs-elevated p-2 text-left font-sans text-sm font-semibold ${task === "causal" ? "text-sci-causal" : "text-sci-arithmetic"}`}>
                    {task === "causal" ? "Causal" : "Arithmetic control"} · {total ? `${total} pairs` : "No matching pairs"}
                  </caption>
                  <thead>
                    <tr className="text-obs-muted">
                      <th scope="col" className="p-2">Expected ↓ / Observed →</th>
                      {labels.map((label) => <th scope="col" className="whitespace-nowrap p-2" key={label}>{label}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {cells.map((row, oracle) => (
                      <tr key={labels[oracle]} className="border-t border-obs-border">
                        <th scope="row" className="whitespace-nowrap p-2 font-medium">{labels[oracle]}</th>
                        {row.map((count, prediction) => <td key={labels[prediction]} className={`p-2 ${oracle === prediction && count ? "bg-sci-verified/10 text-sci-verified" : "text-obs-secondary"}`}>{total ? count : "—"}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          })}
        </div>
        <a className="inline-block text-xs text-sci-observational hover:underline" href="/data/target_transitions.json" download>Download normalized target pairs (JSON)</a>
      </>}
    </section>
  );
}
