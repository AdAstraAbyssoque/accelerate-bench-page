#!/usr/bin/env python3
"""Rebuild dist/assets/results.json from the frozen benchmark v1.1 snapshot behind paper Table 1.

Usage: python3 scripts/build_results_v11.py <snapshot-folder> <task-metadata.json>
The folder is figures/data/v11-round1-unified-20261116 of the manuscript source: stats.json holds the Table 1 rows
as rendered in the paper and cells.jsonl the first-run reward of every agent on every task. The metadata file holds
the task.toml values of the released v1.1 task packages (version, CPUs, memory, agent and verifier time limits).
Areas, diagrams, authors and institutions keep their published values; tasks keep their v1.0 identifiers, mapped below.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist' / 'assets' / 'results.json'
SNAP = Path(sys.argv[1])
TASK_META = json.loads(Path(sys.argv[2]).read_text())
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

names = {V10_TO_V11[t['id']]: t['name'] for t in published['tasks']}
stopped = {r['system']: r['stopped'] for r in rows if r['stopped']}
assert all(cells[s, t]['stopped'] and not cells[s, t]['correct'] for s, ts in stopped.items() for t in ts)
assert sum(c['stopped'] for c in cells.values()) == sum(len(ts) for ts in stopped.values())
models = [{'name': r['system'], 'harness': 'Codex' if r['system'].startswith('GPT-') else 'Claude Code', 'effort': 'high',
           'score': round(r['score'], 1), 'ref': round(r['ref_score'], 1), 'gm': round(r['gm'], 2),
           'a125': round(r['A_1.25'], 1), 'a2': round(r['A_2'], 1), 'steps': None, 'tokens': None,
           'stopped_tasks': [names[t] for t in r['stopped']]} for r in rows]
whole = lambda x: int(x) if float(x).is_integer() else round(x, 1)
tasks = []
for t in published['tasks']:
    v11 = V10_TO_V11[t['id']]
    meta = TASK_META[v11]
    rewards = []
    for r in rows:
        c = cells[r['system'], v11]
        rewards.append(round(100 * c['reward'], 1) if c['correct'] else None)
    tasks.append(dict(t, version=meta['version'], cpus=meta['cpus'], memory_gib=whole(meta['memory_mb'] / 1024),
                      agent_hours=whole(meta['agent_timeout_sec'] / 3600), verify_minutes=whole(meta['verifier_timeout_sec'] / 60),
                      rewards_percent=rewards, stopped_agents=[r['system'] for r in rows if v11 in r['stopped']]))
own = {s: [c for (x, t), c in cells.items() if x == s and not c['stopped']] for s in stopped}
own_score = {s: round(100 * sum(c['reward'] for c in cs if c['correct']) / len(cs), 1) for s, cs in own.items()}
stop_text = ' '.join(
    "On %s, the provider's safety system stopped the %s run; these runs count as failures with zero reward. On its other %d tasks, "
    "%s scores %.1f%%." % (', '.join(names[t] for t in ts[:-1]) + ' and ' + names[ts[-1]] if len(ts) > 1 else names[ts[0]], s,
                           len(own[s]), s, own_score[s]) for s, ts in stopped.items())

results = {
    'title': published['title'],
    'snapshot': 'Benchmark v1.1, first run of each agent; all final programs scored on one machine (manuscript of 16 November 2026)',
    'metric_note': ('Table 1 reports 512 agent-task outcomes: 16 agents and the 32 tasks of benchmark v1.1. Every agent runs once '
                    'per task and this run is scored; all final programs are scored on the same machine. A run stopped by an '
                    'infrastructure or model-API failure is replaced by a new run fixed in advance; failures caused by the agent '
                    'are scored. Gemini-3.8-Flash is not listed because its v1.1 runs are not yet complete. ' + stop_text +
                    ' Per-task rewards are rounded; recompute nothing from them.'),
    'models': models,
    'tasks': tasks,
    'areas': published['areas'],
    'authors': published['authors'],
    'institutions': published['institutions'],
    'sources': {'leaderboard': 'Paper Table 1 (benchmark v1.1)', 'tasks': 'task.toml of the released v1.1 task packages',
                'per_task': 'First-run rewards on benchmark v1.1 from the frozen snapshot behind Table 1',
                'analysis': 'Separate 480-run analysis cohort on benchmark v1.0; paper Section 5 and appendices'},
    'selection': {'snapshot_id': SNAP.name, 'benchmark_version': '1.1', 'aggregation': 'first_run',
                  'scoring': 'all final programs scored once on the same machine', 'not_listed': stats.get('omitted', []),
                  'stopped_by_provider_safety_system': stopped, 'score_on_other_tasks': own_score},
}
OUT.write_text(json.dumps(results, indent=1, ensure_ascii=False) + '\n')
print('wrote', OUT.relative_to(ROOT), len(models), 'models', len(tasks), 'tasks; top three:', [m['name'] for m in models[:3]])
