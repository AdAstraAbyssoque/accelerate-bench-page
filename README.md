# Accelerate Bench project website

Static project page for **Accelerate Bench: Evaluating Agents for Application-Level Program Optimization**.

Site: https://acceleratebench.com/

This repository hosts the website. [Benchmark code](https://github.com/AdAstraAbyssoque/accelerate-bench) is available on GitHub; [versioned task packages and access requests](https://huggingface.co/datasets/AdAstraAbyssoque/accelerate-bench) are on Hugging Face, and 31 of the tasks are public on [Harbor Hub](https://hub.harborframework.com/datasets/accelerate-bench/accelerate-bench).

## Preview and deploy

Run `python3 -m http.server 8765 --directory dist` and open http://127.0.0.1:8765/.
Run `python3 scripts/verify.py` before committing. GitHub Actions deploys `dist/` on pushes to `main`.

## Content and provenance

`dist/assets/results.json` holds the rounded benchmark v1.1 numbers of paper Table 1 (manuscript of November 16, 2026): 16 agents, 32 tasks, 512 outcomes. Every agent runs once per task and this run is scored; all final programs are scored once on the same machine. `scripts/build_results_v11.py` rebuilds the file from the frozen snapshot behind Table 1 (`v11-round1-unified-20261116`: Table 1 rows and per-task first-run rewards); areas, illustrations and authors keep their published values. Gemini-3.8-Flash is not listed because its v1.1 runs are not yet complete. On Graph sparsification, PRESTO and VPIC the provider's safety system stopped the Claude Opus 5.5 run; as in the paper, these runs count as failures with zero reward (`stopped_tasks` and `stopped_agents` in the JSON). Task versions and resource limits come from the `task.toml` files of the released v1.1 packages (`scripts/task-metadata-v11.json`). Null per-task rewards indicate failed correctness. Do not recompute main-table aggregates from the rounded per-task table. The 480-run analysis cohort is separate and uses benchmark v1.0.

DeepSeek-V4.1-Flash-1017 identifies the model version evaluated on benchmark v1.1; the historical `deepseek-v4.1-flash-expires-on-0910` deployment belongs to v1.0. Benchmark versions are never combined.

The task illustrations and control layout build on the authors' earlier SciAccel website. The paper/results/findings structure also references ExplorationBench (https://explorationbench.com/). The Tencent Hy wordmark comes from the Hy-MT2 paper source (https://arxiv.org/abs/2605.22064) and remains its owner's mark. Font licenses are supplied in `dist/assets/fonts/`.

The PDF is the benchmark v1.1 preprint prepared for arXiv. The arXiv record will be added after release. No acceptance status or arXiv identifier is implied.

## License

Original website code is Apache-2.0; see LICENSE and LICENSING.md. Third-party assets retain their own notices. The manuscript and LaTeX template are separate.
