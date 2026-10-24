import { mutate, useOrganic } from '../lib/organic'
import { Content } from './OrganicContent'

export interface MarkingPoint {id:string;label:string;points:number}

export default function MarkingChecklist({qid,unitId,context,groups,original}:{qid:string;unitId:string;context:string;groups:MarkingPoint[];original:string|string[]}){
 const state=useOrganic()
 const key=(id:string)=>JSON.stringify([context,qid,unitId,'weighted-reference-v1',id])
 const reviewed=groups.filter(p=>state.markingChecks[key(p.id)]).length
 return <div className="marking-points">
  <p>参考分组共{groups.reduce((n,p)=>n+p.points,0)}分，已核对{reviewed}/{groups.length}项。非官方评分；勾选只记录已核对，部分分和等价解法仍在下方自评总分。</p>
  {groups.map(p=><div className="marking-point-row" key={p.id}>
   <input type="checkbox" aria-label={`核对采分点 ${p.id} ${unitId}`} checked={!!state.markingChecks[key(p.id)]} onChange={e=>mutate(s=>{s.markingChecks[key(p.id)]=e.target.checked})}/>
   <Content text={p.label}/><span>{p.points}分</span>
  </div>)}
  <details><summary>原始采分建议</summary>{(Array.isArray(original)?original:[original]).map((line,i)=><Content key={i} text={line}/>)}</details>
 </div>
}
