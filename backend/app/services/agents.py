from __future__ import annotations
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from app.services.market_service import fetch_asset

class CopilotState(TypedDict, total=False):
    tickers: List[str]
    risk_profile: str
    esg_preference: bool
    horizon: str
    assets_raw: List[Dict[str, Any]]
    assets: List[Dict[str, Any]]
    allocation: Dict[str, float]
    recommendation: str
    portfolio_score: int
    human_review_required: bool
    agent_trace: List[Dict[str, str]]


def trace(state: CopilotState, agent: str, action: str) -> None:
    state.setdefault("agent_trace", []).append({"agent": agent, "action": action})


def market_data_agent(state: CopilotState) -> CopilotState:
    assets = []
    for ticker in state["tickers"]:
        assets.append(fetch_asset(ticker))
    state["assets_raw"] = assets
    trace(state, "Market Data Agent", "Fetched Yahoo Finance price history, metadata, volume and computed raw indicators.")
    return state


def risk_agent(state: CopilotState) -> CopilotState:
    enriched = []
    for asset in state["assets_raw"]:
        m = asset["metrics"]
        risk = 0
        risk += min(35, int(m["volatility_pct"] * 0.9))
        risk += min(30, int(m["max_drawdown_pct"] * 0.8))
        risk += 15 if m["rsi"] > 70 or m["rsi"] < 30 else 5
        risk += 10 if asset["daily_change_pct"] < -3 else 0
        risk_score = max(0, min(100, risk))
        asset["risk_score"] = risk_score
        asset["risks"] = []
        if m["volatility_pct"] > 30:
            asset["risks"].append("Elevated volatility regime")
        if m["max_drawdown_pct"] > 20:
            asset["risks"].append("Large historical drawdown exposure")
        if m["rsi"] > 70:
            asset["risks"].append("Potentially overbought RSI")
        if m["rsi"] < 30:
            asset["risks"].append("Potentially oversold RSI")
        if not asset["risks"]:
            asset["risks"].append("No major technical risk flag detected")
        enriched.append(asset)
    state["assets"] = enriched
    trace(state, "Risk Agent", "Estimated volatility, drawdown and signal instability risk for each asset.")
    return state


def scoring_agent(state: CopilotState) -> CopilotState:
    for asset in state["assets"]:
        m = asset["metrics"]
        esg = asset["esg"]["overall"]
        score = 50
        drivers = []
        if asset["price"] > m["ma20"]:
            score += 8; drivers.append("Price above 20-day moving average")
        else:
            score -= 5; drivers.append("Price below 20-day moving average")
        if m["ma20"] > m["ma50"]:
            score += 8; drivers.append("Short-term trend above medium-term trend")
        if m["macd"] > 0:
            score += 8; drivers.append("Positive MACD momentum")
        else:
            score -= 5
        if 45 <= m["rsi"] <= 65:
            score += 7; drivers.append("RSI in healthy neutral zone")
        elif m["rsi"] > 70:
            score -= 8
        if m["return_30d_pct"] > 0:
            score += 6; drivers.append("Positive 30-day return")
        score -= int(asset["risk_score"] * 0.25)
        if state.get("esg_preference", True):
            score += int((esg - 50) * 0.25)
            drivers.append("ESG preference included in score")
        score = max(0, min(100, score))
        asset["investment_score"] = score
        asset["confidence"] = max(45, min(92, int(50 + abs(score - 50) * 0.75)))
        if score >= 72:
            signal = "STRONG BUY"
        elif score >= 60:
            signal = "WATCHLIST"
        elif score >= 45:
            signal = "HOLD"
        else:
            signal = "HIGH RISK"
        asset["signal"] = signal
        asset["drivers"] = drivers[:5]
    trace(state, "Scoring Agent", "Combined momentum, risk, ESG and technical indicators into an investment score.")
    return state


def portfolio_agent(state: CopilotState) -> CopilotState:
    assets = state["assets"]
    positive = [max(0, a["investment_score"] - a["risk_score"] * 0.35) for a in assets]
    total = sum(positive)
    if total <= 0:
        allocation = {a["ticker"]: round(100 / len(assets), 2) for a in assets}
    else:
        allocation = {a["ticker"]: round(v / total * 100, 2) for a, v in zip(assets, positive)}
    state["allocation"] = allocation
    portfolio_score = int(sum(a["investment_score"] for a in assets) / len(assets))
    state["portfolio_score"] = portfolio_score
    state["recommendation"] = "Opportunity-oriented" if portfolio_score >= 65 else "Balanced caution" if portfolio_score >= 50 else "Defensive / high caution"
    state["human_review_required"] = any(a["risk_score"] > 65 for a in assets) or portfolio_score < 45
    trace(state, "Investment Committee Agent", "Generated portfolio-level recommendation and allocation proposal with human-review gate.")
    return state


def build_graph():
    graph = StateGraph(CopilotState)
    graph.add_node("market_data", market_data_agent)
    graph.add_node("risk", risk_agent)
    graph.add_node("scoring", scoring_agent)
    graph.add_node("portfolio", portfolio_agent)
    graph.set_entry_point("market_data")
    graph.add_edge("market_data", "risk")
    graph.add_edge("risk", "scoring")
    graph.add_edge("scoring", "portfolio")
    graph.add_edge("portfolio", END)
    return graph.compile()


def run_copilot(tickers: List[str], risk_profile: str, esg_preference: bool, horizon: str) -> CopilotState:
    app = build_graph()
    return app.invoke({
        "tickers": tickers,
        "risk_profile": risk_profile,
        "esg_preference": esg_preference,
        "horizon": horizon,
        "agent_trace": [],
    })
