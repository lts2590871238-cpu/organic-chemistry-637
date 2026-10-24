// Actual migrated records + application logic, without inventing chemistry test questions.
import fs from 'node:fs'
import path from 'node:path'
import assert from 'node:assert/strict'
import {createRequire} from 'node:module'
const require=createRequire(import.meta.url),ts=require('typescript'),root=path.resolve(import.meta.dirname,'..'),cache=new Map()
const local=new Map();globalThis.localStorage={getItem:k=>local.get(k)??null,setItem:(k,v)=>local.set(k,v)}
function moduleAt(file){file=path.resolve(file);if(cache.has(file))return cache.get(file).exports;const module={exports:{}};cache.set(file,module);const text=fs.readFileSync(file,'utf8').replaceAll('import.meta.env.BASE_URL',"'/'");const code=ts.transpileModule(text,{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,target:ts.ScriptTarget.ES2022}}).outputText;const localRequire=s=>{if(s.endsWith('.css'))return {};if(!s.startsWith('.'))return require(s);let f=path.resolve(path.dirname(file),s);if(!fs.existsSync(f))f+=fs.existsSync(f+'.tsx')?'.tsx':'.ts';return moduleAt(f)};new Function('require','module','exports',code)(localRequire,module,module.exports);return module.exports}
const api=moduleAt(root+'/src/lib/organic.ts');const qs=JSON.parse(fs.readFileSync(root+'/public/data/questions.json','utf8'));const cards=JSON.parse(fs.readFileSync(root+'/public/data/cards.json','utf8'));const answers=JSON.parse(fs.readFileSync(root+'/public/data/answers.json','utf8'));const days=JSON.parse(fs.readFileSync(root+'/public/data/days.json','utf8'));const results=[]
const check=(name,fn)=>{fn();results.push({name,passed:true})}
check('21天及真实数据齐全',()=>{assert.equal(days.length,21);assert.equal(cards.length,96);assert.equal(new Set(qs.map(q=>q.id)).size,qs.length);assert(!qs.some(q=>q.year===2021||q.year>=2024));for(const q of qs)assert(answers[q.id])})
check('三卷43题150分且六区分值正确',()=>{for(const p of 'ABC'){const a=qs.filter(q=>q.id.startsWith(p+'-'));assert.equal(a.length,43);assert.equal(a.reduce((s,q)=>s+q.score,0),150);assert.deepEqual(['S01','S02','S03','S04','S05','S06'].map(s=>a.filter(q=>q.section===s).reduce((n,q)=>n+q.score,0)),[30,12,35,15,18,40])}})
check('129题题源页码、36题原选项和六PDF接入完整',()=>{for(const q of qs.filter(q=>q.year==null)){assert(q.source.pdfPage);assert(q.source.printedPage);if(q.section==='S02'){assert(q.optionLabels.length>=2);const norm=s=>s.replace(/[()（）\s、,，.。;；]/g,'');for(const label of norm(q.answerKey))assert(q.optionLabels.map(norm).includes(label),q.id+': '+label)}}for(const p of 'ABC')for(const kind of ['paper','solutions'])assert(fs.readFileSync(root+`/public/papers/mock-${p}-${kind}.pdf`).subarray(0,5).toString()==='%PDF-')})
const q=qs.find(q=>q.id==='A-S02-Q03'),multi=qs.find(q=>q.id==='B-S02-Q03'),two=qs.find(q=>q.id==='B-S02-Q01')
check('真实客观题单选/多选/双空判分',()=>{assert.equal(api.gradeChoice(q,'A'),1);assert.equal(api.gradeChoice(q,'AB'),0);assert.equal(api.gradeChoice(multi,'FCB'),1);assert.equal(api.gradeChoice(multi,'BC'),0);assert.equal(api.gradeChoice(two,'A;D'),1);assert.equal(api.gradeChoice(two,'A;A'),.5);assert.equal(api.gradeChoice(qs.find(q=>q.id==='A-S06-Q01'),'正确'),undefined)})
check('考试时限、草稿持久化、提交幂等',()=>{const e=api.startExam(19,[q]);assert.equal(e.deadline-e.started,10800000);api.patchExam(e.id,x=>x.drafts[q.id]='A');assert.equal(api.read().exams[0].drafts[q.id],'A');api.submitExam(e.id,[q]);const n=api.read().history.length;api.submitExam(e.id,[q]);assert.equal(api.read().history.length,n);assert.equal(api.read().exams[0].scores[q.id],1)})
check('同次考试重评更新记录，不重复累计作答次数',()=>{const e=api.read().exams[0];api.attempt(q,'A',1,e.id);const n=api.read().history.length;api.attempt(q,'A',.5,e.id);assert.equal(api.read().history.length,n)})
check('暂停持久化、恢复不扣暂停时间、到期不可暂停',()=>{const original=Date.now;let now=original()+1000;Date.now=()=>now;try{const e=api.startExam(16,[q]);now+=60000;api.pauseExam(e.id);let saved=api.read().exams.find(x=>x.id===e.id);assert.equal(saved.remainingMs,10740000);const pausedAt=saved.pausedAt;now+=3600000;api.pauseExam(e.id);saved=api.read().exams.find(x=>x.id===e.id);assert.equal(saved.pausedAt,pausedAt);assert.equal(saved.remainingMs,10740000);api.resumeExam(e.id);saved=api.read().exams.find(x=>x.id===e.id);assert.equal(saved.deadline-now,10740000);assert.equal(saved.pausedAt,null);now=saved.deadline;api.pauseExam(e.id);assert.equal(api.read().exams.find(x=>x.id===e.id).pausedAt,null);api.submitExam(e.id,[q]);api.resumeExam(e.id);assert(api.read().exams.find(x=>x.id===e.id).submitted)}finally{Date.now=original}})
check('D18仅用真实非编辑题、生成稳定且不补造150分',()=>{const a=api.makeReview(qs,api.read().history),b=api.makeReview(qs,api.read().history);assert.deepEqual(a.questions.map(q=>q.id),b.questions.map(q=>q.id));assert(a.questions.length>0);assert(a.questions.every(q=>q.year<=2023&&q.year!==2021&&!q.edited));assert.equal(a.questions.reduce((s,q)=>s+q.score,0),150);assert.equal(new Set(a.questions.map(q=>q.id)).size,a.questions.length)})
check('D18不把仅展开核对、D18自身或模拟卷作答当成前期弱点证据',()=>{const real=qs.find(q=>q.year===2010&&!q.edited&&q.score!=null);const base=api.makeReview(qs,[]);const rec={qid:real.id,kp:real.kp,type:real.type,score:0,full:real.score,answer:'',ts:1,status:'wrong',context:'D18-1'};assert.deepEqual(api.makeReview(qs,[rec]).questions.map(q=>q.id),base.questions.map(q=>q.id));assert.deepEqual(api.makeReview(qs,[{...rec,context:'practice',status:'reviewed'}]).reasons,base.reasons)})
check('薄弱点按真实已评分作答累计，不将展开解析计作掌握',()=>{const q=qs.find(q=>q.year===2010&&!q.edited&&q.score>0&&q.kp.length);const rec={qid:q.id,kp:q.kp,type:q.type,score:0,full:q.score,answer:'',ts:1,status:'wrong',context:'practice'};const a=api.weaknessStats(qs,[rec,{...rec,status:'correct',score:q.score},{...rec,status:'reviewed'}]);assert(a.length);assert.equal(a[0].n,2);assert.equal(a[0].wrong,1);assert.equal(a[0].loss,1)})
check('原卷分区总分与未知单题分值分离',()=>{const a=api.examScoreSummary(qs.filter(q=>q.day===17),qs);assert.equal(a.total,150);assert.equal(a.unknown,2);assert.equal(a.known,146);assert.equal(a.unallocated,4);assert.equal(qs.find(q=>q.id==='2023-S03-Q02').score,5);assert.equal(api.examScoreSummary(qs.filter(q=>q.day===16),qs).total,150);assert.equal(api.examScoreSummary(qs.filter(q=>q.day===16),qs).known,110);assert.equal(api.examScoreSummary(qs.filter(q=>q.day===19),qs).total,150);assert.equal(api.examScoreSummary(qs.filter(q=>q.id==='2023-S02-Q02'),qs).total,null)})
check('学习备份与暂停记录可恢复，损坏备份不覆盖原数据',()=>{const before=JSON.stringify(api.read());assert.deepEqual(api.parseBackup(before),api.read());const corrupt=api.read();corrupt.exams[0].ids=null;assert.throws(()=>api.parseBackup(JSON.stringify(corrupt)));assert.equal(JSON.stringify(api.read()),before)})
check('重新练习清空当前答案与采分勾选，保留历史和考试评分',()=>{const q=qs.find(q=>q.year===2010&&!q.edited);api.attempt(q,'旧答案',0,'practice');const key=JSON.stringify(['practice',q.id,q.unitIds[0],'参考采分点',0]),examKey=JSON.stringify(['D19-test',q.id,q.unitIds[0],'参考采分点',0]);api.mutate(s=>{s.notes[q.id]='旧答案';s.markingChecks[key]=true;s.markingChecks[examKey]=true});const n=api.read().history.length;api.restartPractice(q.day,[q]);const state=api.read();assert.equal(state.progress[q.id],undefined);assert.equal(state.notes[q.id],undefined);assert.equal(state.markingChecks[key],undefined);assert.equal(state.markingChecks[examKey],true);assert.equal(state.history.length,n)})
check('正式考试组件渲染时没有答案与自评入口',()=>{const React=require('react'),{renderToStaticMarkup}=require('react-dom/server');const Q=moduleAt(root+'/src/components/OrganicQuestion.tsx').default;const html=renderToStaticMarkup(React.createElement(require('react-router').MemoryRouter,null,React.createElement(Q,{q,locked:true,draft:'A'})));assert(html.includes('交卷后开放答案'));assert(!html.includes('参考答案与逐步讲解'));assert(!html.includes('保存自评'))})
check('编辑修订条件在作答前可见，未提前显示解答',()=>{const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Q=moduleAt(root+'/src/components/OrganicQuestion.tsx').default,q=qs.find(q=>q.editorialStems?.length);assert(q);const html=renderToStaticMarkup(React.createElement(require('react-router').MemoryRouter,null,React.createElement(Q,{q,locked:true})));assert(html.includes('本次练习采用的明确修订'));assert(html.includes(q.editorialStems[0].unitIds[0]));assert(!html.includes('参考答案与逐步讲解'))})
check('93道模拟主观题采分分组与原总分逐题一致',()=>{const subjective=qs.filter(q=>q.year==null&&q.section!=='S02');assert.equal(subjective.length,93);for(const q of subjective){const groups=answers[q.id].units[0].markingPoints;assert(groups?.length,q.id);assert(groups.every(g=>g.points>0));assert.equal(groups.reduce((n,g)=>n+g.points,0),q.score,q.id);assert.equal(new Set(groups.map(g=>g.id)).size,groups.length)}})
check('采分勾选只记录核对，保留部分分和人工评分',()=>{const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Component=moduleAt(root+'/src/components/MarkingChecklist.tsx').default,id='A-S01-Q02',u=answers[id].units[0];const render=()=>renderToStaticMarkup(React.createElement(Component,{qid:id,unitId:u.id,context:'practice',groups:u.markingPoints,original:u.teaching['参考采分点']}));assert(render().includes('0.75分'));assert(render().includes('已核对0/3项'));const before=api.read().history.length;api.mutate(s=>{s.markingChecks[JSON.stringify(['practice',id,u.id,'weighted-reference-v1','P01'])]=true});assert(render().includes('已核对1/3项'));assert.equal(api.read().history.length,before);assert(render().includes('仍在下方自评总分'))})
check('96张完整教学卡正文可渲染且无KaTeX报错节点',()=>{const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),{MemoryRouter}=require('react-router'),{Card}=moduleAt(root+'/src/pages/OrganicPages.tsx');const failures=[];for(const card of cards){const html=renderToStaticMarkup(React.createElement(MemoryRouter,null,React.createElement(Card,{card})));if(html.includes('katex-error'))failures.push(card.id)}fs.writeFileSync(root+'/audit/CARD_RENDER_CHECKS.json',JSON.stringify({at:new Date().toISOString(),cards:cards.length,render_errors:failures,note:'正文和公式渲染检查；不替代化学复算和逐图视觉验收。'},null,2));assert.deepEqual(failures,[])})
check('全部静态SVG引用存在',()=>{for(const filename of fs.readdirSync(root+'/public/data').filter(f=>f.endsWith('.json'))){const text=fs.readFileSync(root+'/public/data/'+filename,'utf8');for(const ref of new Set(text.match(/assets\/[a-z0-9]+\.svg/g)||[]))assert(fs.existsSync(root+'/public/'+ref),ref)}})

