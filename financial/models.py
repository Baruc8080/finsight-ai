from pydantic import BaseModel
from typing import Optional


class FinancialMetrics(BaseModel):
    revenue: Optional[float]
    net_income: Optional[float]
    operating_income: Optional[float]
    total_assets: Optional[float]
    total_liabilities: Optional[float]
    cash_flow: Optional[float]
    eps: Optional[float]
    total_debt: Optional[float]


class FinancialAnalysis(BaseModel):
    summary: str
    risks: list[str]
    metrics: FinancialMetrics
