'use strict';
const $=s=>document.querySelector(s), cap=(v,a,b)=>Math.max(a,Math.min(b,v));
const frames=[
 ['Общий вид','Принять смену','Кликнуть по станции отбора проб. Персонаж обходит линию розлива.','Завод занимает весь экран. В HUD только задача, таймер и четыре отметки.','Ориентирование в производственной цепочке.','world'],
 ['Маршрут','Подойти к оборудованию','Идти по проходу с помощью мыши, WASD или сенсорного джойстика.','Клик по объекту означает «подойти», работа начинается только в зоне доступа.','Разделяем перемещение и взаимодействие.','walk'],
 ['Приближение','Сверить маркировку','На лотке выбрать К-241 / Л-2, затем открыть выдачу пробы.','Камера приближается к реальным предметам. Крупная панель появляется только здесь.','Принадлежность результата конкретной пробе.','samples'],
 ['Головоломка','Повернуть вентиль','Повернуть колесо на четверть оборота и забрать промаркированную пробу.','Поворот мышью или пальцем; стрелки и ползунок дают точную альтернативу.','Следование рабочей карточке; это учебный макет узла выдачи.','valve'],
 ['Перенос','Отнести пробу в лабораторию','В руках одна проба. Выбрать станцию pH и пройти к ней.','Состояние видно прямо у персонажа. Нет постоянно открытого инвентаря.','Связь отбора и измерения.','carry'],
 ['Бортовой компьютер','Проверить pH-метр','Сравнить 4,32 с контрольными 4,00 ± 0,05 и настроить прибор.','Экран оборудования становится игровой поверхностью: показание, регулятор и запуск.','Контроль измерений до работы с пробой.','meter'],
 ['Параллельная работа','Запустить анализ и отойти','Оставить пробу на станции. Пока идёт измерение, перейти к весам.','Таймер прибора продолжает идти в общем виде. Есть повод планировать маршрут.','Различать время работы прибора и время игрока.','process'],
 ['Приближение','Рассчитать результат','Взвесить подготовленный остаток: вычесть тару и получить 6,2%.','Данные находятся на дисплее весов и карточке рядом. Ошибка позволяет исправить расчёт.','Масса тары, массовая доля, проценты.','balance'],
 ['Возвращение','Забрать показания','Вернуться к прибору: первый результат 3,10, повторный 3,12.','Готовность станции видна издалека. Завершение анализа не подменяет вывод.','Воспроизводимость отклонения.','ready'],
 ['Решение','Зафиксировать отклонение','Сопоставить результаты с учебной карточкой и выбрать передачу на проверку.','На компьютере сохраняются оба измерения, расчёт и принятое решение.','Не выдавать единственный показатель за допуск партии.','report'],
 ['Маршрут','Передать протокол','Нести протокол старшему коллеге через производственный проход.','Возвращаемся в общий вид. Завод связывает задания в один рабочий день.','Командное взаимодействие и границы полномочий.','handoff'],
 ['Завершение','Увидеть выполненную работу','Передать результат и прочитать короткий разбор. Можно продолжить прогулку.','Итог компактный, мир остаётся виден. В рабочем продукте здесь будет переход к анкете.','Самопроверка конкретных действий, без рейтинга пригодности.','complete']
].map((f,i)=>({id:i+1,mode:f[0],title:f[1],action:f[2],reason:f[3],check:f[4],scene:f[5]}));
const stations=[{id:'samples',name:'Узел отбора',short:'1',p:[-1.9,2.6],background:'samples'},{id:'meter',name:'pH-метр',short:'2',p:[3,2.65],background:'instrument'},{id:'balance',name:'Весы',short:'3',p:[5.2,2.65],background:'balance'},{id:'senior',name:'Старший коллега',short:'4',p:[-6,-2.7],background:'journal'}];
const blocked=[[-7.5,1.95,-2.55,5.6],[-5.3,-1.1,5.05,1.25],[1.25,3.25,7.9,5.2],[-7.3,-4.7,-4.7,-3.2],[4.9,-4.8,8,-2.35]];
const state={}; let current=0,route=[],pending=null,last=performance.now(),toastUntil=0,open=null,keys=new Set(),joy=[0,0];
function reset(live=true){Object.assign(state,{p:[0,-2.3],carry:null,sample:false,label:false,valve:0,cal:0,calibrated:false,analysis:0,started:false,ready:false,repeat:false,balance:false,report:false,complete:false,paused:false,assist:false,remaining:240,elapsed:0,live,errors:[]});route=[];pending=null;keys.clear();joy=[0,0];open=null;$('#closeup').hidden=true;$('#pause-screen').hidden=true;$('#canvas').classList.remove('in-device');$('#assist').checked=false;$('#toast').textContent='';draw();}
function project(p){return [.5+p[0]*.05,.51266861-p[1]*.06334257]}
function unproject(p){return [(p[0]-.5)/.05,(.51266861-p[1])/.06334257]}
function walkable(p){return p[0]>=-8&&p[0]<=8&&p[1]>=-5&&p[1]<=5.4&&!blocked.some(b=>p[0]>=b[0]&&p[0]<=b[2]&&p[1]>=b[1]&&p[1]<=b[3]);}
const step=.25,key=p=>p.join(',');
function grid(p){return p.map(v=>Math.round(v/step))}
function findPath(start,end){
 const s=grid(start),e=grid(end),q=[s],seen=new Set([key(s)]),prev=new Map();let found=null;
 while(q.length){const a=q.shift();if(a[0]===e[0]&&a[1]===e[1]){found=a;break}for(const d of [[1,0],[-1,0],[0,1],[0,-1]]){const b=[a[0]+d[0],a[1]+d[1]],k=key(b);if(!seen.has(k)&&walkable(b.map(v=>v*step))){seen.add(k);prev.set(k,a);q.push(b)}}}
 if(!found)return [];
 const out=[];while(key(found)!==key(s)){out.unshift(found.map(v=>v*step));found=prev.get(key(found))}return out;
}
function moveTo(p,station=null){if(open||state.paused)return;const end=station?station.p:p;if(!walkable(end)){toast('Здесь оборудование. Выберите свободный проход.');return}const next=findPath(state.p,end);if(!next.length&&Math.hypot(state.p[0]-end[0],state.p[1]-end[1])>.5){toast('До этой точки нет свободного прохода.');return}route=next;pending=station;draw();if(!route.length&&pending)interact(pending.id);}
function toast(message){$('#toast').textContent=message;toastUntil=performance.now()+5500;}
function error(message){state.errors.push(message);const el=$('#feedback');if(el)el.textContent=message;else toast(message);}
function objective(){if(state.complete)return 'Смена завершена · можно осмотреть завод';if(state.report)return 'Передайте протокол старшему коллеге';if(state.ready&&state.balance)return 'Вернитесь к pH-метру за результатами';if(state.started&&!state.balance)return 'Анализ идёт · выполните расчёт у весов';if(state.started)return 'Дождитесь результата у pH-метра';if(state.sample)return 'Доставьте пробу к pH-метру';return 'Заберите пробу К-241 / Л-2';}
function draw(){
 const p=project(state.p);$('#player').style.left=p[0]*100+'%';$('#player').style.top=p[1]*100+'%';$('#player').classList.toggle('walking',route.length>0||keys.size>0||Math.hypot(...joy)>.1);$('#carried').textContent=state.carry==='sample'?'К-241':state.carry==='report'?'Протокол':'';$('#hands').textContent=state.carry==='sample'?'В руках: проба К-241':state.carry==='report'?'В руках: протокол':'Руки свободны';$('#objective').innerHTML='<small>ТЕКУЩАЯ ЗАДАЧА</small>'+objective();
 $('#progress').innerHTML=[state.sample,state.calibrated,state.balance&&state.report,state.complete].map(v=>`<i class="${v?'done':''}"></i>`).join('');
 const t=Math.max(0,Math.floor(state.assist?state.elapsed:state.remaining)),m=String(Math.floor(t/60)).padStart(2,'0'),s=String(t%60).padStart(2,'0');$('#timer').textContent=(state.remaining<0&&!state.assist?'+':'')+(state.remaining<0&&!state.assist?String(Math.floor(-state.remaining/60)).padStart(2,'0')+':'+String(Math.floor(-state.remaining)%60).padStart(2,'0'):m+':'+s);$('.clock').classList.toggle('overtime',state.remaining<0&&!state.assist);
 $('#path').setAttribute('points',[state.p,...route].map(project).map(v=>[v[0]*1600,v[1]*1000].join(',')).join(' '));const dest=route.at(-1);$('#destination').style.opacity=dest?1:0;if(dest){const v=project(dest);$('#destination').setAttribute('cx',v[0]*1600);$('#destination').setAttribute('cy',v[1]*1000)}
 for(const st of stations){const b=$(`[data-station="${st.id}"]`);b.classList.toggle('done',st.id==='samples'?state.sample:st.id==='meter'?state.report:st.id==='balance'?state.balance:state.complete);b.classList.toggle('processing',st.id==='meter'&&state.started&&!state.ready);b.firstChild.textContent=st.id==='meter'&&state.started?(state.ready?'✓':Math.ceil(state.analysis)):st.short;}
 const near=stations.find(s=>Math.hypot(s.p[0]-state.p[0],s.p[1]-state.p[1])<.65);$('#nearby').innerHTML=!open&&near?`<button data-interact="${near.id}">E · ${near.name}</button>`:'';$('#nearby').style.left=p[0]*100+'%';$('#nearby').style.top=(p[1]*100-9)+'%';
}
const paper=(title,body)=>`<aside class="paper"><span class="stamp">РАБОЧАЯ КАРТОЧКА · К-241</span><h3>${title}</h3>${body}</aside>`;
const consoleBox=body=>`<div class="console">${body}<p id="feedback" class="feedback" role="status"></p></div>`;
const btn=(action,text,primary=false)=>`<button data-act="${action}" class="${primary?'primary':''}">${text}</button>`;
function interact(id){
 if(state.paused)return;const st=stations.find(s=>s.id===id);if(Math.hypot(st.p[0]-state.p[0],st.p[1]-state.p[1])>.7){moveTo(st.p,st);return}
 if(id==='meter'&&!state.sample){toast('Сначала заберите промаркированную пробу.');return}if(id==='balance'&&!state.started){toast('Сначала оставьте пробу на станции pH.');return}if(id==='senior'&&!state.report){toast('Коллега ждёт протокол: измерения и расчёт.');return}
 open=id;route=[];pending=null;keys.clear();joy=[0,0];$('#canvas').classList.add('in-device');$('#closeup').hidden=false;$('#closeup-background').src='backgrounds/'+st.background+'.png';$('#device-kind').textContent='РАБОЧЕЕ МЕСТО · '+st.short+' / 4';$('#device-name').textContent=st.name;renderDevice();draw();
}
function renderDevice(){let content='';
 if(open==='samples'){
 content=paper('Выдача пробы','<dl><dt>Партия</dt><dd>К-241</dd><dt>Точка</dt><dd>Л-2</dd></dl><p>Сверьте маркировку. Выдача открывается поворотом колеса на 90°.</p>')+consoleBox(state.sample?'<h3>Проба выдана</h3><p>К-241 / Л-2 уже у вас.</p>'+btn('leave','В цех',true):!state.label?'<h3>Выберите маркировку</h3><p class="meta">Сканер узла выдачи</p><div class="choices">'+btn('wrong-label','К-240 / Л-2')+btn('label','К-241 / Л-2')+btn('wrong-label','Без номера')+'</div>':'<h3>Узел выдачи пробы</h3><div class="display"><span id="angle">'+Math.round(state.valve)+'</span>°<small>Поворот колеса · цель 90° ± 5°</small></div><div class="wheel" role="slider" tabindex="0" aria-label="Повернуть вентиль" aria-valuemin="0" aria-valuemax="180" aria-valuenow="'+state.valve+'" style="transform:rotate('+state.valve+'deg)"></div><label>Положение вентиля<input id="valve" type="range" min="0" max="180" value="'+state.valve+'"></label>'+btn('take','Забрать пробу',true));
 } else if(open==='meter'){
 let screen='';
 if(!state.calibrated)screen='<h3>Контроль прибора</h3><div class="display"><span id="reading">'+(4.32-state.cal*.008).toFixed(2).replace('.',',')+'</span><small>Контрольный раствор · pH</small></div><label>Настройка<input id="cal" type="range" min="0" max="80" value="'+state.cal+'"></label>'+btn('control','Проверить контроль',true);
 else if(!state.started)screen='<h3>Контроль пройден</h3><div class="display">4,01<small>Контрольное измерение</small></div><p>Поставьте пробу К-241 на станцию.</p>'+btn('start-analysis','Поставить и запустить',true);
 else if(!state.ready)screen='<h3>Идёт измерение</h3><div class="display"><span id="process-time">'+Math.ceil(state.analysis)+'</span> с<small>Проба К-241 на станции</small></div><progress id="process-bar" max="14" value="'+(14-state.analysis)+'"></progress><p>Руки свободны. Можно перейти к весам.</p>'+btn('leave','Отойти к весам',true);
 else if(!state.repeat)screen='<h3>Результат измерения</h3><div class="display">3,10<small>pH · первое измерение</small></div><p>Сравните с карточкой. Нужна проверка результата.</p>'+btn('repeat','Повторить измерение',true);
 else screen='<h3>Протокол К-241 / Л-2</h3><div class="display">3,10 / 3,12<small>Первое / повторное измерение pH</small></div><p>Сухой остаток: '+(state.balance?'6,2%':'ещё не рассчитан')+'</p><p>Как передать результат?</p>'+btn('approve','Показатели в норме')+btn('report','Зафиксировать отклонение',true);
 content=paper('Контроль и анализ','<dl><dt>Контроль pH</dt><dd>4,00 ± 0,05</dd><dt>Проба · pH</dt><dd>3,40–3,80</dd><dt>Остаток</dt><dd>5,8–6,6%</dd></dl><p>Сначала проверьте прибор. При отклонении повторите измерение и передайте записи коллеге.</p>')+consoleBox(screen);
 } else if(open==='balance')content=paper('Расчёт остатка','<p>Данные подготовленного образца К-241.</p><p>w = (m₂ − m₁) / m × 100%</p><dl><dt>Тара m₁</dt><dd>24,80 г</dd><dt>Проба m</dt><dd>10,00 г</dd><dt>Интервал</dt><dd>5,8–6,6%</dd></dl>')+consoleBox('<h3>Весы · подготовленный остаток</h3><div class="display">25,42 г<small>Чашка с сухим остатком · m₂</small></div><p>Какова массовая доля остатка?</p><div class="choices">'+btn('wrong-calc','254,2%')+btn('calc','6,2%')+btn('wrong-calc','0,62%')+'</div>'+(state.balance?'<p>Записано: 6,2%. Можно вернуться к pH-метру.</p>'+btn('leave','Вернуться в цех',true):'')+'<p class="note">Образец уже подготовлен. Сушка здесь не воспроизводится.</p>');
 else content=paper('Командная работа','<p>Лаборант передаёт проверенные измерения. Решение по партии принимает уполномоченный специалист.</p>')+consoleBox(state.complete?'<h3>Смена завершена</h3><p>Проба идентифицирована. Прибор проверен. pH повторён. Остаток рассчитан. Отклонение передано.</p><p>Исправлений: '+state.errors.length+'.</p>'+btn('leave','Продолжить прогулку',true):'<h3>Передать протокол</h3><div class="row"><span>Проба</span><strong>К-241 / Л-2</strong></div><div class="row"><span>pH</span><strong>3,10 / 3,12</strong></div><div class="row"><span>Сухой остаток</span><strong>6,2%</strong></div><p>Повторное отклонение pH. Нужна проверка старшим коллегой.</p>'+btn('handoff','Передать коллеге',true));
 $('#device').innerHTML=content;bindWheel();
}
function leave(){open=null;$('#closeup').hidden=true;$('#canvas').classList.remove('in-device');$('#canvas').focus({preventScroll:true});draw();}
function action(a){if(state.paused)return;switch(a){
 case 'leave':leave();break;
 case 'wrong-label':error('Нужна партия К-241 и точка Л-2. Не угадывайте маркировку.');break;
 case 'label':state.label=true;renderDevice();break;
 case 'take':if(Math.abs(state.valve-90)>5){error('Выставьте 90° по рабочей карточке.');break}state.sample=true;state.carry='sample';leave();toast('Проба у вас. Доставьте её к pH-метру.');break;
 case 'control':if(Math.abs(4.32-state.cal*.008-4)>.05){error('Контроль вне допуска ±0,05. Скорректируйте настройку.');break}state.calibrated=true;renderDevice();break;
 case 'start-analysis':state.started=true;state.analysis=14;state.carry=null;renderDevice();break;
 case 'repeat':state.repeat=true;renderDevice();break;
 case 'approve':error('Оба значения pH ниже 3,40. Запишите отклонение и сообщите коллеге.');break;
 case 'report':if(!state.balance){error('Сначала завершите расчёт у весов.');break}state.report=true;state.carry='report';leave();toast('Протокол готов. Передайте его старшему коллеге.');break;
 case 'wrong-calc':error('Вычтите массу чашки: 25,42 − 24,80 = 0,62 г. Разделите на 10,00 г и умножьте на 100%.');break;
 case 'calc':state.balance=true;renderDevice();break;
 case 'handoff':state.complete=true;state.carry=null;renderDevice();break;
 }draw();}
