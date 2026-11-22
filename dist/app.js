import {esc, format, modelIcon, modelLabel, rankRow, taskCard} from './render.mjs';
const $ = selector => document.querySelector(selector);
const shortAreas = ['Molecules & materials','Fluids & atmosphere','Transport & astronomy','Bioinformatics','Numerics & graphs','Quantum circuits','Machine learning','Scientific I/O'];
const sortLabels = {score:'Score@1',gm:'GM',a125:'A₁.₂₅',a2:'A₂'};
let data, metric = 'score';
const heroAgents=['Claude Opus 5.5','GPT-6 Astra','DeepSeek-V4-Pro'];
function renderHero() {
 $('#hero-ranks').innerHTML=data.models.filter(m=>heroAgents.includes(m.name)).map(m=>`<div class="hero-rank">${modelIcon(m.name)}<span class="rank-name">${esc(m.name)}</span><strong>${m.score.toFixed(1)}%</strong><div class="mini-track" aria-hidden="true"><div class="mini-fill" style="width:${m.score}%"></div></div></div>`).join('');
}
function renderResults() {
 const rows=[...data.models].sort((a,b)=>b[metric]-a[metric]);
 $('#rank-rows').innerHTML=rows.map(rankRow).join('');
 const max=Math.max(...rows.map(m=>m[metric]));
 $('#leaderboard-chart').innerHTML=rows.map(m=>`<div class="bar-row">${modelLabel(m.name,m.stopped_tasks)}<div class="bar-track" aria-hidden="true"><div class="bar-fill" style="width:${m[metric]/max*100}%"></div></div><span class="bar-value">${format(m[metric],metric)}</span></div>`).join('');
 document.querySelectorAll('[data-sort]').forEach(b=>{const selected=b.dataset.sort===metric;b.parentElement.removeAttribute('aria-sort');if(selected)b.parentElement.setAttribute('aria-sort','descending');b.textContent=sortLabels[b.dataset.sort]+(selected?' ↓':' ↕');});
 $('#metric').value=metric;
}
function renderAreaFilters() {
 const items=[{id:'',label:'All applications',count:data.tasks.length},...data.areas.map((area,id)=>({id:String(id),label:shortAreas[id],title:area,count:data.tasks.filter(t=>t.area_id===id).length}))];
 $('#area-filters').innerHTML=items.map(a=>`<button class="area-button${a.id===$('#task-area').value?' active':''}" data-area="${a.id}" aria-pressed="${a.id===$('#task-area').value}" ${a.title?`title="${esc(a.title)}"`:''}><span>${esc(a.label)}</span><span>${String(a.count).padStart(2,'0')}</span></button>`).join('');
}
function renderTasks() {
 const q=$('#task-search').value.trim().toLowerCase(), area=$('#task-area').value;
 const tasks=data.tasks.filter(t=>(area===''||String(t.area_id)===area)&&`${t.name} ${t.area} ${t.id}`.toLowerCase().includes(q));
 $('#task-count').textContent=`${tasks.length} / ${data.tasks.length} tasks`;
 $('#task-grid').innerHTML=tasks.length?tasks.map(t=>taskCard(t,data.tasks.indexOf(t))).join(''):'<p class="empty">No tasks match this search.<br><button class="button" id="reset-tasks">Reset filters</button></p>';
 renderAreaFilters();
}
function openTask(id) {
 const t=data.tasks.find(x=>x.id===id);if(!t)return;
 $('#task-details').innerHTML=`<p class="eyebrow">${esc(t.area)}</p><h2 id="task-title">${esc(t.name)}</h2><div class="task-meta"><span>Task version<strong>${esc(t.version)}</strong></span><span>CPU budget<strong>${t.cpus} CPUs</strong></span><span>Memory<strong>${t.memory_gib} GiB</strong></span><span>Agent budget<strong>${t.agent_hours} hours</strong></span><span>Harbor Hub<strong>${t.harbor?`<a href="${esc(t.harbor)}">Open task ↗</a>`:'Full release only'}</strong></span></div><img class="task-detail-diagram" src="${esc(t.diagram)}" alt="Illustration of ${esc(t.name)}"><h3>Reported runtime-saving reward</h3><p class="caption">First-run rewards on benchmark v1.1, from the data behind paper Table 1, rounded to one decimal. Failed correctness is distinct from a correct result with zero speedup reward.</p><div class="table-scroll"><table><thead><tr><th scope="col">Agent model</th><th scope="col">Reward</th></tr></thead><tbody>${data.models.map((m,i)=>`<tr><td>${modelLabel(m.name)}</td><td>${(t.stopped_agents||[]).includes(m.name)?'Stopped by the provider’s safety system (scored as a failure)':t.rewards_percent[i]===null?'Failed correctness':t.rewards_percent[i].toFixed(1)+'%'}</td></tr>`).join('')}</tbody></table></div>`;
 $('#task-dialog').showModal();
}
document.querySelectorAll('dialog').forEach(d=>{
 d.querySelector('.close').addEventListener('click',()=>d.close());
 d.addEventListener('click',e=>{if(e.target===d){const r=d.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)d.close();}});
});
document.querySelectorAll('[data-figure]').forEach(b=>b.addEventListener('click',()=>{$('#expanded-figure').src=b.dataset.figure;$('#expanded-figure').alt=b.dataset.caption;$('#figure-caption').textContent=b.dataset.caption;$('#figure-dialog').showModal();}));
document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener('click',()=>{const chart=b.dataset.view==='chart';$('#leaderboard-table').hidden=chart;$('#leaderboard-chart').hidden=!chart;document.querySelectorAll('[data-view]').forEach(x=>{x.classList.toggle('active',x===b);x.setAttribute('aria-pressed',String(x===b));});}));
$('#copy-citation').addEventListener('click',async()=>{try{await navigator.clipboard.writeText($('#bibtex').textContent);$('#copy-status').textContent='BibTeX copied to clipboard.';}catch{const r=document.createRange();r.selectNodeContents($('#bibtex'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(r);$('#copy-status').textContent='Citation selected. Press Ctrl+C or ⌘C to copy.';}});
const navLinks = [...document.querySelectorAll('nav a')];
let navTicking = false;
function updateActiveNavigation() {
 const marker = Math.max(120, window.innerHeight * .3);
 const visibleSection = navLinks.map(a => document.querySelector(a.hash)).filter(s => s.getBoundingClientRect().top <= marker).at(-1);
 navLinks.forEach(a => {const active = visibleSection && a.hash === '#' + visibleSection.id;a.classList.toggle('active',!!active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});
 navTicking = false;
}
window.addEventListener('scroll',()=>{if(!navTicking){navTicking=true;requestAnimationFrame(updateActiveNavigation);}},{passive:true});
window.addEventListener('resize',updateActiveNavigation);
updateActiveNavigation();
async function load() {
 try {
  const r=await fetch('assets/results.json');if(!r.ok)throw new Error(`Results: ${r.status}`);data=await r.json();
  renderHero();renderResults();
  $('#task-area').innerHTML='<option value="">All application areas</option>'+data.areas.map((a,i)=>`<option value="${i}">${esc(a)}</option>`).join('');
  renderTasks();
  $('#task-search').addEventListener('input',renderTasks);$('#task-area').addEventListener('change',renderTasks);
  $('#area-filters').addEventListener('click',e=>{const b=e.target.closest('[data-area]');if(b){$('#task-area').value=b.dataset.area;renderTasks();}});
  $('#task-grid').addEventListener('click',e=>{const b=e.target.closest('[data-task]');if(b)openTask(b.dataset.task);if(e.target.closest('#reset-tasks')){$('#task-search').value='';$('#task-area').value='';renderTasks();$('#task-search').focus();}});
  $('#metric').addEventListener('change',e=>{metric=e.target.value;renderResults();});
  document.querySelectorAll('[data-sort]').forEach(b=>b.addEventListener('click',()=>{metric=b.dataset.sort;renderResults();}));
 } catch(e) {
  $('#task-count').textContent='Interactive results unavailable. Please reload to use the controls.';
  console.error(e);
 }
 try {const r=await fetch('assets/methods.json');if(!r.ok)throw new Error('Methods unavailable');const methods=await r.json();$('#method-gallery').innerHTML=methods.map(m=>`<article><img src="${esc(m.diagram)}" alt="" loading="lazy"><h4>${esc(m.title)}</h4><p>${esc(m.description)}</p></article>`).join('');}catch{$('#method-gallery').textContent='Method illustrations are temporarily unavailable.';}
}
load();
