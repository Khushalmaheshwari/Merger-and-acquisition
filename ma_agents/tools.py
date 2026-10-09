"""Deterministic data tools adapted from the original notebook."""

from __future__ import annotations

import math
from typing import Any

import pandas as pd
import yfinance as yf


def _number(value: Any) -> float:
    try:
        number = float(value)
        return number if math.isfinite(number) else math.nan
    except (TypeError, ValueError):
        return math.nan


def _row_value(frame: pd.DataFrame, row: str) -> float:
    if frame is None or frame.empty or row not in frame.index:
        return math.nan
    return _number(frame.loc[row].iloc[0])


def _fmt(value: float, currency: str = "₹") -> str:
    return f"{currency}{value:,.0f}" if math.isfinite(value) else "N/A"


def financial_due_diligence(ticker: str) -> dict[str, Any]:
    """Fetch latest available Yahoo Finance statements and calculate basic metrics."""
    company = yf.Ticker(ticker)
    info = company.info or {}
    income, balance, cashflow = company.income_stmt, company.balance_sheet, company.cashflow
    revenue = _row_value(income, "Total Revenue")
    operating_income = _row_value(income, "Operating Income")
    net_income = _row_value(income, "Net Income")
    ebitda = _row_value(income, "EBITDA")
    if not math.isfinite(ebitda):
        ebitda = _row_value(income, "Normalized EBITDA")
    debt = _row_value(balance, "Total Debt")
    cash = _row_value(balance, "Cash Cash Equivalents And Short Term Investments")
    equity = _row_value(balance, "Stockholders Equity")
    assets = _row_value(balance, "Total Assets")
    liabilities = _row_value(balance, "Total Liabilities Net Minority Interest")
    operating_cash_flow = _row_value(cashflow, "Operating Cash Flow")
    capex = _row_value(cashflow, "Capital Expenditure")

    def ratio(numerator: float, denominator: float, scale: float = 1.0) -> float:
        return numerator / denominator * scale if math.isfinite(numerator) and math.isfinite(denominator) and denominator != 0 else math.nan

    net_debt = debt - cash if math.isfinite(debt) and math.isfinite(cash) else math.nan
    debt_to_equity = ratio(debt, equity)
    flags = []
    if math.isfinite(debt_to_equity) and debt_to_equity > 1:
        flags.append("High Debt-to-Equity")
    ebitda_margin = ratio(ebitda, revenue, 100)
    if math.isfinite(ebitda_margin) and ebitda_margin < 10:
        flags.append("Low EBITDA Margin")
    if math.isfinite(net_debt) and net_debt > 0:
        flags.append("Net Debt Position")
    if math.isfinite(operating_cash_flow) and operating_cash_flow < 0:
        flags.append("Negative Operating Cash Flow")
    if not flags:
        flags.append("No major automated financial flags (limited data caveat applies)")

    return {
        "Company": info.get("longName", ticker), "Ticker": ticker,
        "Sector": info.get("sector", "N/A"), "Industry": info.get("industry", "N/A"),
        "Market Cap": _number(info.get("marketCap")), "Revenue": revenue,
        "EBITDA": ebitda, "Operating Income": operating_income, "Net Income": net_income,
        "Total Assets": assets, "Total Liabilities": liabilities, "Equity": equity,
        "Total Debt": debt, "Cash": cash, "Net Debt": net_debt,
        "Operating Cash Flow": operating_cash_flow, "Capital Expenditure": capex,
        "Operating Margin (%)": ratio(operating_income, revenue, 100),
        "EBITDA Margin (%)": ebitda_margin, "Net Margin (%)": ratio(net_income, revenue, 100),
        "Debt / Equity": debt_to_equity,
        "Debt / Operating Income": ratio(debt, operating_income),
        "Operating Cash Flow / Debt": ratio(operating_cash_flow, debt),
        "Risk Flags": flags,
    }


def financial_dd_tool(ticker: str) -> dict[str, Any]:
    """Notebook-compatible name retained for existing callers."""
    return financial_due_diligence(ticker)


def format_financial_data(data: dict[str, Any]) -> str:
    percent_keys = {"Operating Margin (%)", "EBITDA Margin (%)", "Net Margin (%)"}
    ratio_keys = {"Debt / Equity", "Debt / Operating Income", "Operating Cash Flow / Debt"}
    amount_keys = {"Market Cap", "Revenue", "EBITDA", "Operating Income", "Net Income", "Total Assets", "Total Liabilities", "Equity", "Total Debt", "Cash", "Net Debt", "Operating Cash Flow", "Capital Expenditure"}
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            rendered = ", ".join(value)
        elif key in percent_keys:
            rendered = f"{value:.2f}%" if math.isfinite(value) else "N/A"
        elif key in ratio_keys:
            rendered = f"{value:.2f}x" if math.isfinite(value) else "N/A"
        elif key in amount_keys and isinstance(value, float):
            rendered = _fmt(value)
        else:
            rendered = str(value)
        lines.append(f"{key}: {rendered}")
    return "FINANCIAL DATA (latest data returned by Yahoo Finance; verify reporting period and currency):\n" + "\n".join(lines)