function setValve(value){state.valve=cap(value,0,180);const w=$('.wheel');if(w){w.style.transform=`rotate(${state.valve}deg)`;w.setAttribute('aria-valuenow',Math.round(state.valve));$('#angle').textContent=Math.round(state.valve);$('#valve').value=state.valve;}}
function bindWheel(){const w=$('.wheel');if(!w)return;let previous=null;w.onpointerdown=e=>{w.setPointerCapture(e.pointerId);const r=w.getBoundingClientRect();previous=Math.atan2(e.clientY-r.top-r.height/2,e.clientX-r.left-r.width/2);e.preventDefault();};w.onpointermove=e=>{if(previous===null)return;const r=w.getBoundingClientRect(),angle=Math.atan2(e.clientY-r.top-r.height/2,e.clientX-r.left-r.width/2);let delta=angle-previous;if(delta>Math.PI)delta-=Math.PI*2;if(delta< -Math.PI)delta+=Math.PI*2;setValve(state.valve+delta*180/Math.PI);previous=angle;};w.onpointerup=w.onpointercancel=()=>previous=null;w.onkeydown=e=>{if(['ArrowLeft','ArrowDown','ArrowRight','ArrowUp'].includes(e.key)){e.preventDefault();setValve(state.valve+(['ArrowLeft','ArrowDown'].includes(e.key)?-5:5))}};}
function pause(){state.paused=!state.paused;$('#pause-screen').hidden=!state.paused;keys.clear();joy=[0,0];}
$('#pause').onclick=pause;$('#resume').onclick=pause;$('#assist').onchange=e=>{state.assist=e.target.checked;draw()};$('#leave').onclick=leave;
$('#canvas').addEventListener('click',e=>{if(e.target.closest('button,input,.wheel,.console,.paper,#pause-screen,#joystick'))return;if(open)return;const r=$('#canvas').getBoundingClientRect();moveTo(unproject([(e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height]));$('#canvas').focus({preventScroll:true});});
$('#canvas').addEventListener('click',e=>{const b=e.target.closest('[data-act],[data-interact],[data-station]');if(!b)return;if(b.dataset.act)action(b.dataset.act);else if(b.dataset.interact)interact(b.dataset.interact);else moveTo(stations.find(s=>s.id===b.dataset.station).p,stations.find(s=>s.id===b.dataset.station));});
$('#device').addEventListener('input',e=>{if(e.target.id==='valve')setValve(+e.target.value);if(e.target.id==='cal'){state.cal=+e.target.value;$('#reading').textContent=(4.32-state.cal*.008).toFixed(2).replace('.',',')}});
$('#canvas').addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();if(state.paused)pause();else if(open)leave();else pause();return}if(e.target.matches('input,button,[role=slider]'))return;const k=e.key.toLowerCase();if(['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright'].includes(k)){e.preventDefault();if(!open&&!state.paused){keys.add(k);route=[];pending=null}}if(k==='e'&&!open&&!state.paused){e.preventDefault();const n=stations.find(s=>Math.hypot(s.p[0]-state.p[0],s.p[1]-state.p[1])<.7);if(n)interact(n.id);else toast('Подойдите ближе к оборудованию.');}});
window.addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));window.addEventListener('blur',()=>{keys.clear();joy=[0,0];if(state.live&&!state.paused)pause()});document.addEventListener('visibilitychange',()=>{if(document.hidden&&state.live&&!state.paused)pause()});
const stick=$('#joystick');function stickMove(e){const r=stick.getBoundingClientRect();joy=[cap((e.clientX-r.left-r.width/2)/(r.width*.4),-1,1),cap(-(e.clientY-r.top-r.height/2)/(r.height*.4),-1,1)];const l=Math.hypot(...joy);if(l>1)joy=joy.map(v=>v/l);stick.firstElementChild.style.transform=`translate(${joy[0]*90}%,${-joy[1]*90}%)`;route=[];pending=null;}
stick.onpointerdown=e=>{if(open||state.paused)return;stick.setPointerCapture(e.pointerId);stickMove(e);e.preventDefault()};stick.onpointermove=e=>{if(stick.hasPointerCapture(e.pointerId))stickMove(e)};stick.onpointerup=stick.onpointercancel=()=>{joy=[0,0];stick.firstElementChild.style.transform=''};$('#touch-action').onclick=()=>{const n=stations.find(s=>Math.hypot(s.p[0]-state.p[0],s.p[1]-state.p[1])<.7);if(n)interact(n.id);else toast('Подойдите ближе к станции.');};
function tick(now){const dt=Math.min((now-last)/1000,.08);last=now;if(!state.paused&&state.live){if(!state.complete){state.elapsed+=dt;if(!state.assist)state.remaining-=dt}if(state.started&&!state.ready){state.analysis=Math.max(0,state.analysis-dt);if(state.analysis===0){state.ready=true;toast('Анализ К-241 готов. Вернитесь к pH-метру.');if(open==='meter')renderDevice()}else if(open==='meter'&&$('#process-time')){$('#process-time').textContent=Math.ceil(state.analysis);$('#process-bar').value=14-state.analysis}}
 if(!open){let delta=[0,0];if(route.length){const d=[route[0][0]-state.p[0],route[0][1]-state.p[1]],dist=Math.hypot(...d),v=3.2*dt;if(dist<=v){state.p=route.shift();if(!route.length&&pending){const id=pending.id;pending=null;interact(id)}}else state.p=state.p.map((v,i)=>v+d[i]/dist*3.2*dt)}else{delta=[(keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0)+joy[0],(keys.has('w')||keys.has('arrowup')?1:0)-(keys.has('s')||keys.has('arrowdown')?1:0)+joy[1]];const n=Math.hypot(...delta);if(n>.05){delta=delta.map(v=>v/Math.max(1,n)*3.2*dt);const p=[state.p[0]+delta[0],state.p[1]+delta[1]];if(walkable(p))state.p=p;else for(let i=0;i<2;i++){const p=[...state.p];p[i]+=delta[i];if(walkable(p))state.p=p}}}}
 }if(toastUntil&&now>toastUntil){$('#toast').textContent='';toastUntil=0}draw();requestAnimationFrame(tick);}
