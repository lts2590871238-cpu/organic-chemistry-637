import { Route, Routes, Navigate } from 'react-router'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import { ExamPage, Mistakes, AnalyticsPage, CardPage, QuestionPage } from './pages/OrganicPages'
import Training from './pages/TrainingPage'
import SpatialPage from './pages/SpatialPage'
export default function App(){return <Layout><Routes><Route path="/" element={<HomePage/>}/><Route path="/stage1" element={<Training/>}/><Route path="/stage2" element={<Training stage={2}/>}/><Route path="/exam" element={<ExamPage/>}/><Route path="/stage3" element={<Navigate to="/exam?day=16" replace/>}/><Route path="/prediction" element={<Navigate to="/exam?day=19" replace/>}/><Route path="/mistakes" element={<Mistakes/>}/><Route path="/analytics" element={<AnalyticsPage/>}/><Route path="/card/:id" element={<CardPage/>}/><Route path="/question/:id" element={<QuestionPage/>}/><Route path="/spatial" element={<SpatialPage/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Routes></Layout>}
