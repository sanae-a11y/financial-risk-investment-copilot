from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    tickers: List[str] = Field(default=["AAPL", "MSFT", "NVDA"], min_length=1, max_length=8)
    risk_profile: str = "balanced"  # conservative, balanced, growth
    esg_preference: bool = True
    horizon: str = "medium-term"  # short-term, medium-term, long-term

class AssetSignal(BaseModel):
    ticker: str
    name: str
    price: float
    daily_change_pct: float
    signal: str
    investment_score: int
    confidence: int
    risk_score: int
    esg_score: int
    metrics: Dict[str, Any]
    drivers: List[str]
    risks: List[str]

class AnalyzeResponse(BaseModel):
    portfolio_score: int
    recommendation: str
    risk_profile: str
    assets: List[AssetSignal]
    allocation: Dict[str, float]
    agent_trace: List[Dict[str, str]]
    ai_summary: str
    human_review_required: bool
    disclaimer: str