function showFrame(index){current=cap(index,0,frames.length-1);reset(false);const f=frames[current];state.remaining=240-current*17;state.elapsed=current*17;
 if(current>=3)state.label=true;
 if(current>=4){state.sample=true;state.valve=90;state.carry='sample'}
 if(current>=6){state.calibrated=true;state.cal=40;state.started=true;state.analysis=9;state.carry=null}
 if(current>=8){state.balance=true;state.ready=true;state.analysis=0}
 if(current>=9)state.repeat=true;
 if(current>=10){state.report=true;state.carry='report'}
 if(current>=11){state.complete=true;state.carry=null}
 if(['samples','valve'].includes(f.scene)){state.p=[...stations[0].p];interact('samples')}
 if(['meter','report'].includes(f.scene)){state.p=[...stations[1].p];interact('meter')}
 if(f.scene==='balance'){state.p=[...stations[2].p];interact('balance')}
 if(f.scene==='carry')state.p=[.3,2.65];
 if(f.scene==='process')state.p=[4.1,2.65];
 if(f.scene==='ready')state.p=[4.6,2.65];
 if(f.scene==='handoff')state.p=[-2.3,-2.5];
 if(f.scene==='complete'){state.p=[...stations[3].p];interact('senior')}
 if(f.scene==='walk'){state.p=[-5.8,-1.9];route=findPath(state.p,stations[0].p)}
 $('#frame-count').textContent=`${current+1} / ${frames.length}`;$('#frame-mode').textContent=f.mode;$('#frame-title').textContent=f.title;$('#frame-action').innerHTML='<strong>Действие игрока.</strong> '+f.action;$('#frame-reason').innerHTML='<strong>Почему так.</strong> '+f.reason;$('#frame-check').innerHTML='<strong>Что проверяем.</strong> '+f.check;[...$('#timeline').children].forEach((b,i)=>b.classList.toggle('active',i===current));draw();}
