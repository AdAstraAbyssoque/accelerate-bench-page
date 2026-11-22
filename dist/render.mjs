export const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const format = (value, key) => key === 'gm' ? `${value.toFixed(2)}×` : `${value.toFixed(1)}%`;

const icons = {
  Claude: 'claude-color', DeepSeek: 'deepseek-color', Hy: 'hunyuan-color', GLM: 'zai',
  Kimi: 'kimi', Grok: 'grok', Gemini: 'gemini-color', GPT: 'openai'
};

export function modelIcon(name, root = '') {
  const family = Object.keys(icons).find(prefix => name.startsWith(prefix));
  if (!family) return '<span class="model-icon letter" aria-hidden="true">G</span>';
  return `<img class="model-icon" src="${root}assets/models/${icons[family]}.svg" alt="" width="20" height="20">`;
}

export function modelLabel(name, stopped = [], root = '') {
  const note = `The provider's safety system stopped the runs on ${stopped.join(', ')}; they count as failures.`;
  const mark = stopped.length ? `<sup class="model-mark" title="${esc(note)}">†</sup>` : '';
  return `<span class="model-label">${modelIcon(name, root)}<span>${esc(name)}${mark}</span></span>`;
}

export function rankRow(model, index) {
  const score = `<span class="score-cell" style="--fill:${model.score}%"><strong>${format(model.score, 'score')}</strong></span>`;
  const metrics = ['gm', 'a125', 'a2'].map(key => `<td>${format(model[key], key)}</td>`).join('');
  return `<tr><td>${String(index + 1).padStart(2, '0')}</td><td>${modelLabel(model.name, model.stopped_tasks)}</td><td>${esc(model.harness)}</td><td>${score}</td>${metrics}</tr>`;
}

export function taskCard(task, index, linkLabel) {
  const linkName = esc(linkLabel?.replace('{name}', task.name) ?? task.name);
  const visual = `<div class="task-card-visual"><span class="task-index">${String(index + 1).padStart(2, '0')}</span><img src="${esc(task.diagram)}" alt="" loading="lazy"></div>`;
  const footer = `<div class="task-card-foot"><span>${task.cpus} CPUs <span aria-hidden="true">·</span> ${task.memory_gib} GiB</span><span class="task-arrow" aria-hidden="true">↗</span></div>`;
  return `<div class="task-card-wrap"><button class="task-card" data-task="${esc(task.id)}" aria-label="View ${esc(task.name)} task">${visual}<div class="task-card-body"><h3>${esc(task.name)}</h3><p>${esc(task.area)}</p>${footer}</div></button><a class="task-permalink" href="${taskPath(task)}" aria-label="${linkName}" title="${linkName}">↗</a></div>`;
}

export function taskPath(task) {
  return `/tasks/${encodeURIComponent(task.directory)}/`;
}

export function taskMeta(t) {
  return `<div class="task-meta"><span>Task version<strong>${esc(t.version)}</strong></span><span>CPU budget<strong>${t.cpus} CPUs</strong></span><span>Memory<strong>${t.memory_gib} GiB</strong></span><span>Agent budget<strong>${t.agent_hours} hours</strong></span><span>Harbor Hub<strong>${t.harbor?`<a href="${esc(t.harbor)}">Open task ↗</a>`:'Full release only'}</strong></span></div>`;
}

export function taskResults(task, models, root = '') {
  const rows = models.map((model, index) => {
    const reward = task.rewards_percent[index];
    let result = reward === null ? 'Failed correctness' : format(reward, 'score');
    if (task.stopped_agents?.includes(model.name)) {
      result = 'Stopped by the provider’s safety system (scored as a failure)';
    }
    return `<tr><td>${modelLabel(model.name, [], root)}</td><td>${result}</td></tr>`;
  });
  return `<h3>Reported runtime-saving reward</h3><p class="caption">First-run rewards on benchmark v1.1, from the data behind paper Table 1, rounded to one decimal. Failed correctness is distinct from a correct result with zero speedup reward.</p><div class="table-scroll"><table><thead><tr><th scope="col">Agent model</th><th scope="col">Reward</th></tr></thead><tbody>${rows.join('\n')}</tbody></table></div>`;
}
