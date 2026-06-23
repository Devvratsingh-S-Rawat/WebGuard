import ssl
import socket
from datetime import datetime, timezone
from models import ScannerResult, Finding, Severity

def run(hostname: str) -> ScannerResult:
    findings = []
    raw = {}

    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(10)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            cipher = s.cipher()

        # --- Expiry check ---
        expire_str = cert.get("notAfter", "")
        if expire_str:
            expire_dt = datetime.strptime(expire_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_left = (expire_dt - now).days
            raw["expires_in_days"] = days_left
            raw["expiry_date"] = expire_str

            if days_left < 0:
                findings.append(Finding(
                    title="SSL Certificate Expired",
                    description=f"The SSL certificate expired {abs(days_left)} days ago.",
                    severity=Severity.CRITICAL,
                    recommendation="Renew your SSL certificate immediately."
                ))
            elif days_left < 15:
                findings.append(Finding(
                    title="SSL Certificate Expiring Soon",
                    description=f"Certificate expires in {days_left} days.",
                    severity=Severity.HIGH,
                    recommendation="Renew your SSL certificate before it expires."
                ))
            elif days_left < 30:
                findings.append(Finding(
                    title="SSL Certificate Expiring Soon",
                    description=f"Certificate expires in {days_left} days.",
                    severity=Severity.MEDIUM,
                    recommendation="Plan SSL certificate renewal within the next 30 days."
                ))

        # --- Cipher strength check ---
        if cipher:
            cipher_name = cipher[0]
            tls_version = cipher[1]
            raw["cipher"] = cipher_name
            raw["tls_version"] = tls_version

            weak_ciphers = ["RC4", "DES", "3DES", "MD5", "NULL", "EXPORT", "anon"]
            if any(w in cipher_name for w in weak_ciphers):
                findings.append(Finding(
                    title="Weak Cipher Suite Detected",
                    description=f"The server is using weak cipher: {cipher_name}",
                    severity=Severity.HIGH,
                    recommendation="Configure the server to use strong cipher suites (AES-GCM, CHACHA20)."
                ))

            if tls_version in ["TLSv1", "TLSv1.1", "SSLv2", "SSLv3"]:
                findings.append(Finding(
                    title="Outdated TLS Version",
                    description=f"Server uses {tls_version} which is deprecated and insecure.",
                    severity=Severity.HIGH,
                    recommendation="Upgrade to TLS 1.2 or TLS 1.3."
                ))

        # --- Subject / issuer ---
        subject = dict(x[0] for x in cert.get("subject", []))
        issuer  = dict(x[0] for x in cert.get("issuer", []))
        raw["subject"] = subject
        raw["issuer"]  = issuer

        if not findings:
            findings.append(Finding(
                title="SSL Certificate Valid",
                description=f"Certificate is valid for {raw.get('expires_in_days','?')} more days. TLS: {raw.get('tls_version','?')}",
                severity=Severity.INFO,
                recommendation="No action needed. Keep monitoring expiry."
            ))

        return ScannerResult(scanner="SSL/TLS", status="completed", findings=findings, raw=raw)

    except ssl.SSLError as e:
        findings.append(Finding(
            title="SSL Error",
            description=str(e),
            severity=Severity.CRITICAL,
            recommendation="Investigate and fix the SSL configuration on your server."
        ))
        return ScannerResult(scanner="SSL/TLS", status="completed", findings=findings)

    except Exception as e:
        return ScannerResult(scanner="SSL/TLS", status="error", findings=[], raw={"error": str(e)})