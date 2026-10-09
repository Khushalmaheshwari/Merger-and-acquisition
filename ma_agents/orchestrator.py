"""Run the notebook's analysis pipeline once per transaction."""

from .agents import AgentSuite
from .config import get_settings
from .tools import (
    financial_due_diligence,
    format_financial_data,
    industry_intelligence_tool,
    synergy_tool,
    valuation_tool,
)


def run_analysis(target_ticker: str = "JINDALSTEL.NS", acquirer: str = "Tata Steel", target: str = "Jindal Steel") -> dict[str, str]:
    """Fetch tool inputs, call each specialist once, then red-team and synthesize."""
    settings = get_settings()
    agents = AgentSuite(settings)

    financial_data = financial_due_diligence(target_ticker)
    valuation_data = valuation_tool(target_ticker)
    industry_data = industry_intelligence_tool(acquirer, target)
    synergy_data = synergy_tool(acquirer, target)

    reports = {
        "Financial Due Diligence": agents.financial_agent(target_ticker, format_financial_data(financial_data)),
        "Valuation": agents.valuation_agent(target_ticker, valuation_data),
        "Industry Intelligence": agents.industry_agent(acquirer, target, industry_data),
        "Synergy Analysis": agents.synergy_agent(acquirer, target, synergy_data),
    }
    reports["Red-Team Risk Review"] = agents.red_team_agent(acquirer, target, reports)
    reports["Investment Committee Discussion Memo"] = agents.investment_committee_agent(acquirer, target, reports)
    return reports
