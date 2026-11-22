// Regenerate only the two data-backed containers in the committed homepage.
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {rankRow, taskCard} from '../dist/render.mjs';

const homepage = new URL('../dist/index.html', import.meta.url);
const readJson = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const {models, tasks} = readJson('../dist/assets/results.json');
const metadata = readJson('./task-metadata-v11.json');
assert.deepEqual(tasks.map(task => task.directory).sort(), Object.keys(metadata).sort());

const rows = [...models].sort((a, b) => b.score - a.score).map(rankRow);
const cards = tasks.map((task, index) => {
  const {cpus, memory_mb} = metadata[task.directory];
  assert.equal(task.cpus, cpus, task.directory);
  assert.equal(task.memory_gib, memory_mb / 1024, task.directory);
  return taskCard({...task, cpus, memory_gib: memory_mb / 1024}, index);
});

let html = readFileSync(homepage, 'utf8');
function fillContainer(open, close, items) {
  const start = html.indexOf(open);
  const end = html.indexOf(close, start + open.length);
  assert(start !== -1 && start === html.lastIndexOf(open) && end !== -1, open);
  html = html.slice(0, start + open.length) + '\n' + items.join('\n') + '\n' + html.slice(end);
}
fillContainer('<tbody id="rank-rows">', '</tbody>', rows);
fillContainer('<div id="task-grid" class="task-grid">', '</div><!-- /task-grid -->', cards);
writeFileSync(homepage, html);
