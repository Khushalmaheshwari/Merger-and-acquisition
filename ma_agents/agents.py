"""LLM report writers retaining the notebook's specialist agent roles."""

from groq import Groq

from .config import Settings


def _compact_reports(reports: dict[str, str], max_chars_per_report: int = 2400) -> str:
    """Bound chained-agent context so requests stay below provider TPM limits."""
    parts = []
    for name, content in reports.items():
        text = content.strip()
        if len(text) > max_chars_per_report:
            text = text[:max_chars_per_report].rsplit(" ", 1)[0] + "\n[Report excerpt shortened to keep the review within model request limits.]"
        parts.append(f"### {name}\n{text}")
    return "\n\n".join(parts)


class AgentSuite:
    def __init__(self, settings: Settings):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.model
        self.max_completion_tokens = settings.max_completion_tokens

    def _complete(self, role: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": role}, {"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=self.max_completion_tokens,
        )
        return response.choices[0].message.content or ""

    def financial_agent(self, ticker: str, data: str) -> str:
        return self._complete("You are a senior financial due diligence analyst specializing in M&A.", f"""You are analyzing {ticker} for an academic M&A exercise. Use only the supplied information; do not invent figures. Separate facts from interpretation, flag missing data, and do not make an actual investment recommendation.\n\n{data}\n\nReturn a FINANCIAL DUE DILIGENCE REPORT with: executive summary; financial performance; profitability; debt and leverage; cash flow and liquidity; strengths; risks; key due diligence questions; overall assessment.""")

    def valuation_agent(self, ticker: str, data: str) -> str:
        return self._complete("You are a senior M&A valuation analyst specializing in corporate acquisitions.", f"""Evaluate {ticker} using only this data. Do not invent figures. Explain market multiples versus the simplified DCF-style illustration, identify assumptions and sensitivity to them, and explain the information required for a professional valuation. Academic analysis only; no investment recommendation.\n\n{data}\n\nReturn an M&A VALUATION REPORT: summary, market-based valuation, EV/revenue, EV/EBITDA, DCF-style valuation, assumptions, risks, information required, conclusion.""")

    def industry_agent(self, acquirer: str, target: str, data: str) -> str:
        return self._complete("You are a senior industry and competitive intelligence analyst specializing in M&A.", f"""Analyze the industry relevant to {acquirer}'s potential acquisition of {target}. Clearly separate general industry factors from verified facts. Do not invent market shares or company advantages. Current data is not supplied, so identify what requires sourcing. Academic exercise only.\n\n{data}\n\nReturn an INDUSTRY & COMPETITIVE INTELLIGENCE REPORT covering overview, demand, cyclicality, raw materials and energy, competition, risks, regulatory/environmental factors, strategic considerations, and information gaps.""")

    def synergy_agent(self, acquirer: str, target: str, data: str) -> str:
        return self._complete("You are a senior M&A synergy analyst specializing in post-merger value creation.", f"""Assess possible value creation in {acquirer}'s potential acquisition of {target}. Treat all synergies as hypothetical, do not invent numerical values, and specify evidence needed to validate each opportunity plus integration risks.\n\n{data}\n\nReturn an M&A SYNERGY ANALYSIS REPORT with executive summary, cost and revenue opportunities, operations, realization requirements, integration risks, information required, and overall assessment.""")

    def red_team_agent(self, acquirer: str, target: str, reports: dict[str, str]) -> str:
        inputs = _compact_reports(reports)
        return self._complete("You are an independent M&A risk analyst and red-team reviewer. Challenge assumptions rather than agree.", f"""Red-team {acquirer}'s potential acquisition of {target}. Find unsupported conclusions, inconsistencies, missing information, financial/valuation/industry/synergy risks, and plausible downside scenarios. Do not invent facts; distinguish facts, assumptions and risks. Do not recommend an actual transaction.\n\n{inputs}\n\nReturn an M&A RED-TEAM / RISK REPORT: executive risk summary, financial risks, valuation risks, industry risks, synergy and integration risks, weak assumptions/contradictions, information gaps, worst-case scenarios, management questions, conclusion.""")

    def investment_committee_agent(self, acquirer: str, target: str, reports: dict[str, str]) -> str:
        inputs = _compact_reports(reports)
        return self._complete("You are an M&A investment committee memo editor. Be balanced, traceable, and explicit about uncertainty.", f"""Prepare an academic draft memo for {acquirer}'s potential acquisition of {target}, based only on the reports below. Do not invent facts or turn this into an approval decision. Highlight the need for human review and primary-source verification.\n\n{inputs}\n\nReturn an INVESTMENT COMMITTEE DISCUSSION MEMORANDUM with transaction summary, strategic rationale, diligence findings, valuation, synergies, industry context, key risks, information gaps, downside scenarios, questions for management, and discussion points.""")
