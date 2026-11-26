"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { ArrowLeft, ArrowRight, Maximize, Minimize, X } from "lucide-react";
import { EvidenceButton } from "@/components/evidence/EvidenceDrawer";
import type { getFinalStudy } from "@/lib/data/final-study";

const CausalLab = dynamic(() => import("@/components/causal/CausalLab"), {
  loading: () => <p role="status">Opening the causal lab…</p>,
});

const control = "inline-flex items-center justify-center gap-2 rounded border border-obs-border bg-obs-surface px-3 py-2 text-sm hover:border-sci-causal disabled:opacity-40";

export function ResearchPresentation({ study }: { study: ReturnType<typeof getFinalStudy> }) {
  const [index, setIndex] = useState(0);
  const [labOpen, setLabOpen] = useState(false);
  const [notesOpen, setNotesOpen] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const [fullscreenError, setFullscreenError] = useState(false);
  const slides = [
    { title: "When evidence changes, does the model change its mind?", text: "CausalFade studies how language models choose interventions when the evidence or the target population changes.", note: "Ask the audience what would count as evidence that a model actually used the randomized study." },
    { title: "Historical and randomized evidence answer different questions", text: "In the historical study, unmeasured risk influences both treatment assignment and outcome. Random assignment removes that dependence from treatment assignment.", note: "Explain why comparing observed on and off groups can yield a misleading treatment contrast.", lab: true },
    { title: "Follow the causal graph", text: "Switch between historical assignment and a randomized trial. Watch the incoming edge from risk to treatment disappear while risk still affects the outcome.", note: "Use the regime controls to trace the historical backdoor path from treatment through risk to outcome.", lab: true },
    { title: "A different population can require a different action", text: "Changing the mixture of two strata can move the weighted effect through zero while keeping both stratum-specific effects fixed.", note: "Move between the two frozen target weights, then explore an intermediate value labeled illustrative.", lab: true },
    { title: "How CF-TP1 isolates the decision", text: `The study crossed evidence roles and target mixtures across ${study.families} independent numerical families. The matched control names the governing table and supplies the arithmetic.`, note: "Distinguish an independent family from the multiple prompts that reuse that family's numbers." },
    { title: "Why the research moved beyond quantization", text: "Early work asked whether quantization selectively degraded causal decisions. Subsequent studies exposed baseline competence, parsing, evidence order and response-mapping problems.", note: "Connect the change in research question to construct validity and the historical cohort archive." },
    { title: "A shortcut can pass a benchmark", text: "In the earlier order study, selecting the sign of the smaller printed gap solved the fixture without checking which evidence was randomized.", note: "Ask whether perfect accuracy in this setting identifies the reasoning strategy." },
    { title: "Score both members of a target pair", text: `Both answers were correct for ${study.causalPairs} causal pairs and ${study.arithmeticPairs} arithmetic pairs on the transfer form.`, note: "Describe the paired endpoint and explain why responses within a family are dependent.", evidence: true },
    { title: "Correct reversals were rare", text: `The model correctly reversed ${study.reversals} required causal switches. It answered ON for ${study.activation} individual causal transfer decisions.`, note: "Contrast the direction of a reversal with the frequency of any answer change.", evidence: true, reversal: true },
    { title: "The matched comparison was inconclusive", text: `The causal-minus-arithmetic contrast was ${study.contrast}, with an approximate 95% interval of ${study.interval}.`, note: "Explain why an interval spanning zero leaves both selective impairment and equivalence unresolved.", evidence: true },
    { title: "Directional scoring reveals behavior hidden by accuracy", text: "The benchmark distinguishes a correct switch, a switch in the wrong direction and an unwarranted change when the optimal action stays fixed.", note: "Ask what aggregate accuracy would miss about a model that almost always chooses the same action." },
    { title: "What remains open?", text: "The results concern one deployment and two fixed forms. A controlled comparison across precisions and checkpoints is needed to study selective degradation and generalization.", note: "Close by revisiting the first slide and separating the instrument’s contribution from claims about language models in general." },
  ];
  const count = slides.length;
  const slide = slides[index];
  const goTo = useCallback((next: number) => {
    const url = new URL(window.location.href);
    url.searchParams.set("slide", String(next + 1));
    window.history.replaceState(null, "", url);
    setIndex(next);
  }, []);

  useEffect(() => {
    const restore = () => {
      const requested = Number(new URLSearchParams(window.location.search).get("slide"));
      setIndex(Number.isInteger(requested) && requested >= 1 && requested <= count ? requested - 1 : 0);
      setLabOpen(false);
    };
    const syncFullscreen = () => setFullscreen(Boolean(document.fullscreenElement));
    restore();
    window.addEventListener("popstate", restore);
    document.addEventListener("fullscreenchange", syncFullscreen);
    return () => {
      window.removeEventListener("popstate", restore);
      document.removeEventListener("fullscreenchange", syncFullscreen);
    };
  }, [count]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.defaultPrevented || document.querySelector("dialog[open], [aria-modal='true']")) return;
      if (event.key === "Escape") {
        if (labOpen) setLabOpen(false);
        else if (!document.fullscreenElement) window.location.assign("/");
        return;
      }
      if (labOpen || (event.target instanceof Element && event.target.closest("input, textarea, select, [contenteditable]"))) return;
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        goTo(Math.min(count - 1, Math.max(0, index + (event.key === "ArrowRight" ? 1 : -1))));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [count, goTo, index, labOpen]);

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
      setFullscreenError(false);
    } catch {
      setFullscreenError(true);
    }
  }

  return (
    <div className="mx-auto flex min-h-dvh max-w-[1440px] flex-col px-4 py-5 sm:px-10">
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-obs-border pb-4">
        <span className="font-mono text-xs uppercase tracking-widest text-sci-causal">CausalFade · Presentation</span>
        <div className="flex flex-wrap gap-2">
          <button type="button" className={control} onClick={toggleFullscreen}>{fullscreen ? <Minimize size={15} /> : <Maximize size={15} />}{fullscreen ? "Exit full screen" : "Full screen"}</button>
          <Link className={control} href="/"><X size={15} /> Exit presentation</Link>
        </div>
      </header>
      {fullscreenError && <p role="status" className="mt-2 text-sm text-sci-caution">Full screen is unavailable in this browser window.</p>}

      {labOpen ? (
        <main className="grow py-5">
          <button type="button" autoFocus onClick={() => setLabOpen(false)} className={`mb-5 ${control}`}><ArrowLeft size={15} /> Return to slide {index + 1}</button>
          <CausalLab />
        </main>
      ) : (
        <main className="flex grow flex-col justify-center py-10 sm:py-16">
          <div aria-live="polite" aria-atomic="true">
            <h1 className="max-w-5xl font-serif text-4xl leading-[1.08] tracking-tight sm:text-6xl lg:text-7xl">{slide.title}</h1>
            <p className="mt-5 max-w-4xl text-lg leading-relaxed text-obs-secondary sm:text-2xl">{slide.text}</p>
          </div>
          <div className="mt-6 flex flex-wrap gap-2">
            {slide.lab && <button type="button" className={control} onClick={() => setLabOpen(true)}>Open interactive causal lab <ArrowRight size={15} /></button>}
            {slide.evidence && <EvidenceButton meta={slide.reversal ? study.reversalEvidence : study.provenance} title={slide.title} />}
          </div>
          {notesOpen && <p id="slide-notes" className="mt-5 max-w-3xl rounded border border-obs-border bg-obs-surface p-3 text-sm text-obs-secondary">{slide.note}</p>}
        </main>
      )}

      <footer className="space-y-3 border-t border-obs-border pt-4">
        <progress aria-label="Presentation progress" className="block h-1 w-full accent-sci-causal" value={index + 1} max={count} />
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span className="font-mono text-sm text-obs-secondary">Slide {index + 1} of {count}</span>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={control} aria-expanded={notesOpen && !labOpen} aria-controls={notesOpen && !labOpen ? "slide-notes" : undefined} disabled={labOpen} onClick={() => setNotesOpen(!notesOpen)}>Speaker notes</button>
            <button type="button" className={control} disabled={labOpen || index === 0} onClick={() => goTo(index - 1)}><ArrowLeft size={15} /> Previous</button>
            <button type="button" className={control} disabled={labOpen || index === count - 1} onClick={() => goTo(index + 1)}>Next <ArrowRight size={15} /></button>
          </div>
        </div>
      </footer>
    </div>
  );
}
