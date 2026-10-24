import { Link } from 'react-router'
import { useBundle, useOrganic, mutate } from '../lib/organic'
import type { PlanDay } from '../lib/types'

const STAGE_META: Record<string, { name: string; color: string }> = {
  S1: { name: '阶段一', color: 'stage-s1' },
  S2: { name: '阶段二', color: 'stage-s2' },
  S3: { name: '阶段三', color: 'stage-s3' },
  P: { name: '预测', color: 'stage-p' },
}

function dayLink(d: PlanDay): string { return d.day <= 9 ? `/stage1?day=${d.day}` : d.day <= 15 ? `/stage2?day=${d.day}` : `/exam?day=${d.day}` }

export default function HomePage() {
  const {data,error}=useBundle()
  const {progress,daysDone}=useOrganic()
  if(!data)return <div className="loading">{error||'装载21天作战图…'}</div>
  const questions=data.questions
  const plan={days:data.days.map(d=>({day:d.day,title:d.title,stage:d.day<=9?'S1':d.day<=15?'S2':d.day<=18?'S3':'P',kind:'module' as const,ref:String(d.day),est:d.day>=16?'180分钟':'学习 + 练习',note:d.day===18?'按个人记录生成':`${d.ids.length}题${d.cards.length?` · ${d.cards.length}卡`:''}`}))}

  const drillable = questions.filter((q) => q.year != null && q.year <= 2023)
  const done = drillable.filter((q) => progress[q.id]).length
  const correct = drillable.filter((q) => progress[q.id]?.status === 'correct').length
  const wrong = drillable.filter((q) => progress[q.id]?.status === 'wrong').length
  const daysCompleted = Object.values(daysDone).filter(Boolean).length

  return (
    <div className="home">
      <section className="hero">
        
        <div className="hero-kicker mono">🌿 南京工业大学 · 637 有机化学 · 考研冲刺</div>
        <h2 className="hero-title">每天一步，学会有机。</h2>
        <p className="hero-sub">
          从知识复习，到真题训练，再到限时模拟。
        </p>
        <div className="hero-stats">
          <div className="hstat"><b className="mono">{done}</b><span>/ {drillable.length} 已练</span></div>
          <div className="hstat"><b className="mono">{correct}</b><span>已掌握</span></div>
          <div className="hstat hstat-warn"><b className="mono">{wrong}</b><span>在错题本</span></div>
          <div className="hstat"><b className="mono">{daysCompleted}</b><span>/ 21 天完成</span></div>
        </div>
      </section>

      <section className="stage-cards">
        <Link to="/stage1" className="scard stage-s1">
          <div className="scard-no mono">🌱 01 · 打基础</div>
          <h4>模块精练</h4>
          <p>2004–2012年按知识点聚类，完整知识卡与方法卡，先学再练</p>
        </Link>
        <Link to="/stage2" className="scard stage-s2">
          <div className="scard-no mono">🧩 02 · 会组合</div>
          <h4>混库成套</h4>
          <p>2013–2020年按既有难度拆成6天：简单 → 中等 → 困难</p>
        </Link>
        <Link to="/exam?day=16" className="scard stage-s3">
          <div className="scard-no mono">⏱️ 03 · 练速度</div>
          <h4>掐时自测</h4>
          <p>2022、2023两年整卷，180分钟计时，交卷后解锁答案</p>
        </Link>
        <Link to="/exam?day=19" className="scard stage-p">
          <div className="scard-no mono">✨ 04 · 做整卷</div>
          <h4>模拟卷 A / B / C</h4>
          <p>四本真实参考书选题，共129题；A近期型、B综合型、C强化型</p>
        </Link>
      </section>

      <section className="plan">
        <h3 className="sec-title">21 天作战图 <span className="sec-sub mono">点击任意一天直达训练场</span></h3>
        <div className="plan-list">
          {plan.days.map((d) => {
            const doneDay = !!daysDone[String(d.day)]
            return (
              <div key={d.day} className={`day ${doneDay ? 'day-done' : ''}`}>
                <div className="day-num mono">D{d.day}</div>
                <span className={`day-stage ${STAGE_META[d.stage]?.color}`}>{STAGE_META[d.stage]?.name}</span>
                <Link to={dayLink(d)} className="day-title">{d.title}</Link>
                <span className="day-meta"><span className="day-est mono">{d.est}</span><span className="day-note">{d.note}</span></span>
                <button
                  className={`day-check ${doneDay ? 'day-check-on' : ''}`}
                  onClick={() => mutate(s=>{s.daysDone[String(d.day)]=!doneDay})}
                  title={doneDay ? '取消完成标记' : '标记今日完成'}
                >{doneDay ? '✓' : ''}</button>
              </div>
            )
          })}
        </div>
      </section>
    </div>
  )
}
