'use strict';
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const format = (v, metric) => metric === 'gm' ? `${v.toFixed(2)}×` : `${v.toFixed(1)}%`;
let data, metric = 'score';
function renderResults() {
 const rows = [...data.models].sort((a,b) => b[metric]-a[metric]);
 $('#rank-rows').innerHTML = rows.map((m,i) => `<tr><td>${i+1}</td><td>${esc(m.name)}</td><td>${esc(m.effort)}</td>${['score','gm','a125','a2'].map(k=>`<td>${format(m[k],k)}</td>`).join('')}</tr>`).join('');
 const max = Math.max(...rows.map(m=>m[metric]));
 $('#leaderboard-chart').innerHTML = rows.map(m=>`<div class="bar-row"><span>${esc(m.name)}</span><div class="bar-track"><div class="bar-fill" style="width:${m[metric]/max*100}%"></div></div><span class="bar-value">${format(m[metric],metric)}</span></div>`).join('');
 document.querySelectorAll('[data-sort]').forEach(b=>{b.parentElement.removeAttribute('aria-sort'); if(b.dataset.sort===metric)b.parentElement.setAttribute('aria-sort','descending');});
 $('#metric').value=metric;
}
function renderTasks() {
 const q=$('#task-search').value.trim().toLowerCase(), area=$('#task-area').value;
 const tasks=data.tasks.filter(t=>(area==='' || String(t.area_id)===area) && `${t.name} ${t.area} ${t.id}`.toLowerCase().includes(q));
 $('#task-count').textContent=`${tasks.length} of ${data.tasks.length} tasks`;
 $('#task-grid').innerHTML=tasks.length?tasks.map(t=>`<button class="task-card" data-task="${esc(t.id)}" aria-label="View ${esc(t.name)} task"><img src="${esc(t.diagram)}" alt="" loading="lazy"><h3>${esc(t.name)}</h3><p>${esc(t.area)}</p><span>${t.cpus} CPUs · ${t.memory_gib} GiB <span aria-hidden="true">↗</span></span></button>`).join(''):'<p class="empty">No tasks match. Try another name or application area.</p>';
}
function openTask(id) {
 const t=data.tasks.find(x=>x.id===id);if(!t)return;
 $('#task-details').innerHTML=`<p class="eyebrow">${esc(t.area)}</p><h2 id="task-title">${esc(t.name)}</h2><div class="task-meta"><span>Task version<strong>${esc(t.version)}</strong></span><span>CPU budget<strong>${t.cpus} CPUs</strong></span><span>Memory<strong>${t.memory_gib} GiB</strong></span><span>Agent budget<strong>${t.agent_hours} hours</strong></span></div><img class="task-detail-diagram" src="${esc(t.diagram)}" alt="Illustration of ${esc(t.name)}"><h3>Reported runtime-saving reward</h3><p class="caption">Published rounded per-task values from the paper appendix. Failed correctness is distinct from a correct result with zero speedup reward.</p><div class="table-scroll"><table><thead><tr><th scope="col">Agent model</th><th scope="col">Reward</th></tr></thead><tbody>${data.models.map((m,i)=>`<tr><td>${esc(m.name)}</td><td>${t.rewards_percent[i]===null?'Failed correctness':t.rewards_percent[i].toFixed(0)+'%'}</td></tr>`).join('')}</tbody></table></div>`;
 $('#task-dialog').showModal();
}
document.querySelectorAll('dialog').forEach(d=>{
 d.querySelector('.close').addEventListener('click',()=>d.close());
 d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});
});
document.querySelectorAll('[data-figure]').forEach(b=>b.addEventListener('click',()=>{$('#expanded-figure').src=b.dataset.figure;$('#expanded-figure').alt=b.dataset.caption;$('#figure-caption').textContent=b.dataset.caption;$('#figure-dialog').showModal();}));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{const chart=b.dataset.view==='chart';$('#leaderboard-table').hidden=chart;$('#leaderboard-chart').hidden=!chart;document.querySelectorAll('[data-view]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});}));
$('#copy-citation').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('#bibtex').textContent);$('#copy-status').textContent='BibTeX copied.';}catch{const r=document.createRange();r.selectNodeContents($('#bibtex'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(r);$('#copy-status').textContent='Citation selected. Press Ctrl+C or ⌘C to copy.';}});
async function load() {
 try {
  const r=await fetch('assets/results.json');if(!r.ok)throw new Error(`Results: ${r.status}`);data=await r.json();
  renderResults();
  $('#task-area').innerHTML='<option value="">All application areas</option>'+data.areas.map((a,i)=>`<option value="${i}">${esc(a)}</option>`).join('');
  renderTasks();
  $('#task-search').addEventListener('input',renderTasks);$('#task-area').addEventListener('change',renderTasks);
  $('#task-grid').addEventListener('click',e=>{const b=e.target.closest('[data-task]');if(b)openTask(b.dataset.task);});
  $('#metric').addEventListener('change',e=>{metric=e.target.value;renderResults();});
  document.querySelectorAll('[data-sort]').forEach(b=>b.addEventListener('click',()=>{metric=b.dataset.sort;renderResults();}));
  $('#author-list').innerHTML=data.authors.map(a=>`<span>${esc(a.name)}<sup>${a.affiliations.join(',')}${a.role==='Project Lead'?'‡':a.role==='Corresponding author'?'†':''}</sup></span>`).join('');
  $('#affiliations').innerHTML=data.institutions.map(i=>`<li>${esc(i)}</li>`).join('');
 } catch(e) {
  $('#task-grid').innerHTML='<p class="empty" role="alert">Results could not load. Please reload, or read the linked paper.</p>';
  $('#rank-rows').innerHTML='<tr><td colspan="7">Results could not load. The PDF remains available above.</td></tr>';console.error(e);
 }
 try {const r=await fetch('assets/methods.json');if(!r.ok)throw new Error('Methods unavailable');const methods=await r.json();$('#method-gallery').innerHTML=methods.map(m=>`<article><img src="${esc(m.diagram)}" alt="" loading="lazy"><h4>${esc(m.title)}</h4><p>${esc(m.description)}</p></article>`).join('');}catch{$('#method-gallery').textContent='Method illustrations are temporarily unavailable.';}
}
load();