def valuation_tool(ticker: str) -> str:
    """Notebook valuation logic, with missing-data checks and its academic limits stated."""
    stock = yf.Ticker(ticker)
    income, balance = stock.income_stmt, stock.balance_sheet
    if income is None or income.empty:
        raise ValueError(f"No income statement data available for {ticker}.")
    latest = income.columns[0]
    revenue = _row_value(income, "Total Revenue")
    operating_income = _row_value(income, "Operating Income")
    depreciation = _row_value(income, "Depreciation And Amortization")
    ebitda = _row_value(income, "EBITDA")
    if not math.isfinite(ebitda):
        ebitda = operating_income + depreciation if math.isfinite(operating_income) and math.isfinite(depreciation) else math.nan
    debt, cash = _row_value(balance, "Total Debt"), _row_value(balance, "Cash Cash Equivalents And Short Term Investments")
    net_debt = debt - cash if math.isfinite(debt) and math.isfinite(cash) else math.nan
    market_cap = _number((stock.info or {}).get("marketCap"))
    enterprise_value = market_cap + net_debt if math.isfinite(market_cap) and math.isfinite(net_debt) else math.nan
    ev_revenue = enterprise_value / revenue if math.isfinite(enterprise_value) and math.isfinite(revenue) and revenue else math.nan
    ev_ebitda = enterprise_value / ebitda if math.isfinite(enterprise_value) and math.isfinite(ebitda) and ebitda else math.nan
    growth_rate, terminal_growth, discount_rate = 0.08, 0.03, 0.10
    if math.isfinite(ebitda):
        projected = [ebitda * (1 + growth_rate) ** year for year in range(1, 6)]
        terminal_value = projected[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        dcf_value = sum(value / (1 + discount_rate) ** year for year, value in enumerate(projected, start=1)) + terminal_value / (1 + discount_rate) ** 5
    else:
        dcf_value = math.nan
    period = str(latest.date()) if hasattr(latest, "date") else str(latest)
    return f"""M&A VALUATION DATA\nCompany: {(stock.info or {}).get('longName', ticker)}\nTicker: {ticker}\nStatement period: {period}\n\nLATEST FINANCIAL DATA\nRevenue: {_fmt(revenue)}\nOperating Income: {_fmt(operating_income)}\nEstimated EBITDA: {_fmt(ebitda)}\nDebt: {_fmt(debt)}\nCash: {_fmt(cash)}\nNet Debt: {_fmt(net_debt)}\n\nMARKET VALUATION\nMarket Capitalization: {_fmt(market_cap)}\nEnterprise Value: {_fmt(enterprise_value)}\nEV / Revenue: {ev_revenue:.2f}x\nEV / EBITDA: {ev_ebitda:.2f}x\n\nDCF ASSUMPTIONS\nEBITDA growth: 8%; discount rate: 10%; terminal growth: 3%\nDCF-style enterprise value: {_fmt(dcf_value)}\n\nLIMITATION: Simplified EBITDA-based academic illustration, not a professional FCFF DCF or transaction valuation. Verify data period, units and currency."""


def industry_intelligence_tool(acquirer: str, target: str) -> str:
    return f"""INDUSTRY: Indian steel industry\nTARGET: {target}\nACQUIRER: {acquirer}\n\nAcademic industry factors (not current company-specific claims): steel demand is influenced by infrastructure, construction, automotive and manufacturing; steel is cyclical; iron ore, coking coal and energy affect costs; domestic/international prices, trade policy, environmental rules, capacity expansion, competition and utilization affect economics. Analyze company-specific claims only when supported by supplied evidence. Current market data and source validation are not included."""


def synergy_tool(acquirer: str, target: str) -> str:
    return f"""Potential transaction: {acquirer} / {target}. Hypothetical synergy categories only; no numerical savings are confirmed: combined raw-material procurement, logistics optimization, shared overheads, operations and asset utilization, customer cross-selling, broader product portfolio and distribution. Integration risks include execution complexity, workforce/organizational issues, systems integration, regulation and failure to realize benefits. Quantification requires evidence and implementation costs."""
