import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from models import ScannerResult, Finding, Severity

MAX_LINKS = 30  # Max links to check per scan

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except:
        return False

def check_link(url: str) -> tuple:
    try:
        resp = requests.head(url, timeout=6, allow_redirects=True, verify=False)
        return url, resp.status_code
    except requests.exceptions.Timeout:
        return url, "timeout"
    except:
        return url, "error"

def run(url: str) -> ScannerResult:
    findings = []
    raw = {
        "total_links": 0,
        "checked_links": 0,
        "broken_links": [],
        "redirect_links": []
    }

    try:
        resp = requests.get(url, timeout=10, verify=False, allow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")

        # Collect all links
        all_links = set()
        base_domain = urlparse(url).netloc

        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            full_url = urljoin(url, href)
            if is_valid_url(full_url):
                all_links.add(full_url)

        raw["total_links"] = len(all_links)
        links_to_check = list(all_links)[:MAX_LINKS]
        raw["checked_links"] = len(links_to_check)

        broken = []
        redirects = []

        from concurrent.futures import ThreadPoolExecutor, as_completed
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(check_link, link): link for link in links_to_check}
            for future in as_completed(futures):
                link, status = future.result()
                if status in (404, 410, "timeout", "error"):
                    broken.append({"url": link, "status": str(status)})
                elif status in (301, 302, 307, 308):
                    redirects.append({"url": link, "status": str(status)})

        raw["broken_links"] = broken
        raw["redirect_links"] = redirects

        # Add findings for broken links
        if broken:
            for b in broken[:5]:  # Report first 5
                findings.append(Finding(
                    title=f"Broken Link Detected ({b['status']})",
                    description=f"URL returned {b['status']}: {b['url'][:80]}",
                    severity=Severity.LOW,
                    recommendation="Remove or update this broken link to improve security and user experience."
                ))
            if len(broken) > 5:
                findings.append(Finding(
                    title=f"{len(broken) - 5} More Broken Links Found",
                    description=f"Total broken links detected: {len(broken)}",
                    severity=Severity.LOW,
                    recommendation="Audit all broken links and fix or remove them."
                ))
        
        # Add findings for excessive redirects
        if len(redirects) > 5:
            findings.append(Finding(
                title=f"Excessive Redirects Detected ({len(redirects)} links)",
                description=f"{len(redirects)} links are redirecting. Redirect chains slow down the site.",
                severity=Severity.INFO,
                recommendation="Update links to point directly to final destinations where possible."
            ))

        if not findings:
            findings.append(Finding(
                title="No Broken Links Detected",
                description=f"Checked {len(links_to_check)} links — all returned valid responses.",
                severity=Severity.INFO,
                recommendation="Continue monitoring links regularly as external URLs can break over time."
            ))

        return ScannerResult(
            scanner="Broken Links",
            status="completed",
            findings=findings,
            raw=raw
        )

    except Exception as e:
        return ScannerResult(
            scanner="Broken Links",
            status="error",
            findings=[],
            raw={"error": str(e)}
        )