export type AssetSignal = {
  ticker: string;
  name: string;
  price: number;
  daily_change_pct: number;
  signal: string;
  investment_score: number;
  confidence: number;
  risk_score: number;
  esg_score: number;
  metrics: Record<string, any>;
  drivers: string[];
  risks: string[];
};
export type Analysis = {
  portfolio_score: number;
  recommendation: string;
  risk_profile: string;
  assets: AssetSignal[];
  allocation: Record<string, number>;
  agent_trace: { agent: string; action: string }[];
  ai_summary: string;
  human_review_required: boolean;
  disclaimer: string;
};
export async function analyzePortfolio(tickers: string, risk_profile: string, esg_preference: boolean, horizon: string): Promise<Analysis> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const response = await fetch(`${apiUrl}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ tickers: tickers.split(',').map(t => t.trim()).filter(Boolean), risk_profile, esg_preference, horizon }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || 'Failed to analyze portfolio');
  }
  return response.json();
}
