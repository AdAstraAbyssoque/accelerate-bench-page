# Accelerate Bench project website

Static project page for **Accelerate Bench: Evaluating Agents for Application-Level Program Optimization**.

Site: https://adastraabyssoque.github.io/accelerate-bench-page/

This repository hosts the website. The benchmark code and versioned task packages are being prepared separately.

## Preview and deploy

Run `python3 -m http.server 8765 --directory dist` and open http://127.0.0.1:8765/.
Run `python3 scripts/verify.py` before committing. GitHub Actions deploys `dist/` on pushes to `main`.

## Content and provenance

`dist/assets/results.json` preserves the rounded numbers reported in the September 26, 2026 manuscript: 12 agents, 32 tasks, 384 main runs. The 480-run analysis cohort is separate. Null per-task rewards indicate failed correctness. Do not recompute main-table aggregates from the rounded per-task table.

DeepSeek-V4.1-Flash (0910) identifies the historical `deepseek-v4.1-flash-expires-on-0910` deployment. Subsequent model versions require new evidence and separate rows; this page does not claim new evaluations have completed.

The task illustrations and control layout build on the authors' earlier SciAccel website. The paper/results/findings structure also references ExplorationBench (https://explorationbench.com/). The Tencent Hy wordmark comes from the Hy-MT2 paper source (https://arxiv.org/abs/2605.22064) and remains its owner's mark. Font licenses are supplied in `dist/assets/fonts/`.

The PDF is an arXiv preparation draft. The arXiv record and benchmark package links will be added after release. No acceptance status or arXiv identifier is implied.
