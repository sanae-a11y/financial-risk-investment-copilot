from __future__ import annotations

import math
from typing import Any, Dict

import numpy as np
import pandas as pd
import yfinance as yf


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None:
            return default
        value = float(x)
        if math.isnan(value) or math.isinf(value):
            return default
        return value
    except Exception:
        return default


def rsi(series: pd.Series, period: int = 14) -> float:
    series = series.dropna()
    if len(series) < period + 2:
        return 50.0

    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()

    rs = gain / loss.replace(0, np.nan)
    value = 100 - (100 / (1 + rs))

    clean = value.dropna()
    if clean.empty:
        return 50.0

    return _safe_float(clean.iloc[-1], 50.0)


def macd(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) < 35:
        return 0.0

    ema12 = series.ewm(span=12, adjust=False).mean()
    ema26 = series.ewm(span=26, adjust=False).mean()

    return _safe_float((ema12 - ema26).iloc[-1])


def volatility(series: pd.Series) -> float:
    series = series.dropna()
    if len(series) < 5:
        return 0.0

    returns = series.pct_change().dropna()
    if returns.empty:
        return 0.0

    return _safe_float(returns.std() * np.sqrt(252) * 100)


def max_drawdown(series: pd.Series) -> float:
    series = series.dropna()
    series = series[series > 0]

    if series.empty:
        return 0.0

    cumulative = series / series.iloc[0]
    peak = cumulative.cummax()
    dd = (cumulative - peak) / peak

    return abs(_safe_float(dd.min() * 100))


def heuristic_esg_score(ticker: str, info: Dict[str, Any]) -> Dict[str, Any]:
    seed = sum(ord(c) for c in ticker.upper())

    env = 50 + (seed % 31)
    social = 48 + ((seed * 3) % 35)
    gov = 55 + ((seed * 7) % 30)

    overall = round((env + social + gov) / 3)

    risk = "Low" if overall >= 75 else "Medium" if overall >= 55 else "High"

    return {
        "environmental": env,
        "social": social,
        "governance": gov,
        "overall": overall,
        "risk_level": risk,
    }


def build_clean_chart(hist: pd.DataFrame):
    """
    Fixes the vertical drop bug by removing:
    - NaN prices
    - 0 prices
    - negative prices
    - invalid rows
    """

    if hist is None or hist.empty:
        return []

    if "Close" not in hist.columns:
        return []

    clean = hist.copy()
    clean = clean.dropna(subset=["Close"])
    clean = clean[clean["Close"] > 0]

    chart = []

    for idx, row in clean.tail(80).iterrows():
        price = _safe_float(row.get("Close"))

        if price <= 0:
            continue

        volume = _safe_float(row.get("Volume", 0))

        chart.append(
            {
                "date": str(idx.date()),
                "price": round(price, 2),
                "volume": int(volume),
            }
        )

    return chart


def fetch_asset(ticker: str) -> Dict[str, Any]:
    symbol = ticker.strip().upper()

    if not symbol:
        raise ValueError("Ticker is required.")

    yf_ticker = yf.Ticker(symbol)
    hist = yf_ticker.history(period="6mo", interval="1d", auto_adjust=False)

    if hist is None or hist.empty:
        raise ValueError(f"No market data found for {symbol}")

    hist = hist.dropna(subset=["Close"])
    hist = hist[hist["Close"] > 0]

    if hist.empty:
        raise ValueError(f"No valid market prices found for {symbol}")

    try:
        info = yf_ticker.info or {}
    except Exception:
        info = {}

    close = hist["Close"].dropna()
    close = close[close > 0]

    price = _safe_float(close.iloc[-1])
    prev = _safe_float(close.iloc[-2], price) if len(close) > 1 else price

    daily_change_pct = ((price - prev) / prev * 100) if prev else 0.0

    ma20_series = close.rolling(20).mean().dropna()
    ma50_series = close.rolling(50).mean().dropna()

    ma20 = _safe_float(ma20_series.iloc[-1], price) if not ma20_series.empty else price
    ma50 = _safe_float(ma50_series.iloc[-1], price) if not ma50_series.empty else price

    rsi_value = rsi(close)
    macd_value = macd(close)
    vol_value = volatility(close)
    mdd_value = max_drawdown(close)

    returns_30d = (
        _safe_float((price / close.iloc[-30] - 1) * 100)
        if len(close) >= 30 and close.iloc[-30] > 0
        else daily_change_pct
    )

    if "Volume" in hist.columns:
        volume_clean = hist["Volume"].dropna()
        volume_now = _safe_float(volume_clean.iloc[-1]) if not volume_clean.empty else 0
        volume_avg_series = volume_clean.rolling(20).mean().dropna()
        volume_avg = _safe_float(volume_avg_series.iloc[-1]) if not volume_avg_series.empty else 0
    else:
        volume_now = 0
        volume_avg = 0

    volume_strength = _safe_float((volume_now / volume_avg) * 100, 100) if volume_avg else 100

    esg = heuristic_esg_score(symbol, info)
    chart = build_clean_chart(hist)

    return {
        "ticker": symbol,
        "name": info.get("longName") or info.get("shortName") or symbol,
        "price": round(price, 2),
        "currency": info.get("currency", "USD"),
        "daily_change_pct": round(daily_change_pct, 2),
        "metrics": {
            "rsi": round(rsi_value, 2),
            "macd": round(macd_value, 2),
            "ma20": round(ma20, 2),
            "ma50": round(ma50, 2),
            "volatility_pct": round(vol_value, 2),
            "max_drawdown_pct": round(mdd_value, 2),
            "return_30d_pct": round(returns_30d, 2),
            "volume_strength": round(volume_strength, 2),
        },
        "esg": esg,
        "chart": chart,
    }