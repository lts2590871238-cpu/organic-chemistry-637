import type {Attempt,OQuestion} from './organic'
export function assessed(a?:Attempt){return a?.status==='correct'||a?.status==='wrong'}
export function trainingProgress(qs:OQuestion[],records:Record<string,Attempt>){
 const done=qs.filter(q=>assessed(records[q.id])).length
 return {done,total:qs.length,percent:qs.length?Math.round(done/qs.length*100):0,
  mastered:qs.filter(q=>records[q.id]?.status==='correct').length,
  wrong:qs.filter(q=>records[q.id]?.status==='wrong').length}
}
export function trainingSection(q:OQuestion,day:number,sections?:{title:string;ids:string[]}[]){
 const existing=sections?.find(s=>s.ids.includes(q.id));if(existing)return existing.title
 const labels:Record<string,string>=day===8?{'K13':'醛酮','K14':'羧酸及其衍生物','K15':'双官能团化合物'}:day===9?{'K16':'胺及含氮化合物','K17':'杂环','K18':'糖','K19':'氨基酸与肽'}:{}
 if(day!==8&&day!==9)return q.type
 return labels[q.kp.find(k=>labels[k.slice(0,3)])?.slice(0,3)||'']||'跨知识点综合'
}
export function nextUnfinished(qs:OQuestion[],records:Record<string,Attempt>,current?:string){
 const at=qs.findIndex(q=>q.id===current)
 return [...qs.slice(at+1),...qs.slice(0,at+1)].find(q=>!assessed(records[q.id]))
}
export function orderedDayQuestions(qs:OQuestion[],ids:string[],day:number){
 const order=new Map(ids.map((id,i)=>[id,i]));return qs.filter(q=>q.day===day).sort((a,b)=>(order.get(a.id)??Infinity)-(order.get(b.id)??Infinity))
}
