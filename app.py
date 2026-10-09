"""Streamlit dashboard for the M&A decision-support backend."""

import json
from datetime import datetime, timezone

import streamlit as st
from dotenv import load_dotenv

from ma_agents import run_analysis


load_dotenv()
st.set_page_config(page_title="M&A Deal Desk", page_icon="◈", layout="wide")

st.markdown(
    """
    <style>
      .stApp { background: #f5f7fa; }
      [data-testid="stHeader"] { background: rgba(245,247,250,.85); }
      .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1280px; }
      .hero { padding: 1.6rem 1.8rem; border-radius: 18px; color: white;
        background: linear-gradient(115deg,#10243a 0%,#173b56 60%,#176b70 100%); margin-bottom: 1.2rem; }
      .hero-kicker { color: #93d9d0; text-transform: uppercase; letter-spacing: .15em; font-size: .75rem; font-weight: 700; }
      .hero h1 { color: white; margin: .35rem 0; font-size: 2.15rem; }
      .hero p { color: #d1e0e8; margin: 0; }
      .small-note { color: #687789; font-size: .88rem; }
      div[data-testid="stMetric"] { background: white; border: 1px solid #e5eaf0; padding: 1rem; border-radius: 12px; }
      div.stButton > button[kind="primary"] { background: #147b78; border-color: #147b78; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero"><div class="hero-kicker">Analyst workspace</div>'
    '<h1>M&amp;A Deal Desk</h1>'
    '<p>Explore a transaction through specialist analysis, a red-team review, and a committee memo.</p></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Transaction")
    with st.form("transaction_form"):
        acquirer = st.text_input("Acquirer", value="Tata Steel")
        target = st.text_input("Target", value="Jindal Steel")
        ticker = st.text_input("Target Yahoo Finance ticker", value="JINDALSTEL.NS")
        submitted = st.form_submit_button("Generate analysis", type="primary", use_container_width=True)
    st.divider()
    st.caption("A run makes six Groq model calls and fetches current financial data. It may take a few minutes.")
    st.caption("Add GROQ_API_KEY to your local `.env` before running this dashboard.")

if submitted:
    if not acquirer.strip() or not target.strip() or not ticker.strip():
        st.error("Enter an acquirer, target, and ticker to continue.")
    else:
        try:
            with st.status("Running the M&A analysis pipeline…", expanded=True) as status:
                st.write("Retrieving financial statements and preparing analysis inputs.")
                st.write("Generating four specialist reports, a red-team review, and a committee memo.")
                result = run_analysis(ticker.strip(), acquirer.strip(), target.strip())
                status.update(label="Analysis complete", state="complete", expanded=False)
            st.session_state["deal_analysis"] = {
                "reports": result,
                "acquirer": acquirer.strip(),
                "target": target.strip(),
                "ticker": ticker.strip(),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            detail = str(exc)
            if "Request too large" in detail or "tokens per minute" in detail or "rate_limit_exceeded" in detail:
                st.error("Groq rejected a request because it exceeded the current token limit.")
                st.info("The analysis now shortens reports passed between agents and uses a smaller response budget. Restart the dashboard to load the update. If the error continues, lower MAX_COMPLETION_TOKENS in .env (for example, 700) and try again after the provider limit resets.")
            else:
                st.error(f"Analysis could not be completed: {detail}")
                st.info("Check your API key, installed dependencies, network access, and ticker symbol, then try again.")

analysis = st.session_state.get("deal_analysis")
if analysis:
    st.subheader(f"{analysis['acquirer']}  →  {analysis['target']}")
    st.caption(f"Ticker: {analysis['ticker']}  ·  Generated: {analysis['generated_at'][:19].replace('T', ' ')} UTC")
    metrics = st.columns(3)
    metrics[0].metric("Analysis sections", len(analysis["reports"]))
    metrics[1].metric("Specialist reports", 4)
    metrics[2].metric("Review stages", 2)

    tab_names = list(analysis["reports"])
    tabs = st.tabs(tab_names)
    for tab, name in zip(tabs, tab_names):
        with tab:
            st.markdown(analysis["reports"][name])

    export = {
        "transaction": {key: analysis[key] for key in ("acquirer", "target", "ticker", "generated_at")},
        "reports": analysis["reports"],
    }
    st.download_button(
        "Download all reports (JSON)",
        data=json.dumps(export, ensure_ascii=False, indent=2),
        file_name=f"{analysis['ticker'].replace('.', '-')}-ma-analysis.json",
        mime="application/json",
        type="primary",
    )
else:
    left, right = st.columns([1.25, 1])
    with left:
        st.subheader("A structured first-pass review")
        st.write("Run a transaction through financial diligence, valuation, industry intelligence, and synergy analysis. A red-team agent challenges those findings before a committee discussion memo is drafted.")
        st.markdown('<p class="small-note">Use the reports to support analyst review. Verify provider data and model-generated statements against primary sources.</p>', unsafe_allow_html=True)
    with right:
        st.subheader("What you’ll get")
        st.markdown("- Financial due diligence\n- M&A valuation\n- Industry and competitive intelligence\n- Synergy analysis\n- Red-team risk review\n- Investment committee discussion memo")

st.divider()
st.caption("Academic decision-support prototype · Not an investment recommendation or transaction approval")
