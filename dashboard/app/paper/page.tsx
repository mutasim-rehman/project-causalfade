import Link from "next/link";
import { ExternalLink, FileText } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { getFinalStudy } from "@/lib/data/final-study";

export default function PaperPage() {
  const { commit } = getFinalStudy();
  const source = `https://github.com/mutasim-rehman/project-causalfade/blob/${commit}`;
  const documents = [
    {
      title: "Evaluating Target-Population Intervention Decisions in Language Models With Matched Switch and Invariance Tests",
      path: "manuscript/ieee-tnnls.pdf",
      description: "Repository review draft. Covers the CF-TP1 instrument, paired primary endpoint and transfer-form case study.",
    },
    {
      title: "Supplementary materials",
      path: "manuscript/supplement.pdf",
      description: "Mathematical details, cohort history, reproduction procedures and the release reporting correction.",
    },
    {
      title: "The Life of CausalFade",
      path: "docs/scientific-retrospective/build/The_Life_of_CausalFade.pdf",
      description: "The project's scientific retrospective, covering the path from early quantization studies to CF-TP1.",
    },
  ];

  return (
    <div className="space-y-5">
      <PageHeader
        eyebrow="Publication"
        title="Research Paper"
        subtitle="Read the manuscript draft and its supporting documents at the same repository revision used by the observatory."
      />
      <ul className="grid gap-3">
        {documents.map((doc) => (
          <li key={doc.path} className="flex items-start gap-4 rounded border border-obs-border bg-obs-surface p-5">
            <FileText aria-hidden="true" className="mt-1 shrink-0 text-sci-causal" size={21} />
            <div>
              <h2 className="font-serif text-xl">{doc.title}</h2>
              <p className="mt-1 text-sm text-obs-secondary">{doc.description}</p>
              <a href={`${source}/${doc.path}`} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-2 text-sm text-sci-observational hover:underline">
                Open {doc.path.endsWith("ieee-tnnls.pdf") ? "manuscript" : doc.path.endsWith("supplement.pdf") ? "supplement" : "retrospective"} PDF on GitHub
                <ExternalLink size={14} aria-hidden="true" />
              </a>
            </div>
          </li>
        ))}
      </ul>
      <Link href="/findings/" className="inline-block text-sm text-sci-causal hover:underline">Read the final findings</Link>
    </div>
  );
}
