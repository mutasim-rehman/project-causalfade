# CausalFade 
<!-- testing -->
**Does aggressive quantization change how AI agents reason about causes?**

CausalFade is an advanced statistics course research project at the intersection of AI agents, model quantization and causal inference. It investigates whether compressed models become more vulnerable to misleading associations when choosing interventions, and whether this differs from factual recall loss or general reasoning degradation.

## Overarching research commitment

**Causal inference in language models is a central pillar of this research.** The project aims to build rigorous evidence about whether and how LLMs identify causal structure, estimate intervention effects, choose informative interventions, and make decisions from causal evidence. Statistical design and inference are essential to evaluating those capabilities; agentic, multi-step interaction is an important evaluation direction. Quantization is one experimental factor through which these capabilities may be studied, not a substitute for the broader causal-inference research objective. Each study must state which causal capability it measures and distinguish causal reasoning evidence from prompt sensitivity, response-format compliance, arithmetic execution, and general task performance.

## Research question

> Does aggressive post-training quantization increase an AI agent's reliance on misleading associations when choosing interventions, beyond its general effect on task performance?

The motivating idea is that compression might disrupt mechanisms supporting causal reasoning. The primary experiment will measure **behavioral causal competence**. Claims about damaged internal causal graphs require additional mechanistic interventions and cannot be established by accuracy alone.

## Current status

The project now has an **executable simulator and synthetic methodology-validation package**, plus 14 research papers from 2025–2026 and critical summaries. Eight papers were first released or published in 2026. Live exploratory direct-response pilots began on 10 November 2026. Follow the [experiment index](EXPERIMENTS.md), [decision log](DECISIONS.md), and [session report](SESSION_REPORT.md) for the latest evidence. The synthetic parameter-recovery package is separate from model evaluation.

Read the [research methodology](docs/RESEARCH_METHODOLOGY.md), [reproduction instructions](docs/REPRODUCIBILITY.md), and [generated validation report](results/design_validation/VALIDATION_REPORT.md). The proposed psychological adaptation separates causal sensitivity, conditional associative influence and residual action bias, with explicit identification and model-fit limitations.

The [implementation and research roadmap](docs/STUDY_ROADMAP.md) defines the lab setup, durable runner, bounded agent, pilot, power analysis, protocol freeze, collection, statistics and reporting phases. The roadmap records the original prospective phases. The experiment index tracks the current execution state.

The [methodology adaptation and source evidence](docs/METHODOLOGY_ADAPTATION.md) explains the source papers' findings, why the approach suits this question, the exact CNI-style mapping, and what changes in our application. [BibTeX references](docs/references.bib) are included for the proposal.

