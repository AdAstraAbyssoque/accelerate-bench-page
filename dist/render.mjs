export const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const format = (value, key) => key === 'gm' ? `${value.toFixed(2)}×` : `${value.toFixed(1)}%`;

const icons = {
  Claude: 'claude-color', DeepSeek: 'deepseek-color', Hy: 'hunyuan-color', GLM: 'zai',
  Kimi: 'kimi', Grok: 'grok', Gemini: 'gemini-color', GPT: 'openai'
};

export function modelIcon(name) {
  const family = Object.keys(icons).find(prefix => name.startsWith(prefix));
  if (!family) return '<span class="model-icon letter" aria-hidden="true">G</span>';
  return `<img class="model-icon" src="assets/models/${icons[family]}.svg" alt="" width="20" height="20">`;
}

export function modelLabel(name, stopped = []) {
  const note = `The provider's safety system stopped the runs on ${stopped.join(', ')}; they count as failures.`;
  const mark = stopped.length ? `<sup class="model-mark" title="${esc(note)}">†</sup>` : '';
  return `<span class="model-label">${modelIcon(name)}<span>${esc(name)}${mark}</span></span>`;
}

export function rankRow(model, index) {
  const score = `<span class="score-cell" style="--fill:${model.score}%"><strong>${format(model.score, 'score')}</strong></span>`;
  const metrics = ['gm', 'a125', 'a2'].map(key => `<td>${format(model[key], key)}</td>`).join('');
  return `<tr><td>${String(index + 1).padStart(2, '0')}</td><td>${modelLabel(model.name, model.stopped_tasks)}</td><td>${esc(model.harness)}</td><td>${score}</td>${metrics}</tr>`;
}

export function taskCard(task, index) {
  const visual = `<div class="task-card-visual"><span class="task-index">${String(index + 1).padStart(2, '0')}</span><img src="${esc(task.diagram)}" alt="" loading="lazy"></div>`;
  const footer = `<div class="task-card-foot"><span>${task.cpus} CPUs <span aria-hidden="true">·</span> ${task.memory_gib} GiB</span><span class="task-arrow" aria-hidden="true">↗</span></div>`;
  return `<button class="task-card" data-task="${esc(task.id)}" aria-label="View ${esc(task.name)} task">${visual}<div class="task-card-body"><h3>${esc(task.name)}</h3><p>${esc(task.area)}</p>${footer}</div></button>`;
}
