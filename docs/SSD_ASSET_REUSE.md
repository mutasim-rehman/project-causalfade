# Reusing AGERE assets for CausalFade

Audit date: 7 November 2026. Donor: `H:\AGERE`. Destination: `H:\CAUSALFADE`. The copy utility and final import manifest distinguish planned files from successfully verified files. No model inference has been run as part of this import.

## Selected assets

The donor has original Qwen2.5-Instruct checkpoints at all four study sizes, including model shards, tokenizer files, model configs and generation configs:

- `weights/hf/Qwen--Qwen2.5-0.5B-Instruct`
- `weights/hf/Qwen--Qwen2.5-1.5B-Instruct`
- `weights/hf/Qwen--Qwen2.5-3B-Instruct`
- `weights/hf/Qwen--Qwen2.5-7B-Instruct`

Their safetensors headers identify BF16 weights; do not label these raw checkpoints FP16. The converted GGUF baseline files identify mostly F16 tensors with F32 tensors for some components.

Five GGUF artifacts have matching recorded source revisions and expected SHA-256 digests in AGERE's phase2 manifests:

- `qwen2.5-0.5b-instruct-f16.gguf`: 0.926 GiB.
- `qwen2.5-1.5b-instruct-f16.gguf`: 2.881 GiB.
- `qwen2.5-3b-instruct-f16.gguf`: 5.754 GiB.
- `qwen2.5-7b-instruct-f16.gguf`: 14.191 GiB.
- `qwen2.5-7b-instruct-q4_k_m.gguf`: 4.361 GiB.

The revisions are respectively `7ae557604adf67be50417f59c2c2f167def9a775`, `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, `aa8e72537993ba99e69dfaafa59ed015b17504d1`, and `a09a35458c702b33eeacc393d103063234e8bc28`. The two 7B artifacts share the last revision. The recorded conversion runtime commit is `7fe450e19305b828c199d602c23a8337aaa1f03b`; this is historical provenance, not the selected runtime for new experiments.

Original checkpoints plus the five GGUFs occupy about 51.9 GiB. Small provenance files and this project's synthetic datasets add a modest amount. Copying both originals and converted models deliberately duplicates representations to keep CAUSALFADE independent of the donor folder.

## Other useful assets and why they are conditional

- `H:\AGERE\tmp\torch-2.6.0+cu124-cp312-cp312-win_amd64.whl` is an existing 2.358 GiB installer candidate for Python 3.12, Windows x64 and that CUDA build. It is not copied or installed automatically: target OS, Python, driver and dependency compatibility remain to be selected.
- `runtime/agere-cpu-v1` and `runtime/agere-cpu-v2` declare Linux-x86_64 CPU runtimes. Their manifests are retained as evidence. The complete runtime directories are not imported as a presumed Windows/GPU runtime.
- Tokenizer/config files are copied with each original model so local use does not depend on resolving them online. Download metadata and cached source-tree records are preserved separately under `manifests/agere_source`.
- Preparation logs for the four FP16 conversions and the 7B Q4 quantization are retained as provenance, distinct from AGERE experimental results. The 7B log records direct F16-to-Q4_K_M conversion without an importance-matrix argument, successful completion, and a reported quantized tensor-data rate of about 4.91 BPW. This excludes container metadata and is not exactly four bits per weight across the model.
- Current synthetic tasks and their oracle/baseline records are placed in `datasets/design_validation`. All source code belongs in the Git repository. The initial redundant `runtime/source` snapshot has been removed under the data-only storage policy; the removal is recorded in the migration report and journal.

## Assets excluded from the baseline import

- 14B and 32B checkpoints are outside the agreed four-size study.
- The `tier8_v2` 0.5B native-F16 file has 291 tensors and a different context metadata value, versus 290 tensors in the documented converted baseline. The tier8 3B Q4 file has 435 tensors, versus 434 in the documented F16 model. These differences can reflect packaging or tied-weight handling; they do not by themselves prove training changes. Their derivation/parity has not been established, so they are not silently substituted into a controlled precision comparison.
- The tier8 7B Q4 files form a split checkpoint and carry different context metadata from the single-file artifact. They are unnecessary duplicates for this import. Never use a single shard as a complete checkpoint.
- Adapters, hf-training assets and trained/merged checkpoints are excluded. They are not interchangeable with untouched instruction-tuned baselines.
- AGERE run logs, fitted parameters and project-specific datasets are not CausalFade observations. FRAMES and the mortgage/financial-document material found under external datasets are not replacements for the planned SCM-generated causal evaluation. Reuse as a separately justified control would require its own protocol and contamination review.
- No reusable importance-matrix file was found in the filename inventory. A fresh disjoint calibration set/procedure is still needed if the selected quantizer requires one.

## What remains to prepare

The selected GGUFs cover five of the nominal twenty size/precision combinations: four F16 baselines and one 7B Q4 configuration. They do not provide the other fifteen configurations. Most missing variants can potentially be generated from the retained high-precision sources without downloading the models again, once quantizer/backend support is verified. Approximately 1-bit formats must be recorded by exact format and effective precision, not inferred from filenames.

Hashes and revision records establish local provenance and transfer integrity; they do not verify numerical parity between HF and GGUF inference or certify every binary/runtime combination. Before collection, run a fixed smoke/parity set with controlled chat template, decoding, context and tensor/cache precision. Explicitly override model-embedded sampling defaults.

## Copy safety and reproducibility

The [copy utility](../tools/reuse_ssd_assets.py) defaults to a read-only plan:

```bash
python tools/reuse_ssd_assets.py
python tools/reuse_ssd_assets.py --apply
```

It validates paths under the named destination, checks free space with a reserve, refuses conflicting destination files, and writes copies through a staging suffix. A partial transfer is resumed only after validating its prefix against the source. Original donor files are read, not modified, moved or hardlinked. Full source-content hashes must match locally recorded donor digests, and destination content is read back before promotion. This is not a fresh upstream authenticity attestation.

The default report directory is `results/asset_reuse`. Successful completion writes `import_result.json` there and `manifests/agere_reuse_import.json` on the SSD. The append-only per-file journal is `manifests/agere_reuse_journal.jsonl`. Check `status=complete_verified`; a plan alone does not indicate completion. Historical journal entries describe past transfers; the current manifest describes retained assets after source-snapshot removal.

## Storage policy and changing PCs

The repository is the sole location for research source, scripts, analysis and visualization code, dependency specifications and methodology documentation. Commit and push code changes before switching PCs. Keep virtual environments and inference executables on each PC's local disk; recreate them from dependency specifications rather than copying them onto the SSD.

The SSD holds only weights, tokenizer/config assets, datasets, runtime logs, results and provenance. Its root README points back to GitHub. The importer restricts destinations to data directories and inert asset extensions, rejecting scripts, binaries, installers, environments and source snapshots. Manual copies must follow the same policy. The maintenance utility `tools/enforce_ssd_data_only.py` removes only the previously recorded redundant source snapshot, after checking hashes, and refuses unknown or modified files.

Run commands from the repository checkout. On a new PC, clone/pull the same Git commit, create a local environment, reconnect the SSD and update its drive path. Record the Git commit, dependency versions, model hashes and run configuration with every experiment. Validate a fixed overlap set when changing machines. Back up irreplaceable run data separately; a portable SSD is not itself a backup.
