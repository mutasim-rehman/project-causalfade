# CausalFade external SSD — data only

All research code lives in the [GitHub repository](https://github.com/mutasim-rehman/project-causalfade). Run tools from a local checkout. No source snapshots, scripts, executables or environments belong on this SSD.

This directory holds weights, datasets, logs, results and provenance:

- `weights/hf`: original Qwen2.5-Instruct checkpoints and tokenizer/config files for 0.5B, 1.5B, 3B and 7B (BF16 source weights).
- `weights/gguf`: four F16 baselines and one 7B Q4_K_M checkpoint.
- `datasets/design_validation`: synthetic tasks and validation artifacts.
- `runs`: experiment logs/results as collection proceeds.
- `manifests`: hashes, source revisions, preparation logs and transfer history.

See the [asset audit](https://github.com/mutasim-rehman/project-causalfade/blob/main/docs/SSD_ASSET_REUSE.md) and [methodology](https://github.com/mutasim-rehman/project-causalfade/blob/main/docs/RESEARCH_METHODOLOGY.md). The current asset manifest is `manifests/agere_reuse_import.json`; the append-only journal includes historical transfers and subsequent removals.

When changing PCs, clone/pull the repository, recreate the environment on the PC, connect this SSD and update data paths if the drive letter changes. Record the Git commit and environment with each run. Keep a separate backup of irreplaceable results.

Imported weights were checked against locally recorded donor hashes and read back after copying. No upstream re-download or inference parity validation was performed. Remaining precision configurations and a validated experiment runner still need preparation. Historical Linux CPU runtime manifests are provenance only.