The current Ubuntu PC stores model weights and local datasets at `$HOME/Desktop/CAUSALFADE`; current research runs do not use an external SSD. The folder contains all four Qwen2.5-Instruct sizes (0.5B, 1.5B, 3B, 7B) in F16 plus `Q8_0`, `Q4_K_M`, `Q2_K` and `Q1_0` GGUF formats. The [SSD quantization preparation record](docs/SSD_ASSET_REUSE.md#gguf-quantization-prepared-for-lab-use) is historical provenance from the earlier transfer. Each Ubuntu run records the local model digest.

Start with the [executive summary](literature%20review/EXECUTIVE_SUMMARY.md), then use the [reading index](literature%20review/READING_INDEX.md) to browse papers and summaries. Publication status and downloaded versions are documented; reported findings have not been independently reproduced.

## Working hypotheses

Compare matched tasks where an observational association either agrees or conflicts with the beneficial causal intervention. For a precision setting `p`, define:

```text
ConflictPenalty(p) = Accuracy(p, aligned) - Accuracy(p, conflicting)
Delta(p) = ConflictPenalty(p) - ConflictPenalty(full precision)
```

- **Null hypothesis:** `Delta(p) <= 0`. Quantization does not increase the conflict penalty.
- **Alternative hypothesis:** `Delta(p) > 0`. Quantization increases the conflict penalty.

The directional contrast must be prespecified. A positive result supports increased behavioral vulnerability to misleading associations under the tested conditions. Failure to reject the null does not demonstrate preservation; that conclusion needs a predefined practical tolerance and equivalence or noninferiority analysis.

## Planned workflow

1. **Implement a controlled experiment.** Generate small structural causal models with known ground truth and an agent interface for observations, interventions and final decisions. Compare precision variants derived from the same checkpoint, keeping the quantizer, calibration procedure and inference configuration explicit.
2. **Collect reproducible trajectories.** Reuse world seeds across precision conditions. Record observations, actions, tokens, stopping reasons, tool failures and final answers. Include recall, context-comprehension and matched noncausal controls, plus random and classical causal baselines.
3. **Analyze and visualize.** Separate intervention success, graph recovery, estimation error, abstention and process failures. Plot paired changes and effect estimates with uncertainty rather than relying on aggregate accuracy alone.
4. **Estimate causal effects.** Prespecify the primary precision contrast and task population. Use a hierarchical binomial model with precision-by-conflict terms and world-level dependence, report probability-scale contrasts, and check robustness with paired world-level resampling. Choose sample sizes through pilot-based simulation.
5. **Investigate mechanisms if warranted.** Consider targeted component precision restoration after establishing a robust behavioral effect. Treat fine-tuning and high-precision assistance as separate experimental treatments.

This is the broader research workflow; the current implementation covers the simulator and synthetic validation described above. The simulator's true graph, the agent's reported graph and the model's internal computational mechanisms are distinct objects.

## Repository contents

Research code and experiment records live in this Git repository. On this Ubuntu PC, use `$HOME/Desktop/CAUSALFADE` for model weights and local dataset inputs. The `H:\CAUSALFADE` paths in older manifests refer to the earlier Windows setup. Keep model weights and runtime binaries outside Git. Keep per-run logs, configuration, raw responses, and analyses under `experiments/`.

The [historical SSD asset audit](docs/SSD_ASSET_REUSE.md) documents model reuse and earlier transfer checks. Current experiments read the PC-local model/data folder directly. Record the Git commit and environment versions with each experiment; keep a separate backup of irreplaceable results.

```text
causalfade/                Simulator, measurement fitting, scoring and paired analysis
docs/                      Research methodology, data contract and study decisions
tests/                     Simulator, measurement and scoring checks
tools/                     Inference, pilot analysis and asset management utilities
experiments/               Live development runs, raw evidence and cohort analyses
results/design_validation/ Reproducible synthetic tasks and recovery results
literature review/
  EXECUTIVE_SUMMARY.md    Cross-paper synthesis and proposed study
  READING_INDEX.md        Links to all papers and summaries
  paper_manifest.json    Sources, versions, checksums and page counts
  papers/                14 downloaded research PDFs
  summaires/             One critical Markdown summary per paper
  _sources/              Local source-page and extracted-text cache
  download_papers.py     Download and validate the selected sources
  write_review.py        Generate individual summaries and reading index
```

The `summaires` spelling is retained from the original project request. The source cache stays local and is excluded from Git; PDFs, summaries and provenance metadata are versioned.

## Reproducing the research utilities

Python 3.10 or newer is required. NumPy supports the research utilities; pypdf supports the literature downloader.

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m causalfade.generate
python -m causalfade.validate
```

The generator exports 24 independent families, each with four causal/association conditions and two evidence layers. The validation study fits 3,600 independent synthetic response datasets; see its report for convergence failures, weak boundary recovery and observational equivalence. The direct-response pilot runner is in `tools/run_direct_pilot.py`. The hierarchical analyses and confirmatory power calculations remain prospective. See [decisions before collection](docs/DECISIONS_BEFORE_COLLECTION.md).

For the literature tools:

```bash
python -m pip install -r requirements.txt
python "literature review/download_papers.py"
python "literature review/write_review.py"
```

The downloader accesses arXiv, ACL Anthology and Springer, pins arXiv versions, checks PDF headers, parses pages, extracts text and records SHA-256 checksums. It reuses existing PDFs. Run the summary generator after downloading to restore the review annotations in the manifest. The executive summary is maintained separately. These scripts reproduce the selected collection and authored notes; they do not conduct an automated literature search or reproduce the papers' experiments.

## Attribution

Research papers retain their authors' and publishers' copyrights and licenses. Source records are linked in the reading index, individual summaries and manifest. Summaries distinguish authors' findings from reviewer interpretations. No blanket license is granted over the bundled third-party papers.