for(const s of stations){const p=project(s.p);$('#stations').insertAdjacentHTML('beforeend',`<button data-station="${s.id}" class="station" style="left:${p[0]*100}%;top:${(p[1]*100)-4}%" aria-label="Подойти: ${s.name}">${s.short}<span class="label">${s.name}</span></button>`)}
frames.forEach((f,i)=>{const b=document.createElement('button');b.innerHTML=`<b>${String(i+1).padStart(2,'0')}</b>${f.title}`;b.onclick=()=>showFrame(i);$('#timeline').append(b)});$('#previous').onclick=()=>showFrame(current-1);$('#next').onclick=()=>showFrame(current+1);$('#play').onclick=()=>{reset(true);$('#frame-count').textContent='Свободная игра';$('#frame-mode').textContent='ИНТЕРАКТИВНЫЙ МАКЕТ';$('#frame-title').textContent='Пройдите смену самостоятельно';$('#frame-action').textContent='Начните с узла отбора проб. На станциях читайте рабочую карточку.';$('#frame-reason').textContent='Клик по станции прокладывает маршрут. WASD и сенсорный джойстик позволяют идти вручную.';$('#frame-check').textContent='Скорость маршрута и правильность анализа — разные результаты.';[...$('#timeline').children].forEach(b=>b.classList.remove('active'));$('#canvas').focus({preventScroll:true})};
const params=new URLSearchParams(location.search);if(params.has('capture'))document.body.classList.add('capture');reset(false);showFrame((+params.get('frame')||1)-1);requestAnimationFrame(tick);
window.game={state,frames,showFrame,reset,moveTo,interact,action,leave,findPath,walkable,project,stations,get open(){return open},get route(){return route},pause};

$('#fullscreen').onclick=()=>{if(document.fullscreenElement)document.exitFullscreen();else $('#canvas').requestFullscreen?.().catch(()=>toast('Включите альбомную ориентацию экрана.'));};
