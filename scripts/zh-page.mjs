import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {esc, rankRow, taskPath} from '../dist/render.mjs';

const read = name => readFileSync(new URL(name, import.meta.url), 'utf8');
const messaging = read('./messaging.md');
const ui = Object.fromEntries([...read('./zh-ui-strings.md').matchAll(/^\| ([^|]+?) \| ([^|]+?) \| .+? \|$/gm)]
  .map(([, key, value]) => [key, value]));
const resources = [
  ['Harbor Hub', 'https://hub.harborframework.com/datasets/accelerate-bench/accelerate-bench'],
  ['Hugging Face', 'https://huggingface.co/datasets/AdAstraAbyssoque/accelerate-bench'],
  ['GitHub', 'https://github.com/AdAstraAbyssoque/accelerate-bench']
];

function section(name) {
  const marker = '### ' + name + '\n';
  const parts = messaging.split('\n' + marker);
  assert.equal(parts.length, 2, name);
  return parts[1].split(/\n#{2,3} /)[0].trim();
}

function interpolate(template, fields) {
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    assert.ok(fields[key] != null, key);
    return fields[key];
  });
}

function leaderboard(data) {
  const {tasks, models, selection} = data;
  const fields = {
    table: data.sources.leaderboard.match(/Table (\d+)/)[1],
    version: selection.benchmark_version, agents: models.length, tasks: tasks.length,
    outcomes: tasks.length * models.length, omitted: selection.not_listed.join('、')
  };
  const notes = new Map();
  const rows = [...models].sort((a, b) => b.score - a.score).map((model, index) => {
    if (model.stopped_tasks.length) {
      notes.set(model.name, interpolate(ui.stopped, {
        model: model.name, stopped: model.stopped_tasks.join('、'),
        remaining: tasks.length - model.stopped_tasks.length,
        score: selection.score_on_other_tasks[model.name]
      }));
    }
    return rankRow(model, index, {root: '/', stoppedNote: notes.get(model.name)});
  });
  const caption = esc(interpolate(ui.caption, fields)).replace('Aτ', 'A<sub>τ</sub>');
  return `<section id="leaderboard" aria-labelledby="rank-title"><h2 id="rank-title">${esc(ui.leaderboard)}</h2>
<div class="table-scroll" tabindex="0" role="region" aria-labelledby="rank-title"><table aria-labelledby="rank-title" aria-describedby="rank-note">
<thead><tr>${ui.headers.split('、').map(h => `<th scope="col">${esc(h)}</th>`).join('')}</tr></thead>
<tbody id="rank-rows">${rows.join('\n')}</tbody></table></div>
<p class="caption" id="rank-note">${caption} ${[...notes.values()].map(n => '<sup>†</sup>' + esc(n)).join(' ')}</p></section>`;
}

export function zhPage(data, site) {
  const metadata = section('中文页标题和描述');
  const title = metadata.match(/^- 标题：(.+)$/m)[1];
  const description = metadata.match(/^- 描述：(.+)$/m)[1];
  const pairs = section('常见问题').split(/^#### /m).slice(1).map(item => {
    const [question, answer] = item.trim().split('\n\n');
    return {question, answer};
  });
  assert.equal(pairs.length, 8);
  const url = site + '/zh/';
  const graph = [
    {'@type': 'WebPage', '@id': url, url, name: title, description, inLanguage: 'zh-CN',
      isPartOf: {'@id': site + '/#website'}, about: {'@id': site + '/#dataset'}},
    {'@type': 'FAQPage', '@id': url + '#faq', inLanguage: 'zh-CN', isPartOf: {'@id': url},
      mainEntity: pairs.map(({question, answer}) => ({
        '@type': 'Question', name: question, acceptedAnswer: {'@type': 'Answer', text: answer}
      }))}
  ];
  const findings = section('关键发现').split('\n').map(line => {
    const [, lead, rest] = line.match(/^- \*\*(.+?)\*\*( .+)$/);
    return `<li><strong>${esc(lead)}</strong>${esc(rest)}</li>`;
  });
  const groups = data.areas.map(area => {
    assert.ok(ui[area], area);
    const links = data.tasks.filter(task => task.area === area).map(task =>
      `<li><a href="${taskPath(task)}" lang="en">${esc(task.name)}</a></li>`);
    return `<div><h3>${esc(ui[area])}</h3><ul>${links.join('\n')}</ul></div>`;
  });
  const faq = pairs.map(({question, answer}) => `<li><h3>${esc(question)}</h3><p>${esc(answer)}</p></li>`);
  const links = [[ui.paper, '/paper.html'], ...resources].map(([name, href]) =>
    `<a class="button" href="${esc(href)}">${esc(name)}</a>`);
  return `<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title><meta name="description" content="${esc(description)}">
<link rel="canonical" href="${url}">
<link rel="alternate" hreflang="en" href="${site}/">
<link rel="alternate" hreflang="zh-CN" href="${url}">
<link rel="alternate" hreflang="x-default" href="${site}/">
<link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css?v=20261123-pages"><link rel="stylesheet" href="/zh/style.css">
<script type="application/ld+json">
${JSON.stringify({'@context':'https://schema.org', '@graph':graph}, null, 2).replaceAll('<','\\u003c')}
</script></head><body>
<header><div class="header-inner"><a class="wordmark" href="#top"><img src="/assets/favicon.svg" width="29" height="29" alt=""><span>Accelerate<span class="brand-light"> Bench</span></span></a>
<nav><a href="#faq">常见问题</a><a href="#leaderboard">${esc(ui.leaderboard)}</a><a href="#tasks">${esc(ui.tasks)}</a></nav>
<a class="header-paper" href="/" hreflang="en" lang="en">English</a></div></header>
<main id="top">
<section class="zh-intro"><h1>${esc(title)}</h1>
<p class="zh-summary">${esc(section('一句话介绍'))}</p>
<p>${esc(section('简介'))}</p><div class="actions">${links.join('\n')}</div></section>
<section id="findings"><h2>关键发现</h2><ul class="zh-findings">${findings.join('\n')}</ul></section>
<section id="related"><h2>与相近基准的关系</h2>
${section('与相近基准的关系').split('\n\n').map(p => `<p>${esc(p)}</p>`).join('\n')}</section>
<section id="faq"><h2>常见问题</h2><ol id="faq-entries">${faq.join('\n')}</ol></section>
${leaderboard(data)}
<section id="tasks"><h2>${esc(ui.tasks)}</h2><div id="zh-tasks">${groups.join('\n')}</div></section>
</main></body></html>
`;
}

export function llmsText(data, site) {
  const sections = [
    ['Paper', [[data.title, site + '/paper.html']]],
    ['Leaderboard data', [['results.json', site + '/assets/results.json']]],
    ['Tasks', data.tasks.map(t => [t.name, site + taskPath(t)])],
    ['FAQ', [['FAQ', site + '/#faq']]],
    ['Get started', resources], ['中文', [['中文', site + '/zh/']]]
  ];
  return ['# Accelerate Bench', '> ' + section('One sentence'), section('Short description'),
    ...sections.map(([heading, links]) => '## ' + heading + '\n\n' +
      links.map(([name, href]) => `- [${name}](${href})`).join('\n'))].join('\n\n') + '\n';
}
