import React from "react";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import type { ProvenanceMeta } from "@/lib/schemas/observatory";

export function PageHeader({
  eyebrow,
  title,
  subtitle,
  provenance,
  children,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  provenance?: ProvenanceMeta;
  children?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 border-b border-obs-border pb-5 sm:flex-row sm:items-end sm:justify-between">
      <div className="max-w-3xl">
        <div className="font-mono text-[11px] font-semibold uppercase tracking-widest text-sci-causal">
          {eyebrow}
        </div>
        <h1 className="mt-1 font-serif text-2xl font-medium tracking-tight text-obs-text sm:text-3xl">
          {title}
        </h1>
        <p className="mt-1.5 text-sm leading-relaxed text-obs-secondary">
          {subtitle}
        </p>
      </div>
      <div className="flex shrink-0 flex-wrap items-center gap-2">
        {provenance && <EvidenceButton meta={provenance} title={title} />}
        {children}
      </div>
    </div>
  );
}
