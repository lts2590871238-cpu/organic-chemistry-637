import {Link} from 'react-router'
import {assessed,nextUnfinished,trainingProgress,trainingSection} from '../lib/training'
import type {Attempt,OCard,ODay,OQuestion} from '../lib/organic'
export default function TrainingSections({day,questions,records,minutes,current,cards,sections,onSelect}:{day:number;questions:OQuestion[];records:Record<string,Attempt>;minutes:number;current?:OQuestion;cards:OCard[];sections?:ODay['sections'];onSelect:(id:string,section:string)=>void}){
 const p=trainingProgress(questions,records),groups=[...new Set(questions.map(q=>trainingSection(q,day,sections)))]
 const sectionMethods=sections?.find(s=>current&&s.ids.includes(current.id))?.methodCards||[]
 const methods=current?cards.filter(c=>c.kind==='method'&&(sectionMethods.includes(c.id)||current.cards.includes(c.id)||c.points.some(k=>current.kp.includes(k)))):[]
 return <section className="panel training-progress" aria-label="本日学习进度">
  <p><strong>{questions.length}题</strong> · 本日完成 {p.done}/{p.total}（{p.percent}%） · 已掌握 {p.mastered} · 错题 {p.wrong}</p>
  <progress aria-label="本日完成比例" value={p.done} max={p.total||1}/>
  <p className="panel-note">预计作答 {minutes}分钟（编排估计，非实测；可分节多次完成）。完成按评分或自评正误记录计算，单纯展开解析不计掌握。</p>
  <p>{Object.entries(questions.reduce<Record<string,number>>((o,q)=>{o[q.type]=(o[q.type]||0)+1;return o},{})).map(([k,n])=>`${k} ${n}题`).join(' · ')}</p>
  <button className="btn" disabled={p.done===p.total} onClick={()=>{const q=nextUnfinished(questions,records,current?.id);if(q)onSelect(q.id,'all')}}>下一道未完成题</button>
  <details className="study-details"><summary>分节导航与进度 · {groups.length}节</summary>
   <button className="chip" onClick={()=>{if(questions[0])onSelect(questions[0].id,'all')}}>全部题目{day>=12?' · 混编顺序':''}</button>
   {groups.map(group=>{const rows=questions.filter(q=>trainingSection(q,day,sections)===group),s=trainingProgress(rows,records);return <details key={group} className="training-section">
    <summary>{group} · 完成 {s.done}/{s.total} · 掌握 {s.mastered} · 错题 {s.wrong}</summary>
    <button className="btn btn-ghost" onClick={()=>onSelect(rows.find(q=>!assessed(records[q.id]))?.id||rows[0].id,group)}>进入此节</button>
    <nav className="question-nav" aria-label={`${group}题目`}>{rows.map(q=><button className="chip" key={q.id} aria-pressed={q.id===current?.id} onClick={()=>onSelect(q.id,group)}>{q.id}{assessed(records[q.id])?' ✓':''}</button>)}</nav>
   </details>})}
  </details>
  {methods.length>0&&<details className="related-cards-details"><summary>返回当前知识点方法卡 · {methods.length}张</summary>{methods.map(c=><Link className="chip" key={c.id} to={`/card/${encodeURIComponent(c.id)}`}>{c.title}</Link>)}</details>}
 </section>
}
