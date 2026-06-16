from __future__ import annotations
import os
import json
import requests
from typing import Dict, Any

SYSTEM_PROMPT = """
You are an AI investment decision-support copilot for educational and research use only.
Return concise, responsible, non-promissory analysis. Do not give guaranteed financial advice.
Focus on: signal drivers, risk, ESG, uncertainty, and human-review recommendations.
"""


def generate_summary(state: Dict[str, Any]) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat-v3-0324:free")

    fallback = (
        f"The agentic investment committee classifies this portfolio as '{state.get('recommendation')}' "
        f"with a portfolio score of {state.get('portfolio_score')}/100. The analysis combines momentum, "
        "volatility, drawdown, ESG heuristic scores, and allocation logic. Human review is recommended "
        "when risk is elevated or signals are uncertain. This is for educational and research purposes only."
    )
    if not api_key:
        return fallback

    compact_assets = [
        {
            "ticker": a["ticker"],
            "signal": a["signal"],
            "investment_score": a["investment_score"],
            "risk_score": a["risk_score"],
            "esg_score": a["esg"]["overall"],
            "drivers": a["drivers"],
            "risks": a["risks"],
        }
        for a in state.get("assets", [])
    ]
    prompt = f"""
Analyze this agentic portfolio output and generate a short professional summary.
Risk profile: {state.get('risk_profile')}
Horizon: {state.get('horizon')}
Portfolio score: {state.get('portfolio_score')}
Recommendation: {state.get('recommendation')}
Allocation: {state.get('allocation')}
Assets: {json.dumps(compact_assets, ensure_ascii=False)}

Return 2 short paragraphs and 3 bullet watch points.
"""
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return fallback