check('D10—15集合不重不漏、只动day/difficulty，前九天与模拟卷不变',()=>{
 const before=JSON.parse(fs.readFileSync(root+'/audit/TARGETED_BEFORE.json','utf8'))
 const old=before.questions.filter(q=>q.year>=2013&&q.year<=2020),now=qs.filter(q=>q.day>=10&&q.day<=15)
 assert.deepEqual(now.map(q=>q.id).sort(),old.map(q=>q.id).sort());assert.equal(new Set(now.map(q=>q.id)).size,324)
 for(const q of qs){const prior=before.questions.find(p=>p.id===q.id);if(q.year>=2013&&q.year<=2020){const a={...q},b={...prior};for(const key of ['day','difficulty']){delete a[key];delete b[key]}assert.deepEqual(a,b)}else if(q.year!==2023)assert.deepEqual(q,prior)}
 for(const day of days.filter(d=>d.day>=10&&d.day<=15)){
  assert.deepEqual([...day.ids].sort(),qs.filter(q=>q.day===day.day).map(q=>q.id).sort())
  if(day.day>=12)assert(new Set(day.ids.map(id=>qs.find(q=>q.id===id).type)).size>=6)
 }
})
check('D08/D09分节互斥完整，进度及下一未完成不把仅展开算掌握',()=>{
 const tr=moduleAt(root+'/src/lib/training.ts')
 for(const day of [8,9]){const a=qs.filter(q=>q.day===day),groups=[...new Set(a.map(q=>tr.trainingSection(q,day,days[day-1].sections)))];assert(groups.length>=3);assert.equal(groups.reduce((n,g)=>n+a.filter(q=>tr.trainingSection(q,day,days[day-1].sections)===g).length,0),a.length)
 const records={};assert.equal(tr.trainingProgress(a,records).done,0)
 records[a[0].id]={status:'reviewed'};assert.equal(tr.trainingProgress(a,records).done,0)
 records[a[0].id]={status:'correct'};records[a[1].id]={status:'wrong'}
 assert.deepEqual(tr.trainingProgress(a,records),{done:2,total:a.length,percent:Math.round(2/a.length*100),mastered:1,wrong:1})
 assert.equal(tr.nextUnfinished(a,records,a[0].id).id,a[2].id)
 const order=[...a].reverse().map(q=>q.id);assert.deepEqual(tr.orderedDayQuestions(qs,order,day).map(q=>q.id),order)
 }
})
check('未核分题提交前不能记录，提交后正误不造分，重复核对不重复计次',()=>{
 const questions=qs.filter(q=>q.day===16),unknown=questions.find(q=>q.score==null),e=api.startExam(16,questions)
 api.assessUnscoredExam(e.id,unknown,'wrong');assert(!api.read().exams.at(-1).correctness)
 api.submitExam(e.id,questions);api.assessUnscoredExam(e.id,unknown,'wrong');api.assessUnscoredExam(e.id,unknown,'correct')
 const saved=api.read().exams.at(-1);assert.equal(saved.correctness[unknown.id],'correct');assert.equal(saved.scores[unknown.id],undefined);assert.equal(saved.graded[unknown.id],undefined)
 assert.equal(api.read().history.filter(h=>h.context===e.id&&h.qid===unknown.id).length,1)
 const roundtrip=api.parseBackup(JSON.stringify(api.read()));assert.equal(roundtrip.exams.at(-1).correctness[unknown.id],'correct')
 const real=questions.find(q=>q.score==null&&!q.edited);assert(real);api.assessUnscoredExam(e.id,real,'wrong');const rec=api.read().history.find(h=>h.context===e.id&&h.qid===real.id);assert.equal(api.practiceEvidence(qs,[rec]).length,1);assert(api.weaknessStats(qs,[rec]).some(k=>k.wrong===1));
 const again=api.startExam(16,questions);assert.notEqual(again.id,e.id);assert.equal(again.deadline-again.started,10800000);assert.deepEqual(again.scores,{})
})
check('2022/2023成绩仅显示已核110/146部分，未知不NaN或伪精确150',()=>{
 const React=require('react'),{renderToStaticMarkup}=require('react-dom/server'),Panel=moduleAt(root+'/src/components/ExamScorePanel.tsx').default
 for(const [day,known,unknown] of [[16,110,40],[17,146,4]]){
 const questions=qs.filter(q=>q.day===day),e=api.startExam(day,questions);e.submitted=1
 const html=renderToStaticMarkup(React.createElement(Panel,{exam:e,questions,all:qs}))
 assert(html.includes(`/${known}分`));assert(html.includes(`${unknown}分所属`));assert(!html.includes('NaN'));assert(!html.includes('0/150'))
 }
})

fs.writeFileSync(root+'/audit/FUNCTION_CHECKS.json',JSON.stringify({at:new Date().toISOString(),checks:results,browser_visual_verified:false,note:'真实数据、应用函数及服务端组件渲染验证；不冒充桌面/手机浏览器交互实测。'},null,2));console.log(JSON.stringify(results))
