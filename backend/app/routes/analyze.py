from fastapi import APIRouter, HTTPException
from app.schemas import AnalyzeRequest, AnalyzeResponse, AssetSignal
from app.services.agents import run_copilot
from app.services.llm_service import generate_summary

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        state = run_copilot(req.tickers, req.risk_profile, req.esg_preference, req.horizon)
        ai_summary = generate_summary(state)
        assets = []
        for a in state["assets"]:
            assets.append(AssetSignal(
                ticker=a["ticker"],
                name=a["name"],
                price=a["price"],
                daily_change_pct=a["daily_change_pct"],
                signal=a["signal"],
                investment_score=a["investment_score"],
                confidence=a["confidence"],
                risk_score=a["risk_score"],
                esg_score=a["esg"]["overall"],
                metrics={**a["metrics"], "currency": a.get("currency", "USD"), "chart": a.get("chart", [])},
                drivers=a["drivers"],
                risks=a["risks"],
            ))
        return AnalyzeResponse(
            portfolio_score=state["portfolio_score"],
            recommendation=state["recommendation"],
            risk_profile=req.risk_profile,
            assets=assets,
            allocation=state["allocation"],
            agent_trace=state["agent_trace"],
            ai_summary=ai_summary,
            human_review_required=state["human_review_required"],
            disclaimer="Educational and research use only. Not financial advice. Human review is required before any investment decision.",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
