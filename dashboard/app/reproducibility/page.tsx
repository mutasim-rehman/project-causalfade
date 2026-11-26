"use client";

import React, { useEffect, useState } from "react";
import { CheckCircle2, AlertTriangle, ExternalLink } from "lucide-react";
import { loadDataset } from "@/lib/data/loader";
import { PageHeader } from "@/components/ui/PageHeader";
import manifest from "@/DATA_MANIFEST.json";

interface ReproData {
  git_commit: string;
  release_tag: string;
  release_commit: string;
  extraction_timestamp: string;
  cohort_029_verification: {
    passed: boolean;
    checks: { name: string; passed: boolean }[];
  };
  claim_ledger: {
    location: string;
    claim: string;
    classification_or_check: string;
    tagged_path: string;
    sha256_git_blob_content: string;
  }[];
  discrepancies: {
    id: string;
    title: string;
    severity: string;
    reported: string;
    verified_ground_truth: string;
    source_path: string;
  }[];
}

export default function ReproducibilityPage() {
  const [data, setData] = useState<ReproData | null>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    loadDataset<ReproData>("/data/reproducibility.json").then(setData).catch(() => setError(true));
  }, []);

  if (error) return <p role="alert">The frozen reproducibility record is unavailable.</p>;
  if (!data) return <p role="status">Loading verification records…</p>;

  const passedCount = data.cohort_029_verification.checks.filter((c) => c.passed).length;

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Scientific Transparency & Audit Trail"
        title="Reproducibility & Evidence"
        subtitle="Cryptographic provenance, automated reconciliation checks, documented historical discrepancies, and claim-to-evidence mappings."
      />

      {/* Snapshot Summary */}
      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded border border-obs-border bg-obs-surface p-4 font-mono text-xs">
          <span className="text-obs-muted">Pinned Git Commit</span>
          <div className="mt-1 break-all text-obs-text">{data.git_commit}</div>
        </div>
        <div className="rounded border border-obs-border bg-obs-surface p-4 font-mono text-xs">
          <span className="text-obs-muted">Immutable Release Tag</span>
          <div className="mt-1 text-sci-causal">{data.release_tag}</div>
          <div className="mt-0.5 text-[11px] text-obs-muted">{data.release_commit.slice(0, 12)}…</div>
        </div>
        <div className="rounded border border-obs-border bg-obs-surface p-4 font-mono text-xs">
          <span className="text-obs-muted">Cohort 029 Release Verifier</span>
          <div className={`mt-1 flex items-center gap-1.5 text-base font-bold ${data.cohort_029_verification.passed ? "text-sci-verified" : "text-sci-caution"}`}>
            {data.cohort_029_verification.passed ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
            <span>{data.cohort_029_verification.passed ? "PASS" : "FAIL"} ({passedCount} / {data.cohort_029_verification.checks.length} checks)</span>
          </div>
        </div>
      </section>

      <section className="space-y-3 rounded border border-obs-border bg-obs-surface p-5">
        <h2 className="font-serif text-xl">Dashboard snapshot</h2>
        <div className="flex flex-wrap gap-x-5 gap-y-1 text-xs text-obs-secondary">
          <span>Extracted <time className="font-mono" dateTime={data.extraction_timestamp}>{data.extraction_timestamp}</time></span>
          <span>Dashboard reconciliation <strong className={manifest.all_verification_checks_passed ? "text-sci-verified" : "text-sci-caution"}>{manifest.all_verification_checks_passed ? "PASS" : "FAIL"}</strong></span>
        </div>
        <p className="text-sm text-obs-secondary">
          Recheck the local snapshot from the repository root with <code className="break-all text-obs-text">python dashboard/scripts/verify/verify_data.py --check-only</code>.
        </p>
        <details className="rounded border border-obs-border">
          <summary className="cursor-pointer bg-obs-elevated p-2 text-sm">Downloads and SHA-256 digests ({manifest.datasets.length} files)</summary>
          <ul className="divide-y divide-obs-border">
            {manifest.datasets.map((entry) => (
              <li className="px-3 py-2 text-xs" key={entry.path}>
                <a href={entry.path.replace(/^public/, "")} download className="break-all text-sci-observational hover:underline">{entry.path.replace(/^public\/data\//, "")}</a>
                <div className="mt-1 break-all font-mono text-[11px] text-obs-muted">{entry.sha256}</div>
              </li>
            ))}
          </ul>
        </details>
      </section>

      {/* Discrepancies */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-sci-caution">
          <AlertTriangle className="h-4 w-4" />
          <span>Documented Historical Discrepancies & Defects (Exposed, Never Silenced)</span>
        </div>
        <div className="space-y-3">
          {data.discrepancies.map((d) => (
            <div key={d.id} className="rounded border border-obs-border bg-obs-elevated/40 p-3.5 text-xs">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="font-semibold text-obs-text">
                  <span className="mr-2 font-mono text-sci-caution">{d.id}</span>
                  {d.title}
                </span>
                <span className="rounded bg-obs-surface px-2 py-0.5 font-mono text-[10px] text-obs-muted">
                  {d.severity}
                </span>
              </div>
              <p className="mt-1.5 text-obs-secondary">
                <strong>Reported / Historical:</strong> {d.reported}
              </p>
              <p className="mt-1 text-sci-verified">
                <strong>Verified Ground Truth:</strong> {d.verified_ground_truth}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Claim-to-Evidence Registry */}
      <section className="rounded border border-obs-border bg-obs-surface p-5">
        <h2 className="mb-3 text-sm font-semibold text-obs-text">
          Claim-to-Evidence Registry ({data.claim_ledger.length} entries from manuscript/audit/claim-ledger.csv)
        </h2>
        <div className="max-h-96 overflow-y-auto rounded border border-obs-border">
          <table className="w-full text-left text-xs">
            <thead className="sticky top-0 bg-obs-elevated font-mono text-[11px] uppercase text-obs-muted">
              <tr>
                <th className="px-3 py-2">Location</th>
                <th className="px-3 py-2">Claim</th>
                <th className="px-3 py-2">Tagged Artifact (SHA-256)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-obs-border/60 text-obs-secondary">
              {data.claim_ledger.map((row, idx) => (
                <tr key={idx}>
                  <td className="px-3 py-2 font-mono text-sci-causal whitespace-nowrap">{row.location}</td>
                  <td className="px-3 py-2">{row.claim}</td>
                  <td className="px-3 py-2 font-mono text-[11px]">
                    <a
                      href={`https://github.com/mutasim-rehman/project-causalfade/blob/${data.release_commit}/${row.tagged_path}`}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-sci-observational hover:underline"
                    >
                      <span className="break-all">{row.tagged_path}</span>
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <div className="text-[10px] text-obs-muted">
                      sha256:{row.sha256_git_blob_content.slice(0, 16)}…
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
