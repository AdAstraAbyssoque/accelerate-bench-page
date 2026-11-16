#!/usr/bin/env python3
"""Rebuild dist/assets/results.json from the frozen benchmark v1.1 snapshot behind paper Table 1.

Usage: python3 scripts/build_results_v11.py <snapshot-folder>
The folder is figures/data/v11-round1-unified-20261116 of the manuscript source: stats.json holds the Table 1 rows
as rendered in the paper and cells.jsonl the first-run reward of every agent on every task. Task metadata, areas,
authors and institutions keep their published values; tasks keep their v1.0 identifiers, mapped below.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist' / 'assets' / 'results.json'
SNAP = Path(sys.argv[1])
V10_TO_V11 = {
    'gromacs_cpu': 'gromacs-molecular-dynamics', 'lammps_cpu': 'lammps-molecular-dynamics', 'gpaw_cpu': 'gpaw-fd-dft-restart',
    'qe_cpu': 'qe-scf-nscf-dos', 'siesta_cpu': 'siesta-dft-restart', 'fluidity_cpu': 'fluidity-heat-checkpoint',
    'icon_cpu': 'icon-atmosphere-checkpoint', 'mpas_a_cpu': 'mpas-atmosphere-restart', 'nemo_cpu': 'nemo-lock-exchange',
    'openfoam_cpu': 'openfoam-cavity-piso', 'palabos_cpu': 'palabos-lattice-boltzmann', 'su2_cpu': 'su2-transonic-euler',
    'openmc_cpu': 'openmc-multigroup-transport', 'shengbte_cpu': 'shengbte-phonon-transport', 'vpic_cpu': 'vpic-harris-reconnection',
    'presto_cpu': 'presto-pulsar-search', 'abyss_cpu': 'abyss-genome-assembly', 'mhm2_cpu': 'mhm2-metagenome-assembly',
    'mrbayes_cpu': 'mrbayes-phylogenetics', 'wtdbg2_cpu': 'wtdbg2-long-read-assembly', 'hpcg_cpu': 'hpcg-multigrid-pcg',
    'hpl_cpu': 'hpl-dense-lu', 'pac2020_nufft_cpu': 'nufft-imaging', 'pac_tensor_cpu': 'tucker-reconstruction',
    'ipcc22_sparsify_cpu': 'fegrass-graph-sparsification', 'minivite_cpu': 'minivite-louvain', 'quest_cpu': 'quest-circuit-simulation',
    'asc26_qibotn_cpu': 'qibotn-tensor-network-circuits', 'pac_mqa_cpu': 'paged-lm-generation',
    'pac_thundersvm_cpu': 'thundersvm-train-predict', 'datalife_cpu': 'datalife-io-monitoring', 'io500_cpu': 'io500-file-io'}

published = json.loads(OUT.read_text())
stats = json.loads((SNAP / 'stats.json').read_text())
cells = {(c['system'], c['task']): c for c in map(json.loads, (SNAP / 'cells.jsonl').read_text().splitlines())}
rows = stats['rows']
assert len(rows) == 16 and len(cells) == 16 * 32
assert {t['id'] for t in published['tasks']} == set(V10_TO_V11) and set(V10_TO_V11.values()) == {t for _, t in cells}

models = [{'name': r['system'], 'harness': 'Codex' if r['system'].startswith('GPT-') else 'Claude Code', 'effort': 'high',
           'score': round(r['score'], 1), 'ref': round(r['ref_score'], 1), 'gm': round(r['gm'], 2),
           'a125': round(r['A_1.25'], 1), 'a2': round(r['A_2'], 1), 'steps': None, 'tokens': None} for r in rows]
tasks = []
for t in published['tasks']:
    v11 = V10_TO_V11[t['id']]
    rewards = []
    for r in rows:
        c = cells[r['system'], v11]
        rewards.append(round(100 * c['reward'], 1) if c['correct'] else None)
    tasks.append(dict(t, rewards_percent=rewards))
substituted = {r['system']: r['substituted'] for r in rows if r['substituted']}

results = {
    'title': published['title'],
    'snapshot': 'Benchmark v1.1, first run of each agent; all final programs scored on one machine (manuscript of 16 November 2026)',
    'metric_note': ('Table 1 reports 512 agent-task outcomes: 16 agents and the 32 tasks of benchmark v1.1. Every agent runs once '
                    'per task and this run is scored; all final programs are scored on the same machine. A run stopped by an '
                    'infrastructure or model-API failure is replaced by a new run fixed in advance; failures caused by the agent '
                    'are scored. Gemini-3.8-Flash is not listed because its v1.1 runs are not yet complete. On three tasks where '
                    "the provider's safety system stopped a Claude Opus 5.5 run, the score of Claude Sonnet 5.5 on the same task "
                    'is used. Per-task rewards are rounded; recompute nothing from them.'),
    'models': models,
    'tasks': tasks,
    'areas': published['areas'],
    'authors': published['authors'],
    'institutions': published['institutions'],
    'sources': {'leaderboard': 'Paper Table 1 (benchmark v1.1)', 'tasks': 'Paper appendix, resource allocation table',
                'per_task': 'First-run rewards on benchmark v1.1 from the frozen snapshot behind Table 1',
                'analysis': 'Separate 480-run analysis cohort on benchmark v1.0; paper Section 5 and appendices'},
    'selection': {'snapshot_id': SNAP.name, 'benchmark_version': '1.1', 'aggregation': 'first_run',
                  'scoring': 'all final programs scored once on the same machine', 'not_listed': stats.get('omitted', []),
                  'substituted_by_claude_sonnet_5_5': substituted},
}
OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False) + '\n')
print('wrote', OUT.relative_to(ROOT), len(models), 'models', len(tasks), 'tasks; top three:', [m['name'] for m in models[:3]])
