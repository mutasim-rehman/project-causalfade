import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { PageHeader } from "@/components/ui/PageHeader";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import { getFinalStudy } from "@/lib/data/final-study";

export default function FindingsPage() {
  const study = getFinalStudy();

  return (
    <article className="space-y-6">
      <PageHeader
        eyebrow="Publication · Cohort 029"
        title="Final Findings"
        subtitle="The CF-TP1 case study examined whether a single Qwen2.5-7B-Instruct Q4_K_M deployment could choose the correct intervention across changes in target population and evidence provenance."
        provenance={study.provenance}
      />

      <section aria-labelledby="protocol" className="rounded border border-obs-border bg-obs-surface p-5">
        <h2 id="protocol" className="font-serif text-2xl">The final protocol</h2>
        <p className="mt-2 max-w-3xl text-sm leading-relaxed text-obs-secondary">
          Each of the {study.families} independent numerical families admitted two assignments of randomized and historical evidence. The matched arithmetic task named the governing table and specified the calculation. A target pair earned credit when both decisions matched the oracle, including the direction of any required switch.
        </p>
        <Link className="mt-3 inline-block text-sm text-sci-causal hover:underline" href="/experimental-design/">Explore the experimental design</Link>
      </section>

      <section aria-labelledby="established" className="space-y-3">
        <h2 id="established" className="font-serif text-2xl">What we established</h2>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {[
            { label: "Correct causal reversals", value: study.reversals, scope: "Pairs that required a change in action", evidence: study.reversalEvidence },
            { label: "Causal activation", value: study.activation, scope: "Individual causal decisions on the transfer form" },
            { label: "Causal pair fidelity", value: study.causalPairs, scope: "Both decisions correct on the transfer form" },
            { label: "Arithmetic pair fidelity", value: study.arithmeticPairs, scope: "Both decisions correct on the matched control" },
          ].map(({ label, value, scope, evidence }) => (
            <div key={label} className="rounded border border-obs-border bg-obs-surface p-4">
              <h3 className="text-sm font-medium">{label}</h3>
              <p className="mt-2 font-mono text-2xl tabular-nums text-sci-causal">{value}</p>
              <p className="mt-1 text-xs text-obs-secondary">{scope}</p>
              {evidence && <EvidenceButton className="mt-3" meta={evidence} title={label} />}
            </div>
          ))}
        </div>
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded border border-sci-caution/40 bg-obs-surface p-5">
          <h2 className="font-serif text-2xl">What remains unresolved</h2>
          <p className="mt-2 text-sm leading-relaxed text-obs-secondary">
            The family-standardized causal-minus-arithmetic contrast was {study.contrast}. The approximate 95% interval was {study.interval} and the bounded interval was {study.boundedInterval}. The comparison leaves causal-specific impairment and equivalence unresolved. Quantization effects remain unidentified in this case study, which used one precision configuration.
          </p>
        </section>
        <section className="rounded border border-obs-border bg-obs-surface p-5">
          <h2 className="font-serif text-2xl">Questions for future research</h2>
          <p className="mt-2 text-sm leading-relaxed text-obs-secondary">
            Do the directional error patterns recur across checkpoints, precision levels and prompt forms? Can a controlled precision comparison distinguish general task degradation from an effect specific to causal evidence selection?
          </p>
        </section>
      </div>

      <nav aria-label="Related analysis" className="flex flex-wrap gap-x-6 gap-y-3">
        {[["/statistics/", "Inspect the statistics"], ["/decisions/", "Explore decision behavior"], ["/paper/", "Read the research paper"]].map(([href, label]) => (
          <Link key={href} href={href} className="inline-flex items-center gap-2 text-sm text-sci-causal hover:underline">
            {label}<ArrowRight aria-hidden="true" size={15} />
          </Link>
        ))}
      </nav>
    </article>
  );
}
