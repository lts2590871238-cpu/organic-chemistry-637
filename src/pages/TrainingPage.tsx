import { useState } from 'react'
import { useSearchParams } from 'react-router'
import { Card } from './OrganicPages'
import TrainingSections from '../components/TrainingSections'
import { assessed, orderedDayQuestions, trainingSection } from '../lib/training'
import OrganicQuestion from '../components/OrganicQuestion'
import { mutate, restartPractice, useBundle, useOrganic } from '../lib/organic'

export default function TrainingPage({stage=1}:{stage?:number}) {
  const {data,error}=useBundle(),s=useOrganic(),[params,setParams]=useSearchParams()
  const [view,setView]=useState(params.get('view')||'knowledge'),[search,setSearch]=useState(''),[filter,setFilter]=useState('all'),[position,setPosition]=useState(0)
  if(!data)return <div className="loading">{error||'加载学习内容…'}</div>
  const requestedDay=Number(params.get('day')),day=(stage===1?requestedDay>=1&&requestedDay<=9:requestedDay>=10&&requestedDay<=15)&&Number.isInteger(requestedDay)?requestedDay:(stage===1?1:10),d=data.days[day-1]
  const enhanced=day>=8&&day<=15,section=enhanced?(params.get('section')||'all'):'all'
  const all=enhanced?orderedDayQuestions(data.questions,d.ids,day):data.questions.filter(q=>q.day===day)
  const qs=all.filter(q=>(section==='all'||trainingSection(q,day,d.sections)===section)&&(!search||`${q.id} ${q.raw} ${q.kp.join(' ')}`.includes(search))&&(filter==='all'||(filter==='wrong'?s.progress[q.id]?.status==='wrong':(enhanced?!assessed(s.progress[q.id]):!s.progress[q.id]))))
  const saved=enhanced?qs.findIndex(q=>q.id===params.get('question')):-1
  const current=saved>=0?saved:Math.min(position,Math.max(0,qs.length-1)),q=qs[current]
  function go(id:string,group=section,resetFilters=false){setPosition(0);setView('practice');if(resetFilters){setSearch('');setFilter('all')}setParams({day:String(day),view:'practice',question:id,...(group==='all'?{}:{section:group})})}
  const currentCards=data.cards.filter(c=>c.day===day&&c.kind===(view==='method'?'method':'knowledge'))
  const practicing=stage===2||view==='practice'
  return <div className="page clean-training">
    <div className="day-switch" aria-label="训练日">{data.days.filter(x=>stage===1?x.day<=9:x.day>=10&&x.day<=15).map(x=><button key={x.day} title={x.title} aria-pressed={x.day===day} onClick={()=>{setParams({day:String(x.day)});setPosition(0);setSearch('')}}>D{String(x.day).padStart(2,'0')}</button>)}</div>
    <header className="page-head"><p className="eyebrow">第 {day} 天</p><h2 className="page-title">{d.title}</h2><p className="page-sub">{stage===1?'理解知识，掌握方法，再独立练题。':'按实际推理要求编排；简单题递进，中等和困难题混编。'}</p></header>
    {enhanced&&<TrainingSections day={day} questions={all} records={s.progress} minutes={d.minutes??all.reduce((n,q)=>n+({D2:3,D3:7,D4:12}[q.difficulty]||5),0)} current={q} cards={data.cards} sections={d.sections} onSelect={(id,group)=>go(id,group,true)}/>}
    {stage===1&&<nav className="learning-tabs" aria-label="学习步骤">{[['knowledge','知识复习'],['method','解题方法'],['practice','真题训练']].map(([id,t])=><button key={id} className={view===id?'active':''} aria-pressed={view===id} onClick={()=>{setView(id);if(enhanced)setParams(p=>{p.set('view',id);return p})}}>{t}</button>)}</nav>}
    {!practicing?<section className="lesson-stack">{currentCards.map(c=><Card key={c.id} card={c}/>)}</section>:<section>
      <div className="practice-toolbar"><input aria-label="搜索本日真题" type="search" placeholder="搜索题号或知识点" value={search} onChange={e=>{setSearch(e.target.value);setPosition(0);if(enhanced)setParams(p=>{p.delete('question');return p})}}/><select aria-label="题目筛选" value={filter} onChange={e=>{setFilter(e.target.value);setPosition(0);if(enhanced)setParams(p=>{p.delete('question');return p})}}><option value="all">全部题目</option><option value="todo">{enhanced?'尚未完成':'尚未练习'}</option><option value="wrong">错题重练</option></select><span>{all.filter(q=>enhanced?assessed(s.progress[q.id]):!!s.progress[q.id]).length} / {all.length} {enhanced?'已完成':'已练'}</span></div>
      {q?<><div className="question-pager"><button className="btn btn-ghost" disabled={current===0} onClick={()=>enhanced?go(qs[current-1].id):setPosition(current-1)}>上一题</button><span>第 {current+1} / {qs.length} 题</span><button className="btn btn-ghost" disabled={current>=qs.length-1} onClick={()=>enhanced?go(qs[current+1].id):setPosition(current+1)}>下一题</button></div><OrganicQuestion key={q.id+':'+(s.retryStarted[q.id]||0)} q={q}/></>:<p className="empty">没有符合筛选的题目。</p>}
    </section>}
    <details className="study-details"><summary>当天进度与学习管理</summary><p>{all.length}道真实父题 · 已练{all.filter(q=>s.progress[q.id]).length} · 错题{all.filter(q=>s.progress[q.id]?.status==='wrong').length}</p><p>{Object.entries(all.reduce<Record<string,number>>((o,q)=>{o[q.type]=(o[q.type]||0)+1;return o},{})).map(([k,n])=>`${k} ${n}题`).join(' · ')}</p><button className="btn" onClick={()=>mutate(s=>{s.daysDone[String(day)]=!s.daysDone[String(day)]})}>{s.daysDone[String(day)]?'取消今日完成标记':'标记今日学习完成'}</button><button className="btn btn-ghost" onClick={()=>restartPractice(day,all)}>重新练习 · 保留历史</button></details>
  </div>
}
