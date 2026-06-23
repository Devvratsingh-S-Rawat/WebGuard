import whois
import dns.resolver
from datetime import datetime, timezone
from models import ScannerResult, Finding, Severity

def run(hostname: str) -> ScannerResult:
    findings = []
    raw = {}

    # --- WHOIS ---
    try:
        w = whois.whois(hostname)
        creation = w.creation_date
        if isinstance(creation, list):
            creation = creation[0]

        raw["registrar"] = str(w.registrar) if w.registrar else "Unknown"
        raw["country"]   = str(w.country)   if w.country   else "Unknown"

        if creation:
            creation = creation.replace(tzinfo=timezone.utc) if creation.tzinfo is None else creation
            age_days = (datetime.now(timezone.utc) - creation).days
            raw["domain_age_days"] = age_days
            raw["creation_date"]   = str(creation)

            if age_days < 30:
                findings.append(Finding(
                    title="Very New Domain",
                    description=f"Domain is only {age_days} days old. Newly registered domains are often associated with phishing.",
                    severity=Severity.HIGH,
                    recommendation="Exercise extreme caution with very new domains."
                ))
            elif age_days < 180:
                findings.append(Finding(
                    title="Recently Registered Domain",
                    description=f"Domain is {age_days} days old ({age_days//30} months).",
                    severity=Severity.MEDIUM,
                    recommendation="Verify the domain's legitimacy before trusting it."
                ))
            else:
                findings.append(Finding(
                    title="Established Domain",
                    description=f"Domain has been registered for {age_days // 365} year(s).",
                    severity=Severity.INFO,
                    recommendation="Domain age looks good."
                ))
    except Exception as e:
        raw["whois_error"] = str(e)

    # --- DNS Records ---
    try:
        dns_data = {}
        for rtype in ["A", "MX", "TXT", "NS"]:
            try:
                answers = dns.resolver.resolve(hostname, rtype, lifetime=5)
                dns_data[rtype] = [r.to_text() for r in answers]
            except:
                dns_data[rtype] = []

        raw["dns"] = dns_data

        # SPF check
        txt_records = " ".join(dns_data.get("TXT", []))
        if "v=spf1" not in txt_records:
            findings.append(Finding(
                title="No SPF Record Found",
                description="No SPF (Sender Policy Framework) DNS record detected. Email spoofing is possible.",
                severity=Severity.MEDIUM,
                recommendation="Add an SPF TXT record to prevent email spoofing: v=spf1 include:... -all"
            ))

        # DMARC check
        try:
            dmarc = dns.resolver.resolve(f"_dmarc.{hostname}", "TXT", lifetime=5)
            raw["dmarc"] = [r.to_text() for r in dmarc]
        except:
            raw["dmarc"] = []
            findings.append(Finding(
                title="No DMARC Record Found",
                description="DMARC policy not set. Emails from this domain can be spoofed.",
                severity=Severity.MEDIUM,
                recommendation="Add a DMARC TXT record: _dmarc.yourdomain.com → v=DMARC1; p=reject;"
            ))

    except Exception as e:
        raw["dns_error"] = str(e)

    return ScannerResult(scanner="WHOIS / DNS", status="completed", findings=findings, raw=raw)