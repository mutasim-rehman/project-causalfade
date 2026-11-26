[Date of submission]

Editors, *IEEE Transactions on Neural Networks and Learning Systems*

Dear Editors,

Please consider “Evaluating Target-Population Intervention Decisions in Language Models With Matched Switch and Invariance Tests” as a regular article. We introduce CF-TP1, a benchmark for testing whether a neural language model selects an intervention using the evidence source and target-population mixture that determine the correct action. Its paired, feasible data-generating worlds distinguish correct reversals, incorrect reversals and warranted invariance. The arithmetic prompt provides a matched control with the governing table and weighting procedure made explicit.

The completed empirical study is a proof-of-concept case study of one Qwen2.5-7B-Instruct Q4_K_M deployment across 128 numerical families. Its causal and arithmetic target-pair fidelity were 128/512 and 146/512; the prespecified contrast was inconclusive. Directional diagnostics nevertheless revealed 3/256 correct causal reversals where a target change required one, alongside 995/1,024 activation responses. The release includes the frozen prompts, exact oracle, response journal, analysis and reproduction instructions.

The data and code are available in the [public release archive](https://github.com/mutasim-rehman/project-causalfade/releases/tag/cohort-029-v1.0.0). The manuscript discloses its single-deployment scope and the documentary limitation on independent pre-inference review of the transfer form.

[Insert final author approval, exclusivity, competing-interest declarations and any related-submission information after all authors confirm them.]

Sincerely,

Mutasim ur Rehman  
Corresponding author  
FAST National University of Computer and Emerging Sciences, Islamabad, Pakistan  
i242514@isb.nu.edu.pk
