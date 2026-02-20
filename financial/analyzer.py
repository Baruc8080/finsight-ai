import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from financial.models import FinancialAnalysis


def analyze_financial_report(text: str) -> FinancialAnalysis:

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY")  # 👈 importante
    )

    prompt = ChatPromptTemplate.from_template("""
    You are a financial analyst.

    Analyze the following 10-K report excerpt and:

    1. Extract key financial metrics:
       - Revenue
       - Net Income
       - Operating Income
       - Total Assets
       - Total Liabilities
       - Cash Flow
       - EPS
       - Total Debt

    2. Provide a short executive summary (max 200 words).

    3. Identify main business risks mentioned.

    Report:
    {report_text}
    """)

    structured_llm = llm.with_structured_output(FinancialAnalysis)

    chain = prompt | structured_llm

    return chain.invoke({"report_text": text[:12000]})
