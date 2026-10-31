'use strict';
(() => {
const data = window.RE_RL_DATA;
const $ = (s) => document.querySelector(s);
const families = {
  all: {name:'Все направления'},
  math: {name:'Математика и логика', short:'Математика', text:'От алгебры и комбинаторики до логического вывода и трасс алгоритмов. Разные способы учить модель удерживать состояние и связывать шаги.', tags:['Алгебра','Дискретная математика','Логика','Алгоритмы'], color:'#d4e7bc'},
  physics: {name:'Физика', short:'Физика', text:'Механика, электричество, термодинамика, оптика и другие разделы. Задачи связывают численные данные с законами и физическими моделями.', tags:['Механика','Электричество','Оптика','Термодинамика'], color:'#e8cfad'},
  ml: {name:'Машинное обучение', short:'ML', text:'Функции потерь, метрики, обновление параметров и вероятностные модели. Исследуйте вычисления, стоящие за машинным обучением.', tags:['Метрики','Оптимизация','Классификация','Вероятности'], color:'#c8d6ee'},
  rl: {name:'Обучение с подкреплением', short:'RL', text:'Отдача, уравнения Беллмана и обновления ценности. Примеры вычислений, которые связывают награды, действия и будущие состояния.', tags:['Q-learning','SARSA','Bellman','Returns'], color:'#e2cfe5'},
  visual: {name:'Визуальное мышление', short:'VLM', text:'Условие, часть которого находится на изображении. Читайте графики, прослеживайте пути и решайте пространственные головоломки.', tags:['Графы','Диаграммы','Головоломки','Геометрия'], color:'#d6eaa7'},
  formal: {name:'Формальная математика', short:'Lean 4', text:'Отдельный генератор для формальной математики в Lean 4. Познакомьтесь с условиями и структурой примеров в каталоге.', tags:['Lean 4','Формализация'], color:'#cde1d8'}
};
const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const number = n => Number(n).toLocaleString('ru-RU');
const taskNoun = n => n % 100 >= 11 && n % 100 <= 14 ? 'типов задач' : n % 10 === 1 ? 'тип задач' : n % 10 >= 2 && n % 10 <= 4 ? 'типа задач' : 'типов задач';
$('#count-all').textContent = number(data.tasks.length);
$('#count-visual').textContent = data.provenance.visual;
let filter = 'all', page = 1, activeDomain = 'math', gallery = 'graphs', variant = 0, revealed = 0, currentSample;
const pageSize = 12;
const featured = new Set(data.provenance.featured);
const samplesByTask = new Map(data.provenance.featured.map(id => [id, data.samples.filter(s => s.id === id)]));
const taskMap = new Map(data.tasks.map(task => [task.id, task]));
let recordFormat='sft', dialogTaskId='', dialogVariant=0, dialogLanguage='ru', dialogLevel=3;
const svgNS = 'http://www.w3.org/2000/svg';
function svgEl(name, attrs={}, text) { const el = document.createElementNS(svgNS,name); Object.entries(attrs).forEach(([k,v]) => el.setAttribute(k,v)); if(text!==undefined)el.textContent=text; return el; }
function heroGraph(){
 const svg=$('#hero-graph');
 const defs=svgEl('defs'); const pattern=svgEl('pattern',{id:'dotgrid',width:22,height:22,patternUnits:'userSpaceOnUse'}); pattern.append(svgEl('circle',{cx:1,cy:1,r:.65,fill:'#a8b99a',opacity:.65})); defs.append(pattern);svg.append(defs,svgEl('rect',{width:580,height:440,fill:'url(#dotgrid)'}));
 const nodes=[{x:70,y:215,r:29,label:'INPUT',i:'x'},{x:200,y:107,r:25,label:'STATE 01',i:'01'},{x:220,y:300,r:25,label:'STATE 02',i:'02'},{x:340,y:185,r:33,label:'REASONING',i:'ƒ'},{x:430,y:80,r:20,label:'CHECK',i:'✓'},{x:490,y:280,r:40,label:'ANSWER',i:'y'}];
 const links=[[0,1],[0,2],[1,3],[2,3],[1,4],[3,4],[3,5],[4,5]];
 links.forEach(([a,b],i)=>{let x=nodes[a],y=nodes[b];svg.append(svgEl('path',{d:`M${x.x} ${x.y} Q${(x.x+y.x)/2} ${x.y-20} ${y.x} ${y.y}`,fill:'none',stroke:'#8fa581','stroke-width':1,'class':'graph-line'})); const dot=svgEl('circle',{r:3,fill:'#659639',class:'flow-dot'});const motion=svgEl('animateMotion',{dur:`${4+i*.5}s`,repeatCount:'indefinite',path:`M${x.x} ${x.y} Q${(x.x+y.x)/2} ${x.y-20} ${y.x} ${y.y}`});if(!matchMedia('(prefers-reduced-motion: reduce)').matches)dot.append(motion);svg.append(dot);});
 nodes.forEach((n,i)=>{const g=svgEl('g');if(i===3||i===5)g.append(svgEl('circle',{cx:n.x,cy:n.y,r:n.r+13,fill:'none',stroke:'#b4ca9e','stroke-width':1}));g.append(svgEl('circle',{cx:n.x,cy:n.y,r:n.r,fill:i===5?'#163f30':i===3?'#d5edb0':'#f5f4ed',stroke:i===5?'#163f30':'#8ca878','stroke-width':1.4}));g.append(svgEl('text',{x:n.x,y:n.y+6,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':i===3?27:17,fill:i===5?'#d2f97e':'#2c513a'},n.i));g.append(svgEl('text',{x:n.x,y:n.y+n.r+29,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':8,'letter-spacing':1.5,fill:'#61765b'},n.label));svg.append(g);});
 svg.append(svgEl('text',{x:58,y:393,'font-family':'IBM Plex Mono,monospace','font-size':9,fill:'#789168'},'01 / OBSERVE     02 / REASON     03 / VERIFY'));
}
function atlasGraph(){
 const svg=$('#atlas-graph'); svg.replaceChildren();
 const center={x:335,y:240};
 const points=[['math',170,123],['physics',498,120],['ml',558,284],['rl',425,385],['visual',194,381],['formal',95,258]];
 svg.append(svgEl('circle',{cx:center.x,cy:center.y,r:143,fill:'none',stroke:'#c2ceb7','stroke-dasharray':'3 9'}));
 points.forEach(([id,x,y])=>svg.append(svgEl('line',{x1:center.x,y1:center.y,x2:x,y2:y,stroke:activeDomain===id?'#6b974e':'#bac8b2','stroke-width':activeDomain===id?2:1})));
 svg.append(svgEl('circle',{cx:center.x,cy:center.y,r:52,fill:'#163f30'}),svgEl('text',{x:center.x,y:center.y+7,'text-anchor':'middle','font-family':'Golos Text,Arial','font-size':25,'font-weight':600,fill:'#e9f4d7'},'re-rl'),svgEl('text',{x:center.x,y:center.y+76,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':9,fill:'#67805b'},`${data.tasks.length} TASK TYPES`));
 points.forEach(([id,x,y])=>{let n=data.counts[id],r=25+Math.sqrt(n)*1.1;const g=svgEl('g',{class:'atlas-node',role:'button',tabindex:0,'aria-label':`${families[id].name}: ${n} типов`,'aria-pressed':activeDomain===id});g.append(svgEl('circle',{cx:x,cy:y,r:r+6,fill:activeDomain===id?'#e0ebd3':'transparent',stroke:activeDomain===id?'#679149':'transparent'}),svgEl('circle',{cx:x,cy:y,r,fill:families[id].color,stroke:'#9fb98f'}),svgEl('text',{x,y:y+5,'text-anchor':'middle','font-family':'IBM Plex Mono,monospace','font-size':18,fill:'#24412e'},n),svgEl('text',{x,y:y+r+23,'text-anchor':'middle','font-family':'Golos Text,Arial','font-size':12,fill:'#304b35'},families[id].short)); const action=()=>{activeDomain=id;renderDomain();atlasGraph();};g.addEventListener('click',action);g.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();action(); const next=[...svg.querySelectorAll('[role=button]')][points.findIndex(p=>p[0]===id)];next?.focus();}});svg.append(g);});
}
function renderDomain(){const f=families[activeDomain];$('#domain-detail').innerHTML=`<div class="mono small muted">DIRECTION / ${activeDomain.toUpperCase()}</div><div class="domain-count">${data.counts[activeDomain]}</div><h3>${f.name}</h3><p>${f.text}</p><div class="domain-tags">${f.tags.map(t=>`<span>${t}</span>`).join('')}</div><a href="#catalog" class="text-link" id="explore-domain">Исследовать задачи <span>→</span></a>`;$('#explore-domain').addEventListener('click',()=>{filter=activeDomain;page=1;$('#search').value='';$('#kind').value='all';$('#topic').value='all';$('#with-samples').checked=false;renderFilters();renderCatalog();});}
function renderFilters(){ $('#filters').innerHTML=Object.entries(families).map(([key,f])=>`<button data-filter="${key}" class="${filter===key?'active':''}" aria-pressed="${filter===key}">${f.short||f.name} <span>${key==='all'?data.tasks.length:data.counts[key]}</span></button>`).join('');$('#filters').querySelectorAll('button').forEach(button=>button.addEventListener('click',()=>{filter=button.dataset.filter;page=1;renderFilters();renderCatalog();})); }
function renderCatalog(){
 const q=$('#search').value.toLowerCase().trim(),kind=$('#kind').value,topic=$('#topic').value,onlySamples=$('#with-samples').checked,order=$('#sort').value;
 const tasks=data.tasks.filter(t=>(filter==='all'||t.family===filter)&&(kind==='all'||t.kind===kind)&&(topic==='all'||t.domain===topic)&&(!onlySamples||featured.has(t.id))&&(!q||`${t.id} ${t.title||''} ${t.skill||''} ${t.summary} ${t.domain} ${t.example}`.toLowerCase().includes(q)));
 tasks.sort((a,b)=>order==='guided'?(Number(featured.has(b.id))-Number(featured.has(a.id))||a.id.localeCompare(b.id)):order==='domain'?(a.domain.localeCompare(b.domain,'ru')||a.id.localeCompare(b.id)):(a.title||a.id).localeCompare(b.title||b.id,'ru'));
 const pages=Math.max(1,Math.ceil(tasks.length/pageSize));page=Math.min(page,pages);
 $('#catalog-count').textContent=`${number(tasks.length)} ${taskNoun(tasks.length)}${q?' по вашему запросу':''}`;
 $('#task-grid').innerHTML=tasks.slice((page-1)*pageSize,page*pageSize).map(t=>`<button class="task-card" data-task="${escape(t.id)}"><span class="card-top"><span>${escape(t.domain)}</span><span>${t.kind==='visual'?'◉ VLM':'↳ TEXT'}</span></span><h3>${escape(t.title||t.id)}</h3>${t.title?`<span class="task-id mono">${escape(t.id)}</span>`:''}<p>${escape(t.skill||t.summary || 'Условие, решение и эталонный ответ.')}</p><span class="card-bottom"><span>${featured.has(t.id)?'● 60 примеров с решением':`${t.subtypes.length} подтипов`}</span><span>Открыть ↗</span></span></button>`).join('') || '<div class="empty">Ничего не найдено. Попробуйте другой запрос или направление.</div>';
 $('#task-grid').querySelectorAll('[data-task]').forEach(b=>b.addEventListener('click',()=>openTask(b.dataset.task)));
 $('#prev-page').disabled=page===1;$('#next-page').disabled=page===pages;$('#page-label').textContent=`${String(page).padStart(2,'0')} / ${String(pages).padStart(2,'0')}`;
}
let returnFocus;
function openTask(id){
 if(!taskMap.has(id))return;
 dialogTaskId=id;dialogVariant=0;dialogLanguage='ru';dialogLevel=3;
 returnFocus=document.activeElement; renderDialog();
 if(!$('#task-dialog').open)$('#task-dialog').showModal();
 const url=new URL(location.href);url.searchParams.set('task',id);history.replaceState(null,'',url);
}
function renderDialog(){
 const task=taskMap.get(dialogTaskId), bank=samplesByTask.get(dialogTaskId),rich=!!bank;
 const sample=bank?.find(s=>s.language===dialogLanguage&&s.difficulty===dialogLevel&&s.variant===dialogVariant);
 const steps=sample?.steps||task.steps, image=sample?.image||task.image;
 const related=data.tasks.filter(t=>t.id!==task.id&&t.family===task.family&&featured.has(t.id)).slice(0,3);
 $('#dialog-content').innerHTML=`<div class="dialog-meta">${escape(task.domain)} / ${task.kind==='visual'?'VLM':'TEXT'}</div><h2 id="dialog-title">${escape(task.title||task.id)}</h2><div class="mono small muted">${escape(task.id)}</div><p>${escape(task.explanation||task.summary)}</p>${task.skill?`<div class="skill-callout"><span class="mono small">НАВЫК</span><strong>${escape(task.skill)}</strong></div>`:''}
 ${rich?`<div class="dialog-selectors"><label>Уровень<select id="dialog-level">${Array.from({length:10},(_,i)=>`<option value="${i+1}" ${dialogLevel===i+1?'selected':''}>${i+1} / 10</option>`).join('')}</select></label><label>Язык<select id="dialog-language"><option value="ru" ${dialogLanguage==='ru'?'selected':''}>Русский</option><option value="en" ${dialogLanguage==='en'?'selected':''}>English</option></select></label><button class="button outline" id="dialog-variant">Пример ${dialogVariant+1} / 3 ↻</button></div>`:'<p class="snapshot-note">Пример из каталога. Другие варианты и уровни доступны в Python-библиотеке.</p>'}
 ${image?`<img src="${image}" alt="Изображение к задаче ${escape(task.title||task.id)}">`:''}<span class="tag">УСЛОВИЕ${sample?.subtype?' / '+escape(sample.subtype):''}</span><p>${escape(sample?.prompt||task.example)}</p><details><summary>Показать ${steps?'решение и ':''}ответ</summary>${steps?`<ol>${steps.map(step=>`<li>${escape(step)}</li>`).join('')}</ol>`:''}<p><strong>Ответ: ${escape(sample?.answer||task.answer)}</strong></p></details>
 ${rich?'<div class="dialog-actions"><button class="button primary" id="dialog-to-lab">Исследовать в лаборатории →</button><button class="subtle" id="dialog-download">Скачать пример JSON ↓</button></div>':''}<div class="dialog-meta">Подтипы: ${escape(task.subtypes.join(' · '))||'не перечислены в реестре'}</div>
 <details><summary>Как получить такую задачу в Python</summary><pre class="python-snippet">${escape(`from re_rl.tasks.${task.kind==='visual'?'visual.':''}generators import ALL_${task.kind==='visual'?'VISUAL_':''}TASK_GENERATORS\n\ntask = ALL_${task.kind==='visual'?'VISUAL_':''}TASK_GENERATORS["${task.id}"](\n    language="${sample?.language||'ru'}", difficulty=${sample?.difficulty||3}\n)\nprint(task.description)\nprint(task.solution_steps)\nprint(task.final_answer)`)}</pre><p class="small muted">Повторный запуск генерирует новый случайный экземпляр.</p></details>
 ${related.length?`<div class="related-tasks"><p class="mono small">ЕЩЁ В ЭТОМ НАПРАВЛЕНИИ</p>${related.map(t=>`<button class="subtle" data-related="${t.id}">${escape(t.title)} ↗</button>`).join('')}</div>`:''}`;
 $('#task-dialog').setAttribute('aria-labelledby','dialog-title');
 if(rich){
 $('#dialog-level').addEventListener('change',e=>{dialogLevel=+e.target.value;renderDialog();$('#dialog-level').focus();});
 $('#dialog-language').addEventListener('change',e=>{dialogLanguage=e.target.value;renderDialog();$('#dialog-language').focus();});
 $('#dialog-variant').addEventListener('click',()=>{dialogVariant=(dialogVariant+1)%data.provenance.variants;renderDialog();$('#dialog-variant').focus();});
 $('#dialog-to-lab').addEventListener('click',()=>{closeDialog();chooseLab(task.id,dialogLevel,dialogLanguage,dialogVariant);});
 $('#dialog-download').addEventListener('click',()=>downloadSample(sample));
 }
 document.querySelectorAll('[data-related]').forEach(b=>b.addEventListener('click',()=>{openTask(b.dataset.related);$('#task-dialog').scrollTop=0;}));
}
function closeDialog(){ $('#task-dialog').close(); }
$('#close-dialog').addEventListener('click',closeDialog);
$('#task-dialog').addEventListener('click',e=>{if(e.target===$('#task-dialog')){const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)closeDialog();}});
$('#task-dialog').addEventListener('close',()=>{returnFocus?.focus();const url=new URL(location.href);url.searchParams.delete('task');history.replaceState(null,'',url);});
function selectSample(){
 const id=$('#lab-task').value,language=$('#language').value,difficulty=+$('#difficulty').value;
 currentSample=samplesByTask.get(id).find(s=>s.id===id&&s.language===language&&s.difficulty===difficulty&&s.variant===variant);
 revealed=0;$('#difficulty-value').textContent=`${difficulty} / 10`;
 $('#sample-meta').textContent=`L${String(difficulty).padStart(2,'0')} · ${language.toUpperCase()} · #${variant+1}`;
 $('#sample-prompt').textContent=currentSample.prompt;
 const task=taskMap.get(id);$('#sample-skill').innerHTML=`<span class="mono small">ЧЕМУ УЧИТ ЭТА ЗАДАЧА</span><h3>${escape(task.skill)}</h3><p>${escape(task.explanation)}</p>`;
 $('#sample-image').hidden=!currentSample.image;
 if(currentSample.image)$('#sample-image').src=currentSample.image;else $('#sample-image').removeAttribute('src');
 $('#compare-panel').hidden=true;$('#compare-levels').setAttribute('aria-expanded','false');renderTrace();renderRecord();
}
function renderTrace(){
 const steps=currentSample.steps;
 $('#trace-list').innerHTML=revealed?steps.slice(0,revealed).map((s,i)=>`<li data-index="${String(i+1).padStart(2,'0')}">${escape(s)}</li>`).join(''):'<li class="trace-placeholder">Раскройте первый шаг, чтобы начать исследование →</li>';
 $('#step-count').textContent=`${revealed} / ${steps.length} шагов`;
 $('#next-step').disabled=revealed===steps.length;$('#all-steps').disabled=revealed===steps.length;$('#reset-steps').disabled=revealed===0;
 $('#sample-answer').hidden=revealed<steps.length;
 $('#sample-answer').textContent=`✓ ${currentSample.language==='ru'?'Ответ':'Answer'}: ${currentSample.answer}`;
}
$('#next-step').addEventListener('click',()=>{revealed=Math.min(revealed+1,currentSample.steps.length);renderTrace();$('#trace-list').scrollTop=$('#trace-list').scrollHeight;});
$('#all-steps').addEventListener('click',()=>{revealed=currentSample.steps.length;renderTrace();});
$('#reset-steps').addEventListener('click',()=>{revealed=0;renderTrace();});
['#lab-task','#language','#difficulty'].forEach(s=>$(s).addEventListener(s==='#difficulty'?'input':'change',selectSample));
$('#new-sample').addEventListener('click',()=>{variant=(variant+1)%data.provenance.variants;selectSample();});
function downloadSample(sample){const blob=new Blob([JSON.stringify(sample,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`re-rl-${sample.id}-${sample.language}-L${sample.difficulty}.json`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
$('#download-sample').addEventListener('click',()=>downloadSample(currentSample));
$('#compare-levels').addEventListener('click',()=>{
 const panel=$('#compare-panel');panel.hidden=!panel.hidden;$('#compare-levels').setAttribute('aria-expanded',String(!panel.hidden));if(panel.hidden)return;
 panel.innerHTML=`<p class="comparison-note">Два сохранённых примера одного генератора. Числа и подтип могут отличаться. Уровни не означают одинаковую сложность между разными задачами.</p><div class="comparison-grid">${[2,9].map(level=>{const sample=samplesByTask.get(currentSample.id).find(s=>s.language===currentSample.language&&s.difficulty===level&&s.variant===variant);return `<article><span class="mono small">УРОВЕНЬ ${level} / 10 · ${sample.steps.length} ШАГОВ</span>${sample.image?`<img src="${sample.image}" alt="Пример уровня ${level}">`:''}<p>${escape(sample.prompt)}</p><details><summary>Решение и ответ</summary><ol>${sample.steps.map(step=>`<li>${escape(step)}</li>`).join('')}</ol><strong>${escape(sample.answer)}</strong></details></article>`;}).join('')}</div>`;
});
const galleries={graphs:['shortest_path_image','boolean_circuit_image','circuit_resistance_image'],logic:['minesweeper_image','queens_check_image','arrow_turn'],charts:['function_plot_read','bar_chart_read','pv_cycle_image']};
function renderGallery(){
 const aliases={circuit_resistance:['circuit_resistance','circuit_resistance_image'],minesweeper_image:['minesweeper_image','minesweeper'],queens_check:['queens_check','queens_check_image','queens_image'],pv_cycle_image:['pv_cycle_image','pv_cycle']};
 const chosen=galleries[gallery].map(id=>data.tasks.find(t=>t.id===id)||data.tasks.find(t=>aliases[id]?.includes(t.id))).filter(Boolean);
 // Fall back by family keywords only if the source registry renamed an ID.
 const missing=3-chosen.length; if(missing>0){const used=new Set(chosen.map(t=>t.id));chosen.push(...data.tasks.filter(t=>t.kind==='visual'&&!used.has(t.id)).slice(0,missing));}
 $('#visual-gallery').innerHTML=chosen.map(t=>`<button class="visual-card" data-task="${escape(t.id)}"><div class="image-wrap"><img loading="lazy" src="${t.image}" alt="Пример визуального генератора ${escape(t.id)}" width="360" height="200"></div><div class="visual-caption"><span><b>${escape(t.id)}</b><small>Изображение + условие + решение</small></span><span>↗</span></div></button>`).join('');
 $('#visual-gallery').querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>openTask(b.dataset.task)));
 document.querySelectorAll('[data-gallery]').forEach(b=>{b.classList.toggle('active',b.dataset.gallery===gallery);b.setAttribute('aria-pressed',b.dataset.gallery===gallery);});
}
document.querySelectorAll('[data-gallery]').forEach(b=>b.addEventListener('click',()=>{gallery=b.dataset.gallery;renderGallery();}));
['#topic','#sort','#with-samples'].forEach(selector=>$(selector).addEventListener('change',()=>{page=1;renderCatalog();}));
$('#reset-filters').addEventListener('click',()=>{filter='all';page=1;$('#topic').value='all';$('#kind').value='all';$('#sort').value='guided';$('#search').value='';$('#with-samples').checked=false;renderFilters();renderCatalog();});
$('#search').addEventListener('input',()=>{page=1;renderCatalog();});$('#kind').addEventListener('change',()=>{page=1;renderCatalog();});
function turnPage(delta){page+=delta;renderCatalog();$('#catalog').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
$('#prev-page').addEventListener('click',()=>turnPage(-1));$('#next-page').addEventListener('click',()=>turnPage(1));
document.addEventListener('keydown',e=>{if(e.key==='/'&&!$('#task-dialog').open&&!['INPUT','SELECT','TEXTAREA'].includes(document.activeElement.tagName)){e.preventDefault();$('#search').focus();$('#catalog').scrollIntoView();}});
$('.menu').addEventListener('click',()=>{const open=$('.header nav').classList.toggle('open');$('.menu').setAttribute('aria-expanded',open);});
$('.header nav').querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{$('.header nav').classList.remove('open');$('.menu').setAttribute('aria-expanded','false');}));
const routes=[
 {symbol:'⊢',title:'Делать логические выводы',text:'Факты → правила → новые знания',ids:['horn_fire','gate_fold','hamming_code']},
 {symbol:'⌘',title:'Следить за алгоритмом',text:'Состояние → операция → результат',ids:['union_find','page_replacement','binary_search','stable_matching','min_coins','matrix_chain']},
 {symbol:'∂',title:'Моделировать физику',text:'Величины → закон → вычисление',ids:['ballistic_pendulum','resistor_pair','wave_relation','half_life_steps','euler_method']},
 {symbol:'∇',title:'Разбирать обучение ML',text:'Данные → метрика → обновление',ids:['perceptron_update','gini_split','shannon_entropy']},
 {symbol:'↺',title:'Оценивать решения агента',text:'Награда → будущее → ценность',ids:['q_learning','sarsa','bellman_backup','discounted_return','gae_advantage']},
 {symbol:'◈',title:'Рассуждать по изображению',text:'Рисунок → наблюдение → ответ',ids:['shortest_path_image','boolean_circuit_image','bar_chart_read','arrow_turn']}
];
function chooseLab(id,level=5,language='ru',sampleVariant=0){$('#lab-task').value=id;$('#difficulty').value=level;$('#language').value=language;variant=sampleVariant;selectSample();$('#lab').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});}
function setupLearning(){
 $('#learning-routes').innerHTML=routes.map((route,index)=>`<article class="learning-route"><span class="route-symbol">${route.symbol}</span><span class="mono small muted">0${index+1} / REASONING SKILL</span><h3>${route.title}</h3><p>${route.text}</p><div>${route.ids.map(id=>`<button data-route-task="${id}">${escape(taskMap.get(id).title)} <span>↗</span></button>`).join('')}</div></article>`).join('');
 document.querySelectorAll('[data-route-task]').forEach(b=>b.addEventListener('click',()=>chooseLab(b.dataset.routeTask)));
 $('#lab-task').innerHTML=['math','physics','ml','rl','visual'].map(family=>`<optgroup label="${families[family].name}">${data.tasks.filter(t=>featured.has(t.id)&&t.family===family).map(t=>`<option value="${t.id}">${escape(t.title)}</option>`).join('')}</optgroup>`).join('');$('#lab-task').value='horn_fire';
 $('#topic').innerHTML='<option value="all">Все разделы</option>'+[...new Set(data.tasks.map(t=>t.domain))].sort((a,b)=>a.localeCompare(b,'ru')).map(topic=>`<option value="${escape(topic)}">${escape(topic)}</option>`).join('');
}
function trainingRecord(){const s=currentSample,answer=s.steps.join('\n');
 if(recordFormat==='chat')return {...(s.image?{image:s.image}:{}),messages:[{role:'user',content:s.prompt},{role:'assistant',content:answer}],metadata:{task_type:s.id,difficulty:s.difficulty,language:s.language}};
 if(recordFormat==='grpo')return {...(s.image?{image:s.image}:{}),question:s.prompt,answer:s.answer,metadata:{task_type:s.id,difficulty:s.difficulty,language:s.language}};
 return {instruction:s.language==='ru'?'Решите задачу пошагово.':'Solve the problem step by step.',...(s.image?{image:s.image}:{}),input:s.prompt,output:answer,metadata:{task_type:s.id,difficulty:s.difficulty,language:s.language}};
}
function renderRecord(){ $('#record-json').textContent=JSON.stringify(trainingRecord(),null,2);$('#record-source').textContent=`${taskMap.get(currentSample.id).title} · ${currentSample.language.toUpperCase()} · уровень ${currentSample.difficulty}`;document.querySelectorAll('[data-format]').forEach(b=>{b.classList.toggle('active',b.dataset.format===recordFormat);b.setAttribute('aria-pressed',String(b.dataset.format===recordFormat));}); }
document.querySelectorAll('[data-format]').forEach(b=>b.addEventListener('click',()=>{recordFormat=b.dataset.format;renderRecord();}));
$('#copy-record').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(JSON.stringify(trainingRecord(),null,2));toast('JSON скопирован');}catch{toast('Выделите текст записи и скопируйте его вручную.');}});
const quickstart=`from re_rl.dataset_generator import DatasetGenerator\n\ngenerator = DatasetGenerator()\ndata = generator.generate_sft_dataset(\n    task_types=["horn_fire", "q_learning"],\n    num_samples=1000,\n    language="ru",\n    difficulties=[3, 5, 7],\n)\n\ngenerator.save_jsonl(data, "train.jsonl")`;
$('#quickstart').textContent=quickstart;
let toastTimer;
function toast(message){$('#toast').textContent=message;$('#toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),2500);}
$('#copy-code').addEventListener('click',async()=>{try{await navigator.clipboard.writeText(quickstart);toast('Код скопирован');}catch{const range=document.createRange();range.selectNodeContents($('#quickstart'));const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);toast('Код выделен. Нажмите Ctrl+C или ⌘C.');}});
setupLearning();heroGraph();atlasGraph();renderDomain();renderFilters();renderCatalog();selectSample();renderGallery();
const requestedTask=new URLSearchParams(location.search).get('task');if(requestedTask&&taskMap.has(requestedTask))openTask(requestedTask);
})();
