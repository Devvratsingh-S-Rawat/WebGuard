import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from bs4 import BeautifulSoup
from models import ScannerResult, Finding, Severity

XSS_PAYLOADS = [
    "<script>alert('xss')</script>",
    "<img src=x onerror=alert('xss')>",
    "'\"><script>alert('xss')</script>",
    "<svg onload=alert('xss')>",
    "javascript:alert('xss')",
    "<body onload=alert('xss')>",
    "\"><img src=x onerror=alert(1)>",
    "<iframe src=javascript:alert('xss')>",
]

def inject_payload(url: str, param: str, payload: str) -> str:
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    params[param] = [payload]
    new_query = urlencode(params, doseq=True)
    return urlunparse(parsed._replace(query=new_query))

def run(url: str) -> ScannerResult:
    findings = []
    raw = {"tested_params": [], "vulnerable_params": [], "forms_tested": 0}

    try:
        resp = requests.get(url, timeout=10, verify=False)
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # --- Test URL parameters ---
        if params:
            raw["tested_params"] = list(params.keys())
            for param in params:
                for payload in XSS_PAYLOADS[:4]:
                    injected_url = inject_payload(url, param, payload)
                    try:
                        r = requests.get(injected_url, timeout=8, verify=False)
                        if payload.lower() in r.text.lower():
                            raw["vulnerable_params"].append(param)
                            findings.append(Finding(
                                title=f"Reflected XSS in '{param}' Parameter",
                                description=f"Parameter '{param}' reflects unsanitized input. Payload was found in response: {payload[:40]}",
                                severity=Severity.CRITICAL,
                                recommendation=f"Encode all output and sanitize input for '{param}'. Use a Content Security Policy."
                            ))
                            break
                    except:
                        continue

        # --- Test forms ---
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            forms = soup.find_all("form")
            raw["forms_tested"] = len(forms)

            for form in forms[:3]:  # Test first 3 forms
                action = form.get("action", url)
                method = form.get("method", "get").lower()
                inputs = form.find_all("input")

                form_data = {}
                for inp in inputs:
                    name = inp.get("name")
                    if name:
                        form_data[name] = XSS_PAYLOADS[0]

                if not form_data:
                    continue

                try:
                    if method == "post":
                        r = requests.post(action, data=form_data, timeout=8, verify=False)
                    else:
                        r = requests.get(action, params=form_data, timeout=8, verify=False)

                    for payload in XSS_PAYLOADS[:3]:
                        if payload.lower() in r.text.lower():
                            findings.append(Finding(
                                title="Reflected XSS in Form Input",
                                description=f"A form on the page reflects unsanitized input back in the response.",
                                severity=Severity.CRITICAL,
                                recommendation="Sanitize all form inputs and encode output. Implement CSP headers."
                            ))
                            break
                except:
                    continue
        except:
            pass

        if not findings:
            findings.append(Finding(
                title="No XSS Vulnerabilities Detected",
                description="No reflected XSS vulnerabilities found in URL parameters or forms.",
                severity=Severity.INFO,
                recommendation="Continue sanitizing inputs and encoding outputs. Maintain a strong CSP policy."
            ))

        return ScannerResult(scanner="XSS Scanner", status="completed", findings=findings, raw=raw)

    except Exception as e:
        return ScannerResult(scanner="XSS Scanner", status="error", findings=[], raw={"error": str(e)})