import {esc, taskMeta, taskPath, taskResults} from '../dist/render.mjs';

export function taskPage(task, models, copy, site) {
  const entry = copy.tasks[task.directory];
  const {templates, labels} = copy;
  const title = templates.title.replace('{name}', task.name);
  const fullDescription = templates.description.replace('{summary}', entry.summary);
  const description = fullDescription.length <= 160
    ? fullDescription : templates.descriptionShort.replace('{summary}', entry.summary);
  const subtitle = templates.subtitle.replace('{area}', task.area);
  const url = site + taskPath(task);
  const schema = {
    '@context': 'https://schema.org',
    '@graph': [
      {'@type': 'WebPage', '@id': url, url, name: title, description,
        isPartOf: {'@id': site + '/#website'}, about: {'@id': site + '/#dataset'},
        breadcrumb: {'@id': url + '#breadcrumb'}},
      {'@type': 'BreadcrumbList', '@id': url + '#breadcrumb', itemListElement: [
        {'@type': 'ListItem', position: 1, name: 'Accelerate Bench', item: site + '/'},
        {'@type': 'ListItem', position: 2, name: task.name, item: url}
      ]}
    ]
  };
  const sections = ['workload', 'correctness', 'timing'].filter(key => entry[key]).map(key =>
    `<div><h2>${esc(labels[key])}</h2><p>${esc(entry[key])}</p></div>`);
  const links = [
    [labels.leaderboard, '/#leaderboard'], [labels.paper, '/paper.html'],
    [labels.dataset, 'https://huggingface.co/datasets/AdAstraAbyssoque/accelerate-bench'],
    [labels.repository, 'https://github.com/AdAstraAbyssoque/accelerate-bench']
  ];
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
<link rel="canonical" href="${esc(url)}">
<link rel="icon" href="/assets/favicon.svg"><link rel="stylesheet" href="/style.css?v=20261123-pages">
<script type="application/ld+json">
${JSON.stringify(schema, null, 2).replaceAll('<', '\\u003c')}
</script></head>
<body><main id="task-details" class="task-page">
<a class="text-link" href="/">← Accelerate Bench</a>
<div class="task-intro"><div><h1>${esc(task.name)}</h1><p class="eyebrow">${esc(subtitle)}</p><p>${esc(entry.summary)}</p></div>
<img src="/${esc(task.diagram)}" alt=""></div>
<div id="parameters">${taskMeta(task)}</div>
<div class="task-contract">${sections.join('\n')}</div>
<section id="task-results">${taskResults(task, models, '/')}</section>
<div class="actions">${links.map(([name, href]) => `<a class="button" href="${href}">${esc(name)}</a>`).join('')}</div>
</main></body></html>
`;
}
