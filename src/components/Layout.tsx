import { NavLink } from 'react-router'
import { useState } from 'react'
import { useBundle } from '../lib/organic'

const NAV = [
  { to: '/', label: '学习计划', en: 'PLAN', end: true },
  { to: '/stage1', label: '知识点训练', en: '04-12' },
  { to: '/stage2', label: '分难度训练', en: '13-20' },
  { to: '/stage3', label: '限时真题', en: '22-23' },
  { to: '/prediction', label: '模拟考试', en: 'PREDICT' },
  { to: '/mistakes', label: '错题与巩固', en: 'REVIEW' },
  { to: '/analytics', label: '考情分析', en: 'TRENDS' },
  { to:'/spatial',label:'空间结构',en:'3D' },
]

export default function Layout({ children }: { children: React.ReactNode }) {
  const [menuOpen, setMenuOpen] = useState(false)
  const { data } = useBundle()
  return (
    <div className="shell">
      <aside className={`side ${menuOpen ? 'side-open' : ''}`}>
        <div className="side-brand">
          <div className="brand-kicker mono">🧪 NJTECH · 637</div>
          <h1 className="brand-title">637 有机化学<br /><span className="brand-plan">21天刷题站</span></h1>
          <div className="brand-sub">理解原理，独立解题</div>
        </div>
        <nav className="side-nav">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.end as boolean | undefined}
              className={({ isActive }) => `nav-item ${isActive ? 'nav-active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              <span className="nav-label">{n.label}</span>
              <span className="nav-en mono">{n.en}</span>
            </NavLink>
          ))}
        </nav>
        <div className="side-foot mono">
          学习足迹 · {new Date().toISOString().slice(0, 10)}
          <br />进度数据保存在本机浏览器
        </div>
      </aside>
      <div className="main">
        <header className="topbar">
          <button className="menu-btn mono" onClick={() => setMenuOpen(!menuOpen)}>MENU</button>
          <div className="topbar-line mono">
            <span>ORGANIC CHEMISTRY · 一起练会</span>
            <span className="topbar-dot">·</span>
            <span>{data?.questions.length ?? 0} 道接入题目 · {data?.cards.length ?? 0} 张卡</span>
            <span className="topbar-dot">·</span>
            <span>学懂原理 · 独立解题</span>
          </div>
        </header>
        <main className="content">{children}</main>
      </div>
    </div>
  )
}
