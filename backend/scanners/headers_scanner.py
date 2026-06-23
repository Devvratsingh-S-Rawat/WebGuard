import requests
from models import ScannerResult, Finding, Severity

HEADERS_CHECK = [
    {
        "header": "Strict-Transport-Security",
        "title": "Missing HSTS Header",
        "description": "HTTP Strict Transport Security (HSTS) is not set. Browsers may connect over HTTP.",
        "severity": Severity.HIGH,
        "recommendation": "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains"
    },
    {
        "header": "Content-Security-Policy",
        "title": "Missing Content-Security-Policy Header",
        "description": "No CSP header found. This leaves the site open to XSS and data injection attacks.",
        "severity": Severity.HIGH,
        "recommendation": "Define a strict Content-Security-Policy to control allowed sources."
    },
    {
        "header": "X-Frame-Options",
        "title": "Missing X-Frame-Options Header",
        "description": "Site may be vulnerable to clickjacking attacks via iframes.",
        "severity": Severity.MEDIUM,
        "recommendation": "Add: X-Frame-Options: DENY or SAMEORIGIN"
    },
    {
        "header": "X-Content-Type-Options",
        "title": "Missing X-Content-Type-Options Header",
        "description": "Browser may MIME-sniff responses, enabling attacks.",
        "severity": Severity.MEDIUM,
        "recommendation": "Add: X-Content-Type-Options: nosniff"
    },
    {
        "header": "Referrer-Policy",
        "title": "Missing Referrer-Policy Header",
        "description": "Full URL may be leaked in Referer header to third parties.",
        "severity": Severity.LOW,
        "recommendation": "Add: Referrer-Policy: strict-origin-when-cross-origin"
    },
    {
        "header": "Permissions-Policy",
        "title": "Missing Permissions-Policy Header",
        "description": "Browser features (camera, mic, geolocation) are not restricted.",
        "severity": Severity.LOW,
        "recommendation": "Add: Permissions-Policy: geolocation=(), microphone=(), camera=()"
    },
    {
        "header": "X-XSS-Protection",
        "title": "Missing X-XSS-Protection Header",
        "description": "Legacy XSS filter not explicitly configured.",
        "severity": Severity.LOW,
        "recommendation": "Add: X-XSS-Protection: 1; mode=block"
    },
]

def run(url: str) -> ScannerResult:
    findings = []
    raw = {}

    try:
        resp = requests.get(url, timeout=10, allow_redirects=True, verify=False)
        headers = {k.lower(): v for k, v in resp.headers.items()}
        raw["status_code"] = resp.status_code
        raw["headers_found"] = list(resp.headers.keys())

        # Check each security header
        for check in HEADERS_CHECK:
            if check["header"].lower() not in headers:
                findings.append(Finding(
                    title=check["title"],
                    description=check["description"],
                    severity=check["severity"],
                    recommendation=check["recommendation"]
                ))

        # Server header info leak
        if "server" in headers:
            server_val = headers["server"]
            raw["server_header"] = server_val
            if any(tech in server_val.lower() for tech in ["apache/", "nginx/", "iis/", "php/"]):
                findings.append(Finding(
                    title="Server Version Disclosed",
                    description=f"Server header reveals version info: '{server_val}'",
                    severity=Severity.MEDIUM,
                    recommendation="Configure server to hide version info in the Server header."
                ))

        # X-Powered-By leak
        if "x-powered-by" in headers:
            findings.append(Finding(
                title="X-Powered-By Header Exposed",
                description=f"Technology stack exposed: {headers['x-powered-by']}",
                severity=Severity.LOW,
                recommendation="Remove the X-Powered-By header from server responses."
            ))

        if not findings:
            findings.append(Finding(
                title="All Security Headers Present",
                description="All recommended HTTP security headers are properly configured.",
                severity=Severity.INFO,
                recommendation="Great job! Continue monitoring for new header recommendations."
            ))

        return ScannerResult(scanner="HTTP Headers", status="completed", findings=findings, raw=raw)

    except Exception as e:
        return ScannerResult(scanner="HTTP Headers", status="error", findings=[], raw={"error": str(e)})