from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import ScanRequest, ScanResponse, ScannerResult
from scanners import ssl_scanner, headers_scanner, port_scanner, whois_scanner, sqli_scanner, xss_scanner, cms_scanner, broken_links_scanner
from utils.pdf_generator import generate_pdf
import asyncio
import json

router = APIRouter()

def extract_hostname(url: str) -> str:
    parsed = urlparse(url)
    hostname = parsed.hostname or url
    return hostname.replace("www.", "")

def run_scanner(fn, *args) -> ScannerResult:
    try:
        return fn(*args)
    except Exception as e:
        return ScannerResult(scanner="Unknown", status="error", findings=[], raw={"error": str(e)})

def run_all_scanners(url: str, hostname: str):
    results = []
    tasks = [
        (ssl_scanner.run,          hostname),
        (headers_scanner.run,      url),
        (port_scanner.run,         hostname),
        (whois_scanner.run,        hostname),
        (sqli_scanner.run,         url),
        (xss_scanner.run,          url),
        (cms_scanner.run,          url),
        (broken_links_scanner.run, url),
    ]
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(run_scanner, fn, *args): fn.__module__ for fn, *args in tasks}
        for future in as_completed(futures):
            results.append(future.result())
    return results

def calculate_risk_score(summary: dict) -> dict:
    score = 100
    score -= summary.get("critical", 0) * 25
    score -= summary.get("high", 0)     * 10
    score -= summary.get("medium", 0)   * 5
    score -= summary.get("low", 0)      * 2
    score = max(0, score)

    if score >= 90:
        grade = "A"
        label = "Excellent"
        color = "#00d4aa"
    elif score >= 75:
        grade = "B"
        label = "Good"
        color = "#3b8bd4"
    elif score >= 50:
        grade = "C"
        label = "Moderate Risk"
        color = "#f5c542"
    elif score >= 25:
        grade = "D"
        label = "Poor"
        color = "#ef9f27"
    else:
        grade = "F"
        label = "Critical Risk"
        color = "#e24b4a"

    return {
        "score": score,
        "grade": grade,
        "label": label,
        "color": color
    }

def build_summary(all_findings):
    summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in all_findings:
        summary[f.severity.value] = summary.get(f.severity.value, 0) + 1
    return summary

@router.post("/scan", response_model=ScanResponse)
def scan_target(req: ScanRequest):
    url = req.url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    hostname = extract_hostname(url)
    if not hostname:
        raise HTTPException(status_code=400, detail="Invalid URL provided.")

    results = run_all_scanners(url, hostname)
    all_findings = [f for r in results for f in r.findings]
    summary = build_summary(all_findings)
    risk = calculate_risk_score(summary)

    return ScanResponse(
        target=hostname,
        results=results,
        total_findings=len(all_findings),
        summary=summary,
        risk_score=risk
    )

@router.post("/scan/report")
def download_report(req: ScanRequest):
    url = req.url.strip()
    if not url.startswith("http"):
        url = "https://" + url

    hostname = extract_hostname(url)
    results = run_all_scanners(url, hostname)
    all_findings = [f for r in results for f in r.findings]
    summary = build_summary(all_findings)
    risk = calculate_risk_score(summary)

    scan_data = {
        "target": hostname,
        "results": [r.model_dump() for r in results],
        "total_findings": len(all_findings),
        "summary": summary,
        "risk_score": risk
    }

    pdf_bytes = generate_pdf(scan_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=webguard-{hostname}.pdf"}
    )

@router.websocket("/ws/scan")
async def websocket_scan(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = json.loads(data)
        url = payload.get("url", "").strip()

        if not url.startswith("http"):
            url = "https://" + url

        hostname = extract_hostname(url)

        await websocket.send_text(json.dumps({
            "type": "start",
            "message": f"Starting scan on {hostname}..."
        }))

        scanners = [
            ("SSL/TLS Analysis",   ssl_scanner.run,          hostname),
            ("HTTP Headers Audit", headers_scanner.run,      url),
            ("Port Scanning",      port_scanner.run,         hostname),
            ("WHOIS & DNS Lookup", whois_scanner.run,        hostname),
            ("SQL Injection Test", sqli_scanner.run,         url),
            ("XSS Detection",      xss_scanner.run,          url),
            ("CMS Detection",      cms_scanner.run,          url),
            ("Broken Links",       broken_links_scanner.run, url),
        ]

        results = []
        loop = asyncio.get_event_loop()

        for name, fn, arg in scanners:
            await websocket.send_text(json.dumps({
                "type": "progress",
                "scanner": name,
                "message": f"Running {name}..."
            }))

            result = await loop.run_in_executor(None, fn, arg)
            results.append(result)

            await websocket.send_text(json.dumps({
                "type": "scanner_done",
                "scanner": name,
                "findings_count": len(result.findings),
                "message": f"{name} complete — {len(result.findings)} findings"
            }))

        all_findings = [f for r in results for f in r.findings]
        summary = build_summary(all_findings)
        risk = calculate_risk_score(summary)

        final = {
            "type": "complete",
            "target": hostname,
            "results": [r.model_dump() for r in results],
            "total_findings": len(all_findings),
            "summary": summary,
            "risk_score": risk
        }

        await websocket.send_text(json.dumps(final))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))