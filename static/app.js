'use strict';
const $ = id => document.getElementById(id);
let state, csrf='', historyData, pending=false;
function el(tag, text, className) { const e=document.createElement(tag); if(text!==undefined)e.textContent=text; if(className)e.className=className; return e; }
function message(text='',error=false){$('status').textContent=text;$('status').classList.toggle('error',error);}
async function api(path,data){
 const response=await fetch(new URL(path.replace(/^\//,''),new URL('.',window.location.href)),{method:data===undefined?'GET':'POST',headers:data===undefined?{}:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:data===undefined?undefined:JSON.stringify(data)});
 const result=await response.json();
 if(!response.ok){if(response.status===401 && path!='/api/login'){showLogin();}throw new Error(result.error||'Request failed.');}return result;
}
async function run(fn){if(pending)return;pending=true;document.querySelectorAll('button').forEach(b=>b.disabled=true);message('Saving…');try{await fn();message('Saved.');}catch(error){message(error.message,true);}finally{pending=false;document.querySelectorAll('button').forEach(b=>b.disabled=false);}}
function showLogin(){$('login').hidden=false;$('application').hidden=true;$('password').focus();}
function view(name){for(const v of ['planner','recipes','history'])$(v+'-view').hidden=v!==name;window.scrollTo(0,0);}
function formatDate(value,opts={month:'long',day:'numeric',year:'numeric'}){return new Intl.DateTimeFormat('en-US',{...opts,timeZone:'UTC'}).format(new Date(value+'T12:00:00Z'));}
function weekday(value){return new Date(value+'T12:00:00Z').getUTCDay();}
function eatOut(value){return weekday(value)===5 && Math.round((new Date(value+'T12:00:00Z')-new Date('2026-10-16T12:00:00Z'))/86400000)%14===0;}
function eligible(recipe,value){const d=weekday(value);return !recipe.archived&&!eatOut(value)&&(!recipe.weekend||d===0||d===6)&&(d!==2||recipe.taco)&&(d!==4||recipe.crockpot);}
function recipeFor(meal){return state.recipes.find(r=>r.id===meal.recipe_id)||meal.snapshot;}
function dinnerName(meal){return meal.snapshot?.title||recipeFor(meal)?.title||meal.special;}
async function load(start){state=await api('/api/state'+(start?'?start='+encodeURIComponent(start):''));csrf=state.csrf;$('login').hidden=true;$('application').hidden=false;if(!$('start').value)$('start').value=state.start||state.today;render();}
function render(){
 $('season').value=state.settings.season;
 const present=state.meals.length>0;
 $('menu-section').hidden=!present;$('shopping-section').hidden=!state.saved;$('empty').hidden=present;
 $('regenerate').hidden=!state.saved;$('overlap-note').hidden=!present||state.saved;
 $('generate').firstChild.textContent=state.saved?'Open saved menu ':'Generate 2 Weeks ';
 if(present){const end=new Date(state.start+'T12:00:00Z');end.setUTCDate(end.getUTCDate()+13);const last=end.toISOString().slice(0,10);$('menu-range').textContent=formatDate(state.start)+' – '+formatDate(last);$('shopping-title').textContent='Shopping List — '+formatDate(state.start,{month:'short',day:'numeric'})+'–'+formatDate(last,{month:'short',day:'numeric'});renderMeals();}
 renderGroceries();renderRecipes();
}
function renderMeals(){
 $('meals').replaceChildren();
 for(const m of state.meals){const row=el('div',undefined,'meal-row');row.dataset.date=m.date;
 const date=el('div',undefined,'meal-date');date.append(el('strong',formatDate(m.date,{weekday:'long'})),el('span',formatDate(m.date,{month:'long',day:'numeric',year:'numeric'})));
 const info=el('div');info.append(el('div',dinnerName(m),'meal-title'+(!m.recipe_id?' meal-special':'')));
 const tags=[];if(weekday(m.date)===2)tags.push('Taco Tuesday');if(weekday(m.date)===4)tags.push('Crockpot Thursday');if(m.manual)tags.push('Your pick');for(const tag of tags)info.append(el('span',tag,'tag'));
 row.append(date,info);
 if(!eatOut(m.date)&&state.saved){const b=el('button','Change','text-button');b.type='button';b.setAttribute('aria-label','Change dinner for '+m.date);b.addEventListener('click',()=>editMeal(row,m,b));row.append(b);}
 $('meals').append(row);
 }
}
function editMeal(row,meal,button){
 const prior=row.querySelector('.meal-edit');if(prior){prior.remove();button.setAttribute('aria-expanded','false');return;}
 button.setAttribute('aria-expanded','true');
 const form=el('form',undefined,'meal-edit'),select=el('select');select.id='meal-'+meal.date;select.setAttribute('aria-label','Dinner for '+meal.date);
 const label=el('label','Choose an eligible dinner');label.htmlFor=select.id;form.append(label);
 if(weekday(meal.date)===6){const o=el('option','Fend for Yourself');o.value='';select.append(o);}
 for(const r of state.recipes.filter(r=>eligible(r,meal.date)).sort((a,b)=>a.title.localeCompare(b.title))){const o=el('option',r.title);o.value=r.id;select.append(o);}
 select.value=meal.recipe_id||'';
 const save=el('button','Save dinner');const cancel=el('button','Cancel','text-button');cancel.type='button';cancel.onclick=()=>{form.remove();button.focus();button.setAttribute('aria-expanded','false');};form.append(select,save,cancel);
 form.onsubmit=e=>{e.preventDefault();run(async()=>{await api('/api/meal',{start:state.start,date:meal.date,recipe_id:select.value?Number(select.value):null,special:select.value?null:'Fend for Yourself'});await load(state.start);});};row.append(form);select.focus();
}
async function saveGroceries(edits){await api('/api/groceries',{start:state.start,edits});await load(state.start);}
function changeEdits(fn){const edits=structuredClone(state.grocery_edits);fn(edits);return saveGroceries(edits);}
function renderGroceries(){
 $('groceries').replaceChildren();$('excluded').replaceChildren();
 const groups=new Map();for(const item of state.groceries){if(item.excluded){const row=el('div',undefined,'grocery-row');row.append(el('span',item.name));const restore=el('button','Include again','text-button');restore.onclick=()=>run(()=>changeEdits(e=>e.excluded=e.excluded.filter(id=>id!==item.id)));row.append(restore);$('excluded').append(row);continue;}
 if(!groups.has(item.category))groups.set(item.category,[]);groups.get(item.category).push(item);}
 for(const [category,items] of groups){const section=el('section',undefined,'grocery-group');section.append(el('h3',category));for(const item of items){const row=el('div',undefined,'grocery-row'+(item.checked?' checked':'')),check=el('input');check.type='checkbox';check.checked=!!item.checked;check.id='grocery-'+encodeURIComponent(item.id);check.setAttribute('aria-label','Bought '+item.name);
 check.onchange=()=>run(()=>changeEdits(e=>{if(item.id.startsWith('manual:'))e.additions.find(x=>x.id===item.id).checked=check.checked;else e.checked=check.checked?[...new Set([...e.checked,item.id])]:e.checked.filter(id=>id!==item.id);}));
 const label=el('label');label.append(el('span',item.name,'item-name'));label.htmlFor=check.id;label.append(el('span',item.quantity+(item.note?' · '+item.note:'')));
 const edit=el('button','Edit','text-button');edit.setAttribute('aria-label','Edit quantity for '+item.name);edit.onclick=()=>groceryEditor(section,row,item);
 const remove=el('button',item.id.startsWith('manual:')?'Remove':'Have it','text-button');remove.setAttribute('aria-label',(item.id.startsWith('manual:')?'Remove ':'Already have ')+item.name);remove.onclick=()=>run(()=>changeEdits(e=>{if(item.id.startsWith('manual:'))e.additions=e.additions.filter(x=>x.id!==item.id);else e.excluded=[...new Set([...e.excluded,item.id])];}));row.append(check,label,edit,remove);section.append(row);}$('groceries').append(section);}
 $('excluded-details').hidden=!state.grocery_edits?.excluded.length;
}
function groceryEditor(section,row,item){
 if(row.nextSibling?.classList?.contains('grocery-editor'))return;
 const form=el('form',undefined,'grocery-editor');const input=el('input');input.value=item.quantity;input.maxLength=200;input.setAttribute('aria-label','Quantity for '+item.name);const save=el('button','Save amount');const cancel=el('button','Cancel','text-button');cancel.type='button';cancel.onclick=()=>form.remove();form.append(input,save,cancel);row.after(form);input.focus();form.onsubmit=e=>{e.preventDefault();run(()=>changeEdits(edits=>{if(item.id.startsWith('manual:'))edits.additions.find(x=>x.id===item.id).quantity=input.value||'amount not specified';else edits.overrides[item.id]=input.value||'amount not specified';}));};
}
function renderRecipes(){
 $('recipe-list').replaceChildren();for(const r of state.recipes.filter(r=>!r.archived)){
 const card=el('div',undefined,'recipe-card'),info=el('div');info.append(el('h3',r.title));const flags=[r.taco?'Taco Tuesday':null,r.crockpot?'Crockpot':null,r.weekend?'Weekend only':null,{budget:'Budget',moderate:'Moderate',higher:'Higher Cost'}[r.cost]].filter(Boolean);flags.forEach(f=>info.append(el('span',f,'tag')));if(r.review)info.append(el('p',r.review,'review'));const edit=el('button','Edit','text-button');edit.setAttribute('aria-label','Edit '+r.title);edit.onclick=()=>editRecipe(r);card.append(info,edit);$('recipe-list').append(card);}
}
function editRecipe(r){
 $('recipe-form').reset();$('recipe-id').value=r?.id||'';$('editor-title').textContent=r?'Edit recipe':'Add recipe';$('recipe-title').value=r?.title||'';$('ingredient-text').value=r?.ingredient_text||'';$('instructions').value=r?.instructions||'';for(const flag of ['taco','crockpot','weekend'])$(flag).checked=!!r?.[flag];$('cost').value=r?.cost||'moderate';$('archive-recipe').hidden=!r;$('recipe-form').hidden=false;$('recipe-list').hidden=true;$('recipe-title').focus();
}
function closeRecipe(){$('recipe-form').hidden=true;$('recipe-list').hidden=false;}
async function confirmAction(title,text,button='Continue'){
 $('confirm-title').textContent=title;$('confirm-text').textContent=text;$('confirm-yes').textContent=button;const d=$('confirm-dialog');d.returnValue='cancel';d.showModal();return new Promise(resolve=>d.addEventListener('close',()=>resolve(d.returnValue==='yes'),{once:true}));
}
async function showHistory(){
 try{historyData=await api('/api/history');view('history');$('saved-menus').replaceChildren();$('revisions').replaceChildren();
 for(const p of state.plans){const row=el('div',undefined,'history-entry');row.append(el('span','Two weeks from '+formatDate(p.start)));const button=el('button','Open menu','text-button');button.onclick=()=>run(async()=>{$('start').value=p.start;await load(p.start);view('planner');});row.append(button);$('saved-menus').append(row);}
 for(const r of historyData.revisions){const row=el('div',undefined,'history-entry'),detail=el('details'),summary=el('summary',formatDate(r.start)+' · '+r.kind+' · '+new Date(r.created).toLocaleString());const list=el('ul');for(const m of r.data){const li=el('li',formatDate(m.date)+' — '+(m.snapshot?.title||m.special));if(m.snapshot){const nested=el('details');nested.append(el('summary','Recipe snapshot'),el('p',m.snapshot.ingredient_text));if(m.snapshot.instructions)nested.append(el('p',m.snapshot.instructions));li.append(nested);}list.append(li);}detail.append(summary,list);row.append(detail);$('revisions').append(row);}
 if(!state.plans.length)$('saved-menus').append(el('p','No saved menus yet.'));if(!historyData.revisions.length)$('revisions').append(el('p','No previous versions yet.'));findHistory();
 }catch(e){message(e.message,true);}
}
function findHistory(){const value=$('history-date').value;$('history-result').replaceChildren();if(!value)return;const meal=historyData?.meals.find(m=>m.date===value);$('history-result').append(el('p',meal?formatDate(value)+' — '+(meal.snapshot?.title||meal.special):'No saved dinner for this date.'));}
$('login-form').onsubmit=e=>{e.preventDefault();run(async()=>{const result=await api('/api/login',{password:$('password').value});csrf=result.csrf;$('password').value='';await load();});};
$('generate-form').onsubmit=e=>{e.preventDefault();run(async()=>{await api('/api/generate',{start:$('start').value});await load($('start').value);});};
$('start').onchange=()=>run(()=>load($('start').value));
$('regenerate').onclick=async()=>{if(await confirmAction('Replace this menu?','This intentionally replaces all 14 dates, including shared dates in overlapping menus. Previous dinners remain in history. Shopping adjustments for this menu will reset.','Replace & regenerate'))run(async()=>{await api('/api/generate',{start:state.start,replace:true});await load(state.start);});};
$('season').onchange=()=>run(async()=>{await api('/api/settings',{season:$('season').value});await load(state.start);});
$('recipes-link').onclick=()=>{closeRecipe();view('recipes');};$('history-link').onclick=showHistory;document.querySelectorAll('.back').forEach(b=>b.onclick=()=>view('planner'));
$('new-recipe').onclick=()=>editRecipe();$('cancel-recipe').onclick=closeRecipe;
$('recipe-form').onsubmit=e=>{e.preventDefault();run(async()=>{const data={id:$('recipe-id').value?Number($('recipe-id').value):null,title:$('recipe-title').value,ingredient_text:$('ingredient-text').value,instructions:$('instructions').value,cost:$('cost').value};for(const f of ['taco','crockpot','weekend'])data[f]=$(f).checked;await api('/api/recipes',data);await load(state.start);closeRecipe();});};
$('archive-recipe').onclick=async()=>{if(await confirmAction('Archive this recipe?','It will leave the dinner rotation. Saved dinners and historical recipe snapshots stay available.','Archive recipe'))run(async()=>{await api('/api/archive',{id:Number($('recipe-id').value)});await load(state.start);closeRecipe();});};
$('extra-form').onsubmit=e=>{e.preventDefault();run(async()=>{await changeEdits(edits=>edits.additions.push({id:'manual:'+crypto.randomUUID(),name:$('extra-name').value.trim(),quantity:$('extra-quantity').value.trim()||'amount not specified',category:'Other',checked:false}));$('extra-form').reset();});};
$('copy').onclick=async()=>{const text=[$('shopping-title').textContent];let group='';for(const item of state.groceries.filter(i=>!i.excluded)){if(item.category!==group){group=item.category;text.push('',group);}text.push((item.checked?'[x] ':'[ ] ')+item.name+' — '+item.quantity+(item.note?' ('+item.note+')':''));}try{await navigator.clipboard.writeText(text.join('\n'));message('Shopping list copied.');}catch(e){message('Clipboard unavailable. Use Print to save the shopping list.',true);}};
$('print').onclick=()=>window.print();$('history-date').onchange=findHistory;
$('logout').onclick=()=>run(async()=>{await api('/api/logout',{});csrf='';state=null;showLogin();});
load().then(()=>message('')).catch(e=>{if($('login').hidden)message(e.message,true);});
