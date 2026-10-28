"""Build the Markdown review from checked sources and explicit reviewer interpretations."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
# date, status, evidence locations, paper summary, reviewer assessment, proposed use
NOTES = {
'01': ('2025-12-13; downloaded revision: 2025-12-24 (v2)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1, 6-9, 11; Sections 5.5-6 and limitations',
 'Tests Llama-3-8B at BF16, INT8 and NF4 on 3,000 stratified CLadder examples and CRASS, with greedy decoding and an additional ground-truth-graph retrieval condition. Overall NF4 degradation is reported as under one percentage point; interventional questions are more sensitive than the aggregate score suggests. The evaluation includes bootstrap uncertainty. Graph augmentation modestly improves interventional performance.',
 'This is the closest prior study and challenges any assumption that four-bit compression necessarily destroys causal competence. One model and static questions provide limited coverage of agents or extreme compression. A small observed difference is not itself an equivalence result. Graphs supplied to the prompt are external knowledge, not recovered neural circuits.',
 'Replicate a narrow baseline before extending to 2/3-bit models and interactive interventions. Use this as the central related-work comparison, not evidence that the proposed project has already established its conclusion.'),
'02': ('2026-06-24; downloaded revision: 2026-06-29 (v2)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1, 3-6; experimental setup and results',
 'Evaluates low-bit reasoning across mathematical, coding, science and tool-use settings. INT3/INT4 models can maintain final-answer accuracy while producing longer, more repetitive reasoning. The authors propose a chain-of-thought token-inflation measure and examine serving costs and mitigation. Their results show that per-token efficiency and answer accuracy can miss a substantial behavioral change.',
 'This supports measuring the process as well as the answer, but repetition is not direct evidence of associative reasoning or a damaged causal graph. Effects are conditional on model, quantizer and decoding setup. Its output-length result differs from paper 05, motivating a comparison of evaluation conditions.',
 'Log generated tokens, latency, stop reasons and tool calls. Separate a fixed-token-budget experiment from a generous-budget sensitivity analysis; otherwise truncation may be mistaken for a selective causal deficit.'),
'03': ('2026-06-01 (v1)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1-4, 9; failure taxonomy and limitations',
 'Studies Qwen3 reasoning at two model scales using GPTQ-style W2A16/W4A16 inference. Two-bit traces exhibit looping, exhausted budgets and failures to commit to answers. The authors test high-precision planning and loop-rescue procedures. On MATH-500, reported Qwen3-8B accuracy rises from 17.2% to 74.2% with loop rescue.',
 'A large final-answer drop can therefore reflect generation control rather than lost causal knowledge. Recovery uses selective high-precision assistance, so it is not a pure two-bit treatment. The limitations explicitly restrict quantizer and model-family generalization.',
 'Include a failure taxonomy: incorrect inference, invalid tool action, repetition, truncation and missing final answer. Keep rescued runs as a separate intervention arm. Test whether any causal-task deficit remains after accounting descriptively for these process failures.'),
'04': ('2026-01-21 (v1)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1, 3-8, 9; empirical comparisons and limitations',
 'Systematically studies quantization-aware training for reasoning models. Knowledge distillation, post-training-quantization initialization and calibration/training-domain alignment form the Reasoning-QAT workflow. The authors also investigate reinforcement learning after a viable initialization. The evaluated workflow improves low-bit reasoning over PTQ baselines, including two-bit settings. Training is primarily math-oriented, with limited cross-domain transfer noted.',
 'The quality of a low-bit model depends on its training and calibration history, not only its nominal bit width. These experiments do not directly assess causal-agent decisions. Comparing a QAT model with an untouched full-precision model bundles precision changes with additional training.',
 'Use PTQ as the first controlled treatment. Consider QAT only as a later recovery experiment with an appropriate training-matched comparison. Record calibration data and checkpoint provenance in every run.'),
'05': ('2025-04-07; downloaded revision: 2025-08-18 (v2)', 'COLM 2025; venue stated on arXiv and in the paper', 'PDF pp. 1-8; study design and main results',
 'Evaluates weight, activation and KV-cache quantization across DeepSeek-R1-distilled families and other reasoning models on mathematics, science and coding. W8A8 and W4A16 can preserve measured performance in tested settings, while lower precision introduces greater risk. Model scale, origin and task difficulty affect robustness. Unlike paper 02, this study does not find increased output lengths in its evaluated regime.',
 'This is strong background for selecting compression conditions, but general reasoning benchmarks do not isolate causal reasoning. Claims of lossless performance should be interpreted within the tested benchmarks and uncertainty, not as a universal guarantee.',
 'Hold activation and KV-cache precision fixed while varying weights initially. Include multiple checkpoints if feasible, and do not equate identical bit widths across different quantizers. Treat output-length disagreement as a question to test, not a contradiction to hide.'),
'06': ('2025-05-16; downloaded revision: 2026-01-20 (v4)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1-8; process-level analysis and recovery experiments',
 'Examines AWQ, GPTQ and SmoothQuant on Qwen/LLaMA models and mathematical benchmarks using aligned solution steps. Method and execution errors increase more than high-level conceptual errors, and an early faulty step can propagate to the final answer. A targeted measure-locate-restore workflow uses small curated training sets to recover performance in evaluated low-bit settings.',
 'The process-level distinction is valuable for separating damaged execution from lost knowledge. However, mathematical error labels and successful fine-tuning do not identify an internal causal graph. Alignment and annotation choices also matter when interpreting the first erroneous step.',
 'Annotate the earliest observable failure in agent trajectories. Distinguish choosing an invalid causal adjustment from correctly identifying the adjustment but executing code incorrectly. Use trace categories as secondary outcomes; avoid claiming that the written trace faithfully exposes every internal computation.'),
'07': ('2025-04-02; downloaded revision: 2026-03-02 (v3)', 'ICLR 2026; stated in the downloaded paper', 'PDF pp. 1-10; benchmarking, component attribution and selective protection',
 'Compares quantization, pruning and distillation on DeepSeek-R1 variants across four reasoning datasets. It combines benchmarking with activation-based attribution and targeted component protection. The authors identify vulnerable final-layer and MLP modules; protecting approximately 2% of weights improves average accuracy by a reported 6.57% in their experiment. Knowledge and reasoning respond differently to compression.',
 'This is the most useful bridge here from behavioral evaluation to component interventions. Nevertheless, compression methods change different properties, and an attributed reasoning component is not automatically a representation of a domain causal edge. Interpret the reported percentage in the paper\'s own metric rather than assuming percentage points.',
 'If the behavioral result is robust, test selected component precision restoration with equal-weight-count controls. Keep pruning and distillation outside the primary quantization comparison. Specify the exact causal claim supported by each manipulation.'),
'08': ('2026-02-23; downloaded revision: 2026-06-25 (v2)', 'arXiv preprint; abstract page says under review', 'PDF pp. 1-7; paired construction and experimental comparisons',
 'Builds semantically similar question pairs with opposite causal answers using chain, confounder and collider relationships. Additional noisy prefixes leave the underlying causal logic unchanged while stressing semantic shortcuts. The authors compare training paradigms and report that explicit chain-of-thought supervision can still be misled, while their internalized-reasoning approach improves causal grounding.',
 'This closely matches the proposed distinction between causal reasoning and semantic association. It is a question-answering benchmark, however, and does not itself show quantization causes shortcut reliance. Synthetic event triples also cover only a limited slice of causal reasoning.',
 'Adapt paired contrasts for every precision setting and test the precision-by-shortcut-conflict interaction. Counterbalance answer labels and paraphrases. Use the pairs as diagnostics alongside an interactive environment, so the project remains about agents making interventions.'),
'09': ('2026-05-25; downloaded revision: 2026-05-28 (v2)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1-3, 7-12; setup, mechanism scores and limitations',
 'Introduces an interactive synthetic laboratory with a hidden SCM. Agents observe records, intervene and predict a held-out outcome; explicit hypotheses permit graph and mechanism scoring. In a six-node observational setting, GPT-5.2-high achieves 92% task accuracy but 0.471 all-edge F1. Mixed observation/intervention strategies improve structural fidelity. The evaluated worlds contain 3-7 nodes and mostly linear mechanisms.',
 'This demonstrates why predictive accuracy and recovered structure should be scored separately. An agent-written graph is still an externalized hypothesis, not a direct measurement of its neural representation. Synthetic mechanisms and a finite model/prompt suite constrain generalization.',
 'Use this as the main interactive design reference. Score intervention success, graph recovery and exploration behavior independently. For precision comparisons, reuse world seeds and observation budgets, but allow actions and resulting observations to differ naturally across agents.'),
'10': ('2026-09-16 (v1)', 'arXiv preprint; explicitly a preliminary benchmark audit', 'PDF pp. 1-3, 10; scoring contract and Section 6.4',
 'Defines budgeted observe-intervene-submit interactions in linear-Gaussian SCMs, separating skeleton recovery, directed-graph recovery and intervention efficiency. PC with active orientation outperforms the evaluated LLM agents on directed F1. A random-DAG baseline obtains a substantial score in dense worlds. The authors identify density leakage, eight seeds per level and limited backbone coverage as important limitations.',
 'This is useful precisely because it audits benchmark weaknesses rather than treating every nonzero score as causal understanding. Its sample size is inadequate for fine-grained rankings, and causal sufficiency and linearity narrow the target setting.',
 'Include random, observational-only and classical causal-discovery baselines. Pilot graph density and difficulty before the main experiment. Estimate uncertainty over independent worlds and expand the number of seeds rather than inflating apparent sample size through paraphrases of the same world.'),
'11': ('2026-07-09; downloaded revision: 2026-10-14 (v2)', 'arXiv preprint; peer-reviewed publication not verified', 'PDF pp. 1-8, 60 onward; benchmark design and Appendix A.17',
 'Generates causal data-science scenes from sampled SCMs, observational data and grounded narratives. Tasks span association, intervention and counterfactuals, often requiring code and tools. Some targets are intentionally unidentifiable, making abstention the correct response. The generator permits fresh exams. Limitations include synthetic realism and a graph-based identifiability policy that does not credit every alternative inferential strategy.',
 'This is particularly relevant to an advanced statistics course because it tests whether agents can identify and estimate causal targets, not merely repeat causal language. However, failures combine reasoning, coding and data-analysis demands; no quantization comparison is established by this paper alone.',
 'Borrow a small, transparent subset of identifiable and unidentifiable tasks. Grade identification, numerical estimation, interval coverage and abstention separately. Use ordinary statistical estimators as reference solutions, with assumptions and numerical tolerances documented.'),
'12': ('2026-10-06 online publication; journal issue metadata says 2026/12', 'Discover Computing 29, article 700 (2026); open-access journal article', 'PDF pp. 1-4, 33-34; framework and limitations',
 'PRISM separates parametric recall, contextual copying and comprehension using conflict probes, synthetic entities and component-wise quantization. Across tested small-model families and quantizers, closed-book recall deteriorates while copying remains more robust. MLP/FFN quantization affects recall more than attention quantization. The work runs within an 8GB GPU budget and explicitly limits component-level conclusions and model scale.',
 'This is the most directly relevant control for the proposed forgetting explanation. Preserved copying is insufficient evidence of preserved reasoning. The authors also caution that component sensitivity is weaker evidence than proving a component stores a fact. Publisher online date qualifies this paper despite its later issue-date metadata.',
 'Build separate closed-book recall, supplied-context comprehension and causal-decision controls. Use fictional entities to check leakage. If feasible, adapt matched component perturbations, while distinguishing component necessity under perturbation from a claim about stored causal representations.'),
'13': ('NAACL 2025 proceedings, April-May 2025', 'NAACL 2025, Volume 1: Long Papers; review plus empirical evaluation', 'PDF pp. 1-8; taxonomy, evaluation and challenges',
 'Combines a review of causal-reasoning enhancement methods with empirical evaluation. It distinguishes language models acting as reasoning engines from models assisting traditional causal methods with knowledge or data. It organizes tasks across levels of causality and discusses prompting, training and causal representations. Reliable causal reasoning remains uneven across settings and enhancement strategies.',
 'Useful for defining the project\'s task taxonomy and positioning its contribution. It is not a quantization experiment, and its heterogeneous evaluation should not be pooled directly with quantization papers into a single effect size. A survey category is also not proof of an internal mechanism.',
 'Use the taxonomy to label each outcome and identify what the agent itself must infer versus what a tool supplies. Include symbolic and numerical components, but keep one primary outcome to avoid a project with many weakly connected tests.'),
'14': ('Findings of NAACL 2025, April-May 2025', 'Findings of NAACL 2025; survey', 'PDF pp. 1-7; preliminaries, task categories and future directions',
 'Reviews LLM-assisted causal inference across tasks, methods, datasets and evaluation. It introduces structural causal models and distinguishes levels of causal queries, discussing how language-model knowledge can assist causal analysis. The survey highlights challenges including unverified causal ground truth, hallucinations and the need for better evaluation and interaction.',
 'This supplies terminology and broad context rather than direct evidence for quantization-induced degradation. Much of the reviewed evidence comes from older studies, so the 2025 publication date does not make every underlying experiment a 2025 result. It should not be treated as an independent experimental replication.',
 'Use it to separate causal discovery, identification, estimation and counterfactual inference in the proposal. Ground the experiment in a simulator with known assumptions, and independently justify the statistical estimator used to measure the effect of quantization.'),
}

manifest=json.loads((ROOT/'paper_manifest.json').read_text(encoding='utf-8'))
index=[]
for p in manifest:
 key=p['slug'][:2]
 date,status,loc,summary,assessment,use=NOTES[key]
 title=p['metadata']['citation_title'][0]
 authors='; '.join(p['metadata'].get('citation_author',[]))
 body=f'''# {title}

- **Authors:** {authors}
- **Date / version:** {date}
- **Publication status:** {status}
- **Theme:** {p['topic']}
- **Primary source:** [{p.get('arxiv_version') or 'Publisher record'}]({p['landing_url']})
- **Downloaded paper:** [PDF ({p['pages']} pages)](../papers/{p['slug']}.pdf)
- **Evidence locations:** {loc}. Page numbers refer to PDF positions.

## Research question, approach and findings

{summary}

## Critical assessment

{assessment}

## Application to CausalFade (reviewer's proposal)

{use}

---
Prepared 2026-10-28 from the downloaded full text and source record. Findings above are the authors' reports, not independently reproduced results. Critical assessment and proposed applications are reviewer interpretations. [Return to executive summary](../EXECUTIVE_SUMMARY.md).
'''
 (ROOT/'summaires'/f"{p['slug']}.md").write_text(body,encoding='utf-8')
 p['review_date_note']=date
 p['publication_status']=status
 p['verification']='PDF parsed; full text extracted; source metadata and relevant sections inspected'
 index.append(f"{int(key)}. **{title}** — {date}. [{p['topic']} summary](summaires/{p['slug']}.md) · [PDF](papers/{p['slug']}.pdf) · [Source]({p['landing_url']})")
(ROOT/'paper_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'READING_INDEX.md').write_text('# Reading index\n\n'+'\n\n'.join(index)+'\n',encoding='utf-8')
print(f'Wrote {len(manifest)} individual summaries and the linked reading index.')
