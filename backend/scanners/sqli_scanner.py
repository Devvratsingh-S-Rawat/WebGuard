import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from models import ScannerResult, Finding, Severity

SQLI_PAYLOADS = [
    "'",
    "''",
    "' OR '1'='1",
    "' OR 1=1--",
    "\" OR \"1\"=\"1",
    "' OR 'x'='x",
    "'; DROP TABLE users--",
    "1' ORDER BY 1--",
    "1' ORDER BY 2--",
    "' UNION SELECT NULL--",
]

SQLI_ERRORS = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "sqlstate",
    "ora-01756",
    "microsoft ole db provider for sql server",
    "odbc sql server driver",
    "postgresql error",
    "pg_query()",
    "sqlite3.operationalerror",
    "sqlite_error",
    "syntax error in query expression",
    "data type mismatch",
    "mysql_fetch",
    "num_rows",
]

def inject_payload(url: str, param: str, payload: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def run(url: str) -> ScannerResult:
    findings = []
    raw = {"tested_params": [], "vulnerable_params": []}

    try:
        # Get the page and find query parameters
        resp = requests.get(url, timeout=10, verify=False)
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        if not params:
            # Try common vulnerable params if none in URL
            test_params = ["id", "page", "search", "q", "user", "item"]
            base = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            params = {p: ["1"] for p in test_params}
            test_url = base + "?" + urlencode({p: "1" for p in test_params})
        else:
            test_url = url

        raw["tested_params"] = list(params.keys())
        vulnerable = []

        for param in params:
            for payload in SQLI_PAYLOADS[:5]:  # Test first 5 payloads per param
                injected_url = inject_payload(test_url, param, payload)
                try:
                    r = requests.get(injected_url, timeout=8, verify=False)
                    body = r.text.lower()
                    for error in SQLI_ERRORS:
                        if error in body:
                            vulnerable.append(param)
                            findings.append(Finding(
                                title=f"SQL Injection Detected in '{param}' Parameter",
                                description=f"Parameter '{param}' is vulnerable to SQL injection. DB error triggered with payload: {payload}",
                                severity=Severity.CRITICAL,
                                recommendation=f"Sanitize and parameterize all database queries. Never trust user input in '{param}'."
                            ))
                            break
                except:
                    continue
            if param in vulnerable:
                raw["vulnerable_params"].append(param)

        if not findings:
            findings.append(Finding(
                title="No SQL Injection Detected",
                description="No obvious SQL injection vulnerabilities found in URL parameters.",
                severity=Severity.INFO,
                recommendation="Continue using parameterized queries and input validation."
            ))

        return ScannerResult(scanner="SQL Injection", status="completed", findings=findings, raw=raw)

    except Exception as e:
        return ScannerResult(scanner="SQL Injection", status="error", findings=[], raw={"error": str(e)})