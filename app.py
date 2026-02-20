import streamlit as st
from dotenv import load_dotenv
from financial.extractor import extract_text_from_pdf
from financial.analyzer import analyze_financial_report
import plotly.graph_objects as go
from io import BytesIO
import traceback
import os

load_dotenv()

st.set_page_config(
    page_title="📊 FinSight AI",
    page_icon="📈",
    layout="wide"
)

# -----------------------
# Helpers
# -----------------------
def format_currency(value):
    if value is None:
        return "N/A"
    try:
        v = float(value)
    except Exception:
        return "N/A"
    abs_v = abs(v)
    sign = "-" if v < 0 else ""
    if abs_v >= 1_000_000_000:
        return f"{sign}${abs_v/1_000_000_000:.2f}B"
    if abs_v >= 1_000_000:
        return f"{sign}${abs_v/1_000_000:.2f}M"
    return f"{sign}${v:,.0f}"


def safe_get_metrics(analysis):
    """
    Return an object with attributes we can read (metrics).
    If analysis has .metrics, return that; else return analysis itself.
    """
    return getattr(analysis, "metrics", analysis)


def financial_health(metrics):
    try:
        ni = getattr(metrics, "net_income", None)
        cf = getattr(metrics, "cash_flow", None)
        ta = getattr(metrics, "total_assets", None)
        td = getattr(metrics, "total_debt", None)
        if ni is not None and cf is not None and ta is not None and td is not None:
            if ni > 0 and cf > 0 and td < ta:
                return "🟢 Financially Stable"
    except Exception:
        pass
    return "🟡 Needs Attention"


# -----------------------
# Page header / sidebar
# -----------------------
st.markdown(
    """
    <div style="text-align:center">
        <h1>📊 FinSight AI</h1>
        <h4 style="color:gray">Panel Inteligente de Análisis Financiero 10-K</h4>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.title("FinSight AI")
    st.markdown("Sube un PDF estilo 10-K y obtén:")
    st.markdown("- Métricas financieras clave (estructuradas)")
    st.markdown("- Resumen ejecutivo")
    st.markdown("- Factores de riesgo principales")
    st.markdown("- Visualizaciones (estructura de capital y rentabilidad)")
    st.markdown("---")
    st.caption("Desarrollado con LangChain & OpenAI")

st.markdown("---")

# -----------------------
# File uploader
# -----------------------
uploaded_file = st.file_uploader("Upload 10-K Report (PDF)", type="pdf")

if not uploaded_file:
    st.info("📂 Upload a 10-K PDF to begin the analysis.")
    st.stop()

# -----------------------
# Process file
# -----------------------
with st.spinner("Reading PDF and running analysis..."):
    try:
        # Streamlit's uploaded_file is a file-like object; we can get bytes
        file_bytes = uploaded_file.read()

        # extractor expects bytes -> returns text
        # ensure our extractor handles bytes by wrapping with BytesIO internally (recommended)
        text = extract_text_from_pdf(file_bytes)

        # analyzer expects text -> returns FinancialAnalysis-like object
        analysis = analyze_financial_report(text)

    except Exception as e:
        st.error("Error during analysis. See details below.")
        st.text(traceback.format_exc())
        st.stop()

st.success("Analysis complete")

# -----------------------
# Defensive metrics access
# -----------------------
metrics = safe_get_metrics(analysis)

# helper to fetch attribute or fallback
def g(attr, default=None):
    return getattr(metrics, attr, default)

revenue = g("revenue") or g("Revenue") or None
net_income = g("net_income") or g("netIncome") or g("net_income_usd") or None
operating_income = g("operating_income") or g("operatingIncome") or None
eps = g("eps") or g("EPS") or None
total_assets = g("total_assets") or g("totalAssets") or None
total_liabilities = g("total_liabilities") or g("totalLiabilities") or None
cash_flow = g("cash_flow") or g("cashFlow") or None
total_debt = g("total_debt") or g("totalDebt") or None

# -----------------------
# Key Metrics UI
# -----------------------
st.markdown("## 📈 Key Financial Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue", format_currency(revenue))
col2.metric("Net Income", format_currency(net_income))
col3.metric("Operating Income", format_currency(operating_income))
col4.metric("EPS", f"{eps}" if eps is not None else "N/A")

col5, col6, col7, col8 = st.columns(4)
col5.metric("Total Assets", format_currency(total_assets))
col6.metric("Total Liabilities", format_currency(total_liabilities))
col7.metric("Cash Flow", format_currency(cash_flow))
col8.metric("Total Debt", format_currency(total_debt))

st.markdown("---")

# -----------------------
# Financial Health
# -----------------------
st.markdown("## 🏦 Financial Health Indicator")
st.markdown(f"### {financial_health(metrics)}")

st.markdown("---")

# -----------------------
# Charts
# -----------------------
st.markdown("## 📊 Capital Structure Overview")
# fallback numeric 0 if None
ta = float(total_assets or 0)
td = float(total_debt or 0)
equity = max(ta - td, 0)

fig_capital = go.Figure()
fig_capital.add_trace(go.Bar(
    x=["Equity", "Debt"],
    y=[equity, td],
    marker_color=["#7C5CFF", "#FF6B6B"]
))
fig_capital.update_layout(
    template="plotly_white",
    yaxis_title="USD",
    height=420,
    margin=dict(t=20, b=20, l=20, r=20)
)
st.plotly_chart(fig_capital, use_container_width=True)

st.markdown("## 📈 Profitability Breakdown")
rev = float(revenue or 0)
op_inc = float(operating_income or 0)
ni = float(net_income or 0)

fig_profit = go.Figure()
fig_profit.add_trace(go.Bar(
    x=["Revenue", "Operating Income", "Net Income"],
    y=[rev, op_inc, ni],
    marker_color=["#4CC9F0", "#7209B7", "#3A0CA3"]
))
fig_profit.update_layout(
    template="plotly_white",
    yaxis_title="USD",
    height=420,
    margin=dict(t=20, b=20, l=20, r=20)
)
st.plotly_chart(fig_profit, use_container_width=True)

st.markdown("---")

# -----------------------
# Executive Summary & Risks
# -----------------------
st.markdown("## 📝 Executive Summary")
summary_text = getattr(analysis, "summary", None) or getattr(analysis, "executive_summary", None) or "No summary available."
with st.expander("View Summary"):
    st.write(summary_text)

st.markdown("## ⚠️ Key Risk Factors")
risks = getattr(analysis, "risks", None) or getattr(analysis, "key_risks", None) or []
with st.expander("View Risks"):
    if risks:
        for r in risks:
            st.write(f"- {r}")
    else:
        st.write("No risks identified.")

st.markdown("---")

# -----------------------
# Debug: extracted text
# -----------------------
with st.expander("Raw extracted text (first 20k chars)"):
    st.text_area("Extracted text", text[:20000], height=300)
