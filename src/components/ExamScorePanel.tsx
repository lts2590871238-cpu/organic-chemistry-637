import {examScoreSummary,type Exam,type OQuestion} from '../lib/organic'
export default function ExamScorePanel({exam,questions,all}:{exam:Exam;questions:OQuestion[];all:OQuestion[]}){
 const summary=examScoreSummary(questions,all),known=questions.filter(q=>q.score!=null),unknown=questions.filter(q=>q.score==null)
 const earned=known.reduce((n,q)=>n+(exam.graded[q.id]&&Number.isFinite(exam.scores[q.id])?exam.scores[q.id]:0),0)
 const reviewed=unknown.filter(q=>exam.correctness?.[q.id]).length,correct=unknown.filter(q=>exam.correctness?.[q.id]==='correct').length,wrong=unknown.filter(q=>exam.correctness?.[q.id]==='wrong').length
 return <section className="exam-score-panel" aria-label="成绩与未核分值说明">
  <h3>已交卷 · 已核定题目得分：{earned}/{summary.known}分</h3>
  <p>已评 {known.filter(q=>exam.graded[q.id]).length}/{known.length} 道已核分题。未自评的主观题尚未评定，不视为0分或满分；上述为当前已录得分。</p>
  {unknown.length>0&&<><p role="status">另有{summary.unallocated!=null?`${summary.unallocated}分所属的`:''}{unknown.length}道小题尚未完成分值核定，已提供答案核对，暂不计入正式得分。不按比例换算为150分。</p>
   <p>未核分题已核对 {reviewed}/{unknown.length} · 自评掌握 {correct} · 自评有误 {wrong}。这些是正确性记录，不是精确分数。</p></>}
  <p>{[...new Set(questions.map(q=>q.type))].map(type=>{
   const group=questions.filter(q=>q.type===type),scored=group.filter(q=>q.score!=null),missing=group.length-scored.length
   return `${type}：${scored.length?`${scored.reduce((n,q)=>n+(exam.graded[q.id]?exam.scores[q.id]||0:0),0)}/${scored.reduce((n,q)=>n+q.score!,0)}分`:''}${missing?`${scored.length?'；':''}${missing}题分值待核`:''}`
  }).join(' · ')}</p>
 </section>
}
