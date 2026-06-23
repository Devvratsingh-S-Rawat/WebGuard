import requests
from models import ScannerResult, Finding, Severity

CMS_SIGNATURES = {
    "WordPress": {
        "checks": [
            lambda h, b: "/wp-content/" in b,
            lambda h, b: "/wp-includes/" in b,
            lambda h, b: 'name="generator" content="WordPress' in b,
            lambda h, b: "wp-json" in b,
        ],
        "severity": Severity.MEDIUM,
        "description": "Site is running WordPress. WordPress is the most targeted CMS by attackers due to its popularity.",
        "recommendation": "Keep WordPress core, themes, and plugins updated. Use a security plugin like Wordfence. Disable XML-RPC if not needed."
    },
    "Joomla": {
        "checks": [
            lambda h, b: "/components/com_" in b,
            lambda h, b: "/media/jui/" in b,
            lambda h, b: 'name="generator" content="Joomla' in b,
            lambda h, b: "/administrator/" in b,
        ],
        "severity": Severity.MEDIUM,
        "description": "Site is running Joomla. Outdated Joomla installations are frequently exploited.",
        "recommendation": "Update Joomla to the latest version. Audit installed extensions and remove unused ones."
    },
    "Drupal": {
        "checks": [
            lambda h, b: "/sites/default/files/" in b,
            lambda h, b: "Drupal.settings" in b,
            lambda h, b: 'name="generator" content="Drupal' in b,
            lambda h, b: "/core/misc/drupal.js" in b,
        ],
        "severity": Severity.MEDIUM,
        "description": "Site is running Drupal. Drupal has had critical vulnerabilities like Drupalgeddon2.",
        "recommendation": "Keep Drupal core and modules updated. Monitor security advisories at drupal.org/security."
    },
    "Wix": {
        "checks": [
            lambda h, b: "wix.com" in b,
            lambda h, b: "_wix_" in b,
            lambda h, b: "wixstatic.com" in b,
        ],
        "severity": Severity.INFO,
        "description": "Site is built with Wix — a hosted website builder.",
        "recommendation": "Wix manages security updates automatically. Ensure your Wix account uses 2FA."
    },
    "Shopify": {
        "checks": [
            lambda h, b: "cdn.shopify.com" in b,
            lambda h, b: "shopify.com/s/files" in b,
            lambda h, b: "Shopify.theme" in b,
        ],
        "severity": Severity.INFO,
        "description": "Site is running on Shopify — a hosted e-commerce platform.",
        "recommendation": "Shopify manages core security. Audit installed apps and use 2FA on your account."
    },
    "Laravel": {
        "checks": [
            lambda h, b: "laravel_session" in h.get("set-cookie", ""),
            lambda h, b: "Laravel" in h.get("x-powered-by", ""),
            lambda h, b: "XSRF-TOKEN" in h.get("set-cookie", ""),
        ],
        "severity": Severity.INFO,
        "description": "Site appears to use the Laravel PHP framework.",
        "recommendation": "Ensure Laravel is updated to the latest stable version. Keep .env file protected and never expose it publicly."
    },
    "Django": {
        "checks": [
            lambda h, b: "csrftoken" in h.get("set-cookie", ""),
            lambda h, b: "django" in h.get("x-powered-by", "").lower(),
        ],
        "severity": Severity.INFO,
        "description": "Site appears to use the Django Python framework.",
        "recommendation": "Ensure DEBUG=False in production. Keep Django updated and use HTTPS."
    },
}

def run(url: str) -> ScannerResult:
    findings = []
    raw = {"detected_cms": [], "checked": list(CMS_SIGNATURES.keys())}

    try:
        resp = requests.get(url, timeout=10, verify=False, allow_redirects=True)
        body = resp.text
        headers = {k.lower(): v for k, v in resp.headers.items()}

        for cms_name, cms_data in CMS_SIGNATURES.items():
            matched = any(check(headers, body) for check in cms_data["checks"])
            if matched:
                raw["detected_cms"].append(cms_name)
                findings.append(Finding(
                    title=f"{cms_name} Detected",
                    description=cms_data["description"],
                    severity=cms_data["severity"],
                    recommendation=cms_data["recommendation"]
                ))

        if not findings:
            findings.append(Finding(
                title="No Common CMS Detected",
                description="No fingerprints of common CMS platforms (WordPress, Joomla, Drupal, etc.) were found.",
                severity=Severity.INFO,
                recommendation="Custom-built sites are harder to fingerprint — this is generally a good sign."
            ))

        return ScannerResult(scanner="CMS Detection", status="completed", findings=findings, raw=raw)

    except Exception as e:
        return ScannerResult(scanner="CMS Detection", status="error", findings=[], raw={"error": str(e)})