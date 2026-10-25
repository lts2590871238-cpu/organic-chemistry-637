import { Content, VectorFigure } from './OrganicContent'
import MarkingChecklist from './MarkingChecklist'
import { mutate, useOrganic, type OUnit } from '../lib/organic'

/** Render the complete stored solution, including the revised teaching record. */
export default function AnswerUnit({unit:u,qid,context}:{unit:OUnit;qid:string;context:string}) {
 const s=useOrganic()
 function teaching(blocks:OUnit['teaching'],editorial=false) {
  return Object.entries(blocks||{}).map(([title,body])=><details key={title} open={/逐步|步骤|参考采分|基础|推导/.test(title)}>
   <summary>{title}</summary>
   {!editorial&&/采分/.test(title)&&u.markingPoints?.length
    ? <MarkingChecklist qid={qid} unitId={u.id} context={context} groups={u.markingPoints} original={body}/>
    : (Array.isArray(body)?body:[body]).map((text,i)=>{
      const key=JSON.stringify([context,qid,u.id,editorial?'editorial:'+title:title,i])
      return <div key={i}>{/采分/.test(title)&&<input type="checkbox" aria-label={`核对${editorial?'修订版':''}${title}第${i+1}项`} checked={!!s.markingChecks[key]} onChange={e=>mutate(s=>{s.markingChecks[key]=e.target.checked})}/>}<Content text={String(text)}/></div>
    })}
  </details>)
 }
 function original(){return <><Content text={u.answer}/>{u.derivation.length>0&&<ol>{u.derivation.map((step,i)=><li key={i}><Content text={step}/></li>)}</ol>}{teaching(u.teaching)}<details><summary>独立验算与条件检查</summary>{u.checks.map((step,i)=><Content key={i} text={step}/>)}</details></>}
 return <section className="unit-answer"><h4>{u.id}</h4>
  {u.editorial?<><section className="editorial-solution"><h4>明确修订版：答案与完整讲解</h4><Content text={u.editorial.question}/><Content text={u.editorial.answer}/>{teaching(u.editorial.teaching,true)}<p>本解析对应明确修订题；编辑内容不计真实考频，不能冒充原题唯一恢复。</p></section><details><summary>原题候选推导与待核说明（保留对照）</summary>{original()}</details></>:original()}
  {u.figures.length>0&&<section aria-label="完整解析图"><h4>{u.completeSolutionSource?'完整解析图（含全部续页）':'答案结构与推导图'}</h4>{u.figures.map((src,i)=><div key={src}>{u.figures.length>1&&<small>解析图 {i+1} / {u.figures.length}</small>}<VectorFigure src={src}/></div>)}</section>}
 </section>
}
