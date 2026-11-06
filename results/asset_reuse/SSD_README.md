# CausalFade external SSD — data only

All research code lives in the [GitHub repository](https://github.com/mutasim-rehman/project-causalfade). Run tools from a local checkout. No source snapshots, scripts, executables or environments belong on this SSD.

This directory holds weights, datasets, logs, results and provenance:

- `weights/hf`: original Qwen2.5-Instruct checkpoints and tokenizer/config files for 0.5B, 1.5B, 3B and 7B (BF16 source weights).
- `weights/gguf`: four F16 baselines and all four sizes at Q8_0, Q4_K_M, Q2_K and Q1_0. The original AGERE 7B Q4_K_M file is preserved under `weights/gguf/agere_original`.
- `datasets/design_validation`: synthetic tasks and validation artifacts.
- `runs`: experiment logs/results as collection proceeds.
- `manifests`: hashes, source revisions, preparation logs and transfer history.

See the [asset audit](https://github.com/mutasim-rehman/project-causalfade/blob/main/docs/SSD_ASSET_REUSE.md) and [methodology](https://github.com/mutasim-rehman/project-causalfade/blob/main/docs/RESEARCH_METHODOLOGY.md). The current asset manifest is `manifests/agere_reuse_import.json`; the append-only journal includes historical transfers and subsequent removals.

Quantization commands, output hashes, sizes and per-model logs are recorded in `manifests/quantization_preparation.json` and next to each generated GGUF. The local llama.cpp quantizer was kept on the PC, not this SSD. Q1_0 is recorded by exact GGUF type; its effective storage rate is slightly above one bit per weight because of block scales and metadata.

When changing PCs, clone/pull the repository, recreate the environment on the PC, connect this SSD and update data paths if the drive letter changes. Record the Git commit and environment with each run. Keep a separate backup of irreplaceable results.

Imported weights were checked against locally recorded donor hashes and read back after copying. No upstream re-download or inference parity validation was performed. Model preparation is complete for the listed formats; no inference, evaluation or research data collection has been run. Historical Linux CPU runtime manifests are provenance only.
