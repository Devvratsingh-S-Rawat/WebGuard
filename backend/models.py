from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"

class Finding(BaseModel):
    title: str
    description: str
    severity: Severity
    recommendation: str

class ScannerResult(BaseModel):
    scanner: str
    status: str
    findings: List[Finding] = []
    raw: Optional[dict] = None

class ScanRequest(BaseModel):
    url: str

class RiskScore(BaseModel):
    score: int
    grade: str
    label: str
    color: str

class ScanResponse(BaseModel):
    target: str
    results: List[ScannerResult]
    total_findings: int
    summary: dict
    risk_score: Optional[RiskScore] = None