'use client';
import { useState } from 'react';
import { analyzePortfolio, Analysis, AssetSignal } from '@/lib/api';
import PriceChart from '@/components/PriceChart';

export default function Home(){
  const [tickers,setTickers]=useState('AAPL, MSFT, NVDA');
  const [risk,setRisk]=useState('balanced');
  const [horizon,setHorizon]=useState('medium-term');
  const [esg,setEsg]=useState(true);
  const [loading,setLoading]=useState(false);
  const [error,setError]=useState('');
  const [analysis,setAnalysis]=useState<Analysis|null>(null);
  async function submit(e:React.FormEvent){e.preventDefault();setLoading(true);setError('');try{setAnalysis(await analyzePortfolio(tickers,risk,esg,horizon));}catch(err){setError(err instanceof Error?err.message:'Something went wrong')}finally{setLoading(false)}}
  return <main className="container">
    <section className="hero">
      <span className="badge">Agentic AI · RAG-ready · LangGraph · FastAPI · Next.js</span>
      <h1>Financial Risk & Investment Copilot</h1>
      <p>An AI-native decision-support platform where specialized agents analyze market signals, ESG exposure, volatility risk, and portfolio allocation with human-review gates.</p>
      <form className="form" onSubmit={submit}>
        <input value={tickers} onChange={e=>setTickers(e.target.value)} placeholder="AAPL, MSFT, NVDA" />
        <select value={risk} onChange={e=>setRisk(e.target.value)}><option value="conservative">Conservative</option><option value="balanced">Balanced</option><option value="growth">Growth</option></select>
        <select value={horizon} onChange={e=>setHorizon(e.target.value)}><option value="short-term">Short-term</option><option value="medium-term">Medium-term</option><option value="long-term">Long-term</option></select>
        <label><input type="checkbox" checked={esg} onChange={e=>setEsg(e.target.checked)} /> ESG</label>
        <button disabled={loading}>{loading?'Analyzing...':'Run Agent Committee'}</button>
      </form>
      {error && <div className="error">{error}</div>}
    </section>

    {analysis && <section>
      <div className="grid">
        <div className="card"><h2>Portfolio Score</h2><div className="metric">{analysis.portfolio_score}/100</div><p className="muted">{analysis.recommendation}</p></div>
        <div className="card"><h2>Human Review</h2><div className="metric">{analysis.human_review_required?'Required':'Optional'}</div><p className="muted">Governance gate for risky or uncertain outputs.</p></div>
        <div className="card"><h2>Allocation Proposal</h2>{Object.entries(analysis.allocation).map(([k,v])=><div key={k}><b>{k}</b> {v}%<div className="bar"><span style={{width:`${v}%`}}/></div></div>)}</div>
      </div>
      <div className="grid two"><div className="card"><h2>AI Investment Committee Summary</h2><p style={{whiteSpace:'pre-line'}}>{analysis.ai_summary}</p></div><div className="card"><h2>Agent Trace</h2><div className="trace">{analysis.agent_trace.map((t,i)=><div className="traceItem" key={i}><b>{t.agent}</b><br/><span className="muted">{t.action}</span></div>)}</div></div></div>
      <div className="grid">{analysis.assets.map(asset=><AssetCard key={asset.ticker} asset={asset}/>)}</div>
      <p className="footer">{analysis.disclaimer}</p>
    </section>}
  </main>
}
function AssetCard({asset}:{asset:AssetSignal}){const chart=asset.metrics.chart||[];return <div className="card"><div className="asset"><div><div className="ticker">{asset.ticker}</div><div className="muted">{asset.name}</div></div><span className={`pill ${asset.signal.includes('RISK')?'danger':asset.signal==='HOLD'?'gold':''}`}>{asset.signal}</span></div><PriceChart data={chart}/><div className="grid" style={{gridTemplateColumns:'1fr 1fr 1fr',gap:10}}><Mini label="Score" value={`${asset.investment_score}`}/><Mini label="Risk" value={`${asset.risk_score}`}/><Mini label="ESG" value={`${asset.esg_score}`}/></div><p><b>{asset.price}</b> {asset.metrics.currency} · <span className={asset.daily_change_pct<0?'muted':''}>{asset.daily_change_pct}% today</span></p><div><span className="pill">RSI {asset.metrics.rsi}</span><span className="pill">MACD {asset.metrics.macd}</span><span className="pill">Vol {asset.metrics.volatility_pct}%</span></div><h3>Drivers</h3><ul>{asset.drivers.map((d,i)=><li key={i}>{d}</li>)}</ul><h3>Risks</h3><ul>{asset.risks.map((r,i)=><li key={i}>{r}</li>)}</ul></div>}
function Mini({label,value}:{label:string,value:string}){return <div><div className="muted">{label}</div><b>{value}</b></div>}
