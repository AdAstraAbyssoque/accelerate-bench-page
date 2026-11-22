// Regenerate data-backed content in the committed static site.
import assert from 'node:assert/strict';
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {esc, rankRow, taskCard, taskPath} from '../dist/render.mjs';
import {taskPage} from './task-page.mjs';

const homepage = new URL('../dist/index.html', import.meta.url);
const readJson = path => JSON.parse(readFileSync(new URL(path, import.meta.url), 'utf8'));
const {models, tasks} = readJson('../dist/assets/results.json');
const metadata = readJson('./task-metadata-v11.json');
assert.deepEqual(tasks.map(task => task.directory).sort(), Object.keys(metadata).sort());

const copy = readJson('./task-pages-copy.json');
assert.deepEqual(Object.keys(copy.tasks).sort(), Object.keys(metadata).sort());
const rows = [...models].sort((a, b) => b.score - a.score).map(rankRow);
const cards = tasks.map((task, index) => {
  const {cpus, memory_mb, version, agent_timeout_sec} = metadata[task.directory];
  assert.equal(task.cpus, cpus, task.directory);
  assert.equal(task.memory_gib, memory_mb / 1024, task.directory);
  assert.equal(task.version, version, task.directory);
  assert.equal(task.agent_hours, agent_timeout_sec / 3600, task.directory);
  return taskCard({...task, cpus, memory_gib: memory_mb / 1024}, index, copy.templates.taskLink);
});

let html = readFileSync(homepage, 'utf8');
function fillContainer(open, close, items) {
  const start = html.indexOf(open);
  const end = html.indexOf(close, start + open.length);
  assert(start !== -1 && start === html.lastIndexOf(open) && end !== -1, open);
  html = html.slice(0, start + open.length) + '\n' + items.join('\n') + '\n' + html.slice(end);
}
fillContainer('<tbody id="rank-rows">', '</tbody>', rows);
const gridTag = `<div id="task-grid" class="task-grid" data-link-label="${esc(copy.templates.taskLink)}">`;
html = html.replace(/<div id="task-grid"[^>]*>/, gridTag);
fillContainer(gridTag, '</div><!-- /task-grid -->', cards);
const faq = readJson('./faq.json');
fillContainer('<ol class="steps" id="faq-entries">', '</ol>', faq.map(({question, answer}) =>
  `<li><div class="step-copy"><h3>${esc(question)}</h3></div><div class="step-body"><p>${esc(answer)}</p></div></li>`));
const faqSchema = {
  '@context': 'https://schema.org', '@type': 'FAQPage', '@id': 'https://acceleratebench.com/#faq',
  mainEntity: faq.map(({question, answer}) => ({
    '@type': 'Question', name: question, acceptedAnswer: {'@type': 'Answer', text: answer}
  }))
};
fillContainer('<script type="application/ld+json" id="faq-schema">', '</script>',
  [JSON.stringify(faqSchema, null, 2).replaceAll('<', '\\u003c')]);
writeFileSync(homepage, html);

const site = 'https://acceleratebench.com';
const dist = new URL('../dist/', import.meta.url);
for (const task of tasks) {
  assert.match(task.directory, /^[a-z0-9-]+$/);
  const path = taskPath(task);
  const directory = new URL(path.slice(1), dist);
  mkdirSync(directory, {recursive: true});
  writeFileSync(new URL('index.html', directory), taskPage(task, models, copy, site));
}
const pageDate = '2026-11-23';
const sitemapEntries = [
  ['/', pageDate], ['/paper.html', pageDate], ['/assets/accelerate-bench.pdf', '2026-11-16'],
  ...tasks.map(task => [taskPath(task), pageDate])
];
writeFileSync(new URL('sitemap.xml', dist), [
  '<?xml version="1.0" encoding="UTF-8"?>',
  '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
  ...sitemapEntries.map(([path, date]) => `  <url><loc>${site}${path}</loc><lastmod>${date}</lastmod></url>`),
  '</urlset>', ''
].join('\n'));
