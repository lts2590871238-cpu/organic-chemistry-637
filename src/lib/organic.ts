import { useEffect, useState } from 'react'
export interface OQuestion { id:string; year:number|null; no:number; section:string; type:string; score:number|null; sectionScore?:number; raw:string; kp:string[]; cards:string[]; unitIds:string[]; difficulty:string; day:number; source:{book:string;page?:string|number;exercise?:string;paper?:string;printedPage?:string|number|number[];pdfPage?:string|number|number[]}; answerKey?:string|null;optionLabels?:string[]; edited?:boolean;editorialStems?:{unitIds:string[];text:string}[]; auditStatus:string }
export interface OCard {id:string;day:number;kind:string;title:string;body:string;points:string[];linkedParents:string[];figures:string[];sources:string[]}
export interface ODay {day:number;title:string;ids:string[];cards:string[];minutes:number|null;sections?:{title:string;ids:string[];methodCards:string[]}[]}
export interface OUnit {completeSolutionSource?:{pdf:string;pages:number[];nativeVector:boolean};id:string;answer:string;derivation:string[];checks:string[];teaching:Record<string,string[]|string>;figures:string[];markingPoints?:{id:string;label:string;points:number}[];editorial?:{question:string;answer:string;teaching:Record<string,string[]|string>}}
export interface OAnswer {units:OUnit[];missing:boolean;final_accepted:boolean}
export interface Bundle {questions:OQuestion[];cards:OCard[];days:ODay[]}
const memo=new Map<string,Promise<unknown>>()
export function load<T>(name:string):Promise<T>{if(!memo.has(name))memo.set(name,fetch(import.meta.env.BASE_URL+'data/'+name+'.json').then(r=>{if(!r.ok)throw Error(`内容加载失败 ${r.status}: ${name}`);return r.json()}));return memo.get(name) as Promise<T>}
export const loadBundle=():Promise<Bundle>=>Promise.all([load<OQuestion[]>('questions'),load<OCard[]>('cards'),load<ODay[]>('days')]).then(([questions,cards,days])=>({questions,cards,days}))
export function useBundle(){const [data,setData]=useState<Bundle>();const [error,setError]=useState('');useEffect(()=>{loadBundle().then(setData).catch(e=>setError(String(e)))},[]);return {data,error}}
export const loadAnswers=()=>load<Record<string,OAnswer>>('answers')
export function examScoreSummary(qs:OQuestion[],all:OQuestion[]){
 const known=qs.reduce((n,q)=>n+(q.score??0),0),unknown=qs.filter(q=>q.score==null).length
 const year=qs[0]?.year,wholeOriginal=year!=null&&qs.every(q=>q.year===year)&&all.filter(q=>q.year===year).every(q=>qs.some(x=>x.id===q.id))
 const groups=new Map<string,OQuestion[]>();for(const q of qs){const key=`${q.year??q.day}-${q.section}`;groups.set(key,[...(groups.get(key)||[]),q])}
 let total=0,complete=qs.length>0
 for(const group of groups.values()){
  const first=group[0],whole=all.filter(q=>q.year===first.year&&q.day===first.day&&q.section===first.section)
  const printed=[...new Set(group.map(q=>q.sectionScore).filter((n):n is number=>n!=null&&Number.isFinite(n)))]
  if(wholeOriginal&&printed.length===1&&group.length===whole.length&&whole.every(q=>group.some(x=>x.id===q.id)))total+=printed[0]
  else if(group.every(q=>q.score!=null))total+=group.reduce((n,q)=>n+q.score!,0)
  else complete=false
 }
 const originalTotal=wholeOriginal&&(year===2022||year===2023)?150:null
 const confirmedTotal=originalTotal??(complete?total:null)
 return {known,unknown,total:confirmedTotal,unallocated:confirmedTotal!=null?Math.max(0,confirmedTotal-known):null}
}
export interface Attempt {qid:string;ts:number;status:'correct'|'wrong'|'reviewed';score?:number;full?:number;answer:string;context:string;kp:string[];type:string}
export interface Exam {id:string;day:number;ids:string[];started:number;deadline:number;pausedAt?:number|null;remainingMs?:number;submitted:number|null;drafts:Record<string,string>;paperDone:Record<string,boolean>;scores:Record<string,number>;graded:Record<string,boolean>;correctness?:Record<string,'correct'|'wrong'|'reviewed'>;reasons?:Record<string,string>}
interface State {progress:Record<string,Attempt>;history:Attempt[];savedIds:Record<string,boolean>;cardsDone:Record<string,boolean>;daysDone:Record<string,boolean>;exams:Exam[];notes:Record<string,string>;retryStarted:Record<string,number>;markingChecks:Record<string,boolean>}
const KEY='organic637.v1';const listeners=new Set<()=>void>();const empty=():State=>({progress:{},history:[],savedIds:{},cardsDone:{},daysDone:{},exams:[],notes:{},retryStarted:{},markingChecks:{}})
export function parseBackup(text:string):State{
 const x=JSON.parse(text),object=(v:unknown):v is Record<string,unknown>=>!!v&&typeof v==='object'&&!Array.isArray(v)
 const numeric=(v:unknown)=>typeof v==='number'&&Number.isFinite(v)&&v>=0
 const dict=(v:unknown,test:(n:unknown)=>boolean)=>object(v)&&Object.values(v).every(test)
 const record=(v:unknown)=>object(v)&&typeof v.qid==='string'&&numeric(v.ts)&&['correct','wrong','reviewed'].includes(String(v.status))&&typeof v.answer==='string'&&typeof v.context==='string'&&typeof v.type==='string'&&Array.isArray(v.kp)&&v.kp.every(k=>typeof k==='string')&&(v.score==null||numeric(v.score))&&(v.full==null||numeric(v.full))
 if(!object(x)||!Array.isArray(x.history)||!x.history.every(record)||!dict(x.progress,record)||!Array.isArray(x.exams))throw Error('备份中的作答记录不完整，未恢复任何数据。')
 for(const e of x.exams){if(!object(e)||typeof e.id!=='string'||!Number.isInteger(e.day)||Number(e.day)<16||Number(e.day)>21||!Array.isArray(e.ids)||!e.ids.every(id=>typeof id==='string')||!numeric(e.started)||!numeric(e.deadline)||(e.submitted!=null&&!numeric(e.submitted))||(e.pausedAt!=null&&(!numeric(e.pausedAt)||!numeric(e.remainingMs)))||!dict(e.drafts,v=>typeof v==='string')||!dict(e.paperDone,v=>typeof v==='boolean')||!dict(e.scores,numeric)||!dict(e.graded,v=>typeof v==='boolean')||(e.correctness!=null&&!dict(e.correctness,v=>['correct','wrong','reviewed'].includes(String(v))))||(e.reasons!=null&&!dict(e.reasons,v=>typeof v==='string')))throw Error('备份中的考试或暂停记录无效，未恢复任何数据。')}
 const result=empty()
 for(const key of ['savedIds','cardsDone','daysDone','markingChecks'] as const){if(x[key]!=null&&!dict(x[key],v=>typeof v==='boolean'))throw Error('备份学习标记无效');if(x[key])result[key]=x[key] as Record<string,boolean>}
 if(x.notes!=null&&!dict(x.notes,v=>typeof v==='string'))throw Error('备份笔记无效')
 if(x.retryStarted!=null&&!dict(x.retryStarted,numeric))throw Error('备份重练记录无效')
 return {...result,progress:x.progress as State['progress'],history:x.history as Attempt[],exams:x.exams as Exam[],notes:(x.notes||{}) as State['notes'],retryStarted:(x.retryStarted||{}) as State['retryStarted']}
}
export function read():State{try{return {...empty(),...JSON.parse(localStorage.getItem(KEY)||'{}')}}catch{return empty()}}
export function mutate(fn:(s:State)=>void){const s=read();fn(s);localStorage.setItem(KEY,JSON.stringify(s));listeners.forEach(f=>f())}
export function restartPractice(day:number,qs:OQuestion[]){const ids=new Set(qs.map(q=>q.id)),now=Date.now();mutate(s=>{for(const id of ids){delete s.progress[id];delete s.notes[id];s.retryStarted[id]=now}for(const key of Object.keys(s.markingChecks)){try{const [context,qid]=JSON.parse(key);if(context==='practice'&&ids.has(qid))delete s.markingChecks[key]}catch{/* Unknown legacy keys are retained. */}}s.daysDone[String(day)]=false})}
export function useOrganic(){const [,tick]=useState(0);useEffect(()=>{const f=()=>tick(n=>n+1);listeners.add(f);const sync=(e:StorageEvent)=>{if(e.key===KEY)f()};window.addEventListener('storage',sync);return()=>{listeners.delete(f);window.removeEventListener('storage',sync)}},[]);return read()}
export function attempt(q:OQuestion,answer:string,score:number|undefined,context:string,selfStatus?:Attempt['status']){const rec:Attempt={qid:q.id,ts:Date.now(),status:selfStatus??(score==null?'reviewed':score>=(q.score??1)?'correct':'wrong'),score,full:q.score??undefined,answer,context,kp:q.kp,type:q.type};mutate(s=>{s.progress[q.id]=rec;const prev=/^D\d+-/.test(context)?s.history.findIndex(a=>a.context===context&&a.qid===q.id):-1;if(prev>=0)s.history[prev]=rec;else s.history.push(rec)})}
export function gradeChoice(q:OQuestion,text:string):number|undefined{
 if(!q.answerKey||q.score==null)return undefined
 const norm=(x:string)=>x.toUpperCase().replace(/[()（）\s、,，.。]/g,'').split('').sort().join('')
 if(/[;；]/.test(q.answerKey)){const key=q.answerKey.split(/[;；]/),xs=text.split(/[;；]/);return key.reduce((n,k,i)=>n+(norm(k)===norm(xs[i]||'')?q.score!/key.length:0),0)}
 return norm(text)===norm(q.answerKey)?q.score:0
}
export function startExam(day:number,questions:OQuestion[],reasons?:Record<string,string>){const now=Date.now(),base=`D${day}-${now}`;let id=base,suffix=0;while(read().exams.some(e=>e.id===id))id=`${base}-${++suffix}`;const e:Exam={id,day,ids:questions.map(q=>q.id),started:now,deadline:now+180*60*1000,submitted:null,drafts:{},paperDone:{},scores:{},graded:{},reasons};mutate(s=>s.exams.push(e));return e}
export function patchExam(id:string,fn:(e:Exam)=>void){mutate(s=>{const e=s.exams.find(e=>e.id===id);if(e)fn(e)})}
export function assessUnscoredExam(id:string,q:OQuestion,status:'correct'|'wrong'|'reviewed'){
 const e=read().exams.find(e=>e.id===id)
 if(!e?.submitted||q.score!=null||!e.ids.includes(q.id))return
 patchExam(id,x=>{x.correctness={...x.correctness,[q.id]:status}})
 attempt(q,e.drafts[q.id]||'',undefined,id,status)
}
export function pauseExam(id:string){const now=Date.now();patchExam(id,e=>{if(e.submitted||e.pausedAt!=null||now>=e.deadline)return;e.remainingMs=e.deadline-now;e.pausedAt=now})}
export function resumeExam(id:string){const now=Date.now();patchExam(id,e=>{if(e.submitted||e.pausedAt==null)return;e.deadline=now+Math.max(0,e.remainingMs??0);e.pausedAt=null;delete e.remainingMs})}
export function submitExam(id:string,qs:OQuestion[]){mutate(s=>{const e=s.exams.find(x=>x.id===id);if(!e||e.submitted)return;e.submitted=e.pausedAt!=null?Date.now():Math.min(Date.now(),e.deadline);for(const q of qs){const score=gradeChoice(q,e.drafts[q.id]||'');if(score!=null){e.scores[q.id]=score;e.graded[q.id]=true;const rec:Attempt={qid:q.id,ts:Date.now(),status:score===(q.score??0)?'correct':'wrong',score,full:q.score??undefined,answer:e.drafts[q.id]||'',context:e.id,kp:q.kp,type:q.type};s.history.push(rec);s.progress[q.id]=rec}}})}
export function practiceEvidence(qs:OQuestion[],history:Attempt[]){const ids=new Set(qs.filter(q=>q.year!=null&&q.year<=2023&&q.day<=17&&!q.edited).map(q=>q.id));return history.filter(a=>ids.has(a.qid)&&!/^D18-/.test(a.context)&&(a.status==='correct'||a.status==='wrong'))}
export function weaknessStats(qs:OQuestion[],history:Attempt[]){
 const stats=new Map<string,{point:string;n:number;wrong:number;loss:number;questionIds:string[]}>()
 for(const a of practiceEvidence(qs,history))for(const point of new Set(a.kp)){const v=stats.get(point)||{point,n:0,wrong:0,loss:0,questionIds:[]};v.n++;v.wrong+=a.status==='wrong'?1:0;v.loss+=a.score!=null&&a.full?Math.min(1,Math.max(0,(a.full-a.score)/a.full)):a.status==='wrong'?1:0;if(!v.questionIds.includes(a.qid))v.questionIds.push(a.qid);stats.set(point,v)}
 return [...stats.values()].sort((a,b)=>b.loss/b.n-a.loss/a.n||b.wrong-a.wrong||a.point.localeCompare(b.point))
}
export function makeReview(qs:OQuestion[],history:Attempt[]){
 const eligible=qs.filter(q=>q.year!=null&&q.year<=2023&&q.score!=null&&!q.edited)
 const evidence=practiceEvidence(qs,history)
 const stats=new Map<string,{n:number;loss:number}>(),types=new Map<string,{n:number;loss:number}>()
 for(const a of evidence){
  const loss=a.score!=null&&a.full&&Number.isFinite(a.score)?Math.min(1,Math.max(0,(a.full-a.score)/a.full)):a.status==='wrong'?1:0
  const ty=types.get(a.type)||{n:0,loss:0};ty.n++;ty.loss+=loss;types.set(a.type,ty)
  for(const k of new Set(a.kp)){const s=stats.get(k)||{n:0,loss:0};s.n++;s.loss+=loss;stats.set(k,s)}
 }
 const ranked=eligible.map(q=>{
  const ss=q.kp.map(k=>stats.get(k)).filter(Boolean) as {n:number;loss:number}[]
  const priority=ss.length?Math.max(...ss.map(s=>(s.loss+1)/(s.n+2))):.5
  const repeats=evidence.filter(a=>a.qid===q.id&&a.status==='wrong').length
  const ty=types.get(q.type)
  return {q,priority:priority+Math.min(repeats,3)*.05+(ty?((ty.loss+1)/(ty.n+2))*.15:0),why:ss.length?`按已评分作答的错误率、失分和重复错误选入；关联知识点证据最多 ${Math.max(...ss.map(s=>s.n))} 次${Math.max(...ss.map(s=>s.n))<3?'，证据不足，建议性选题':''}`:'尚缺已评分作答证据，选作覆盖训练'}
 }).sort((a,b)=>b.priority-a.priority||a.q.id.localeCompare(b.q.id))
 // Use each original question at most once. Prefer an exact 150 using its real
 // score; never change a question's points to fill a greedy one-point gap.
 const best=new Map<number,{value:number;indices:number[]}>([[0,{value:0,indices:[]}]])
 ranked.forEach((x,i)=>{const score=x.q.score??0,cost=Math.round(score*100);if(cost<=0||Math.abs(cost/100-score)>1e-8)return
  for(const [sum,path] of [...best]){const next=sum+cost;if(next>15000)continue;const value=path.value+x.priority*score;if(!best.has(next)||value>best.get(next)!.value+1e-9)best.set(next,{value,indices:[...path.indices,i]})}
 })
 const target=best.has(15000)?15000:Math.max(...best.keys()),selected=new Set(best.get(target)!.indices)
 const chosen:OQuestion[]=[],reasons:Record<string,string>={}
 ranked.forEach((x,i)=>{if(selected.has(i)){chosen.push(x.q);reasons[x.q.id]=x.why}})
 return {questions:chosen,reasons}
}
