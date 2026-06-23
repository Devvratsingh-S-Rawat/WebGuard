import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import ScannerResult, Finding, Severity

PORTS = {
    21:   ("FTP",        Severity.HIGH,   "FTP is unencrypted. Use SFTP or FTPS instead."),
    22:   ("SSH",        Severity.INFO,   "SSH is open. Ensure key-based auth and disable root login."),
    23:   ("Telnet",     Severity.CRITICAL,"Telnet sends data in plaintext. Disable immediately, use SSH."),
    25:   ("SMTP",       Severity.MEDIUM, "SMTP open. Ensure it's not an open relay."),
    53:   ("DNS",        Severity.INFO,   "DNS port open. Normal for DNS servers."),
    80:   ("HTTP",       Severity.INFO,   "HTTP open. Ensure traffic is redirected to HTTPS."),
    443:  ("HTTPS",      Severity.INFO,   "HTTPS open. Standard secure web port."),
    3306: ("MySQL",      Severity.CRITICAL,"MySQL exposed to the internet. Bind to localhost only."),
    3389: ("RDP",        Severity.HIGH,   "RDP exposed. High risk of brute-force. Use VPN or restrict IP."),
    5432: ("PostgreSQL", Severity.CRITICAL,"PostgreSQL exposed. Bind to localhost only."),
    6379: ("Redis",      Severity.CRITICAL,"Redis exposed without auth by default. Restrict access immediately."),
    8080: ("HTTP-Alt",   Severity.MEDIUM, "Alt HTTP port open. May expose dev server or admin panels."),
    8443: ("HTTPS-Alt",  Severity.INFO,   "Alt HTTPS port open."),
    27017:("MongoDB",    Severity.CRITICAL,"MongoDB exposed. Often configured without auth. Restrict immediately."),
}

def check_port(hostname: str, port: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except:
        return False

def run(hostname: str) -> ScannerResult:
    findings = []
    raw = {"open_ports": [], "checked_ports": list(PORTS.keys())}

    try:
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_map = {executor.submit(check_port, hostname, port): port for port in PORTS}
            for future in as_completed(future_map):
                port = future_map[future]
                is_open = future.result()
                if is_open:
                    raw["open_ports"].append(port)
                    name, severity, rec = PORTS[port]
                    findings.append(Finding(
                        title=f"Port {port} ({name}) Open",
                        description=f"Port {port} ({name}) is accessible from the internet.",
                        severity=severity,
                        recommendation=rec
                    ))

        # Sort findings by severity weight
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        findings.sort(key=lambda f: sev_order.get(f.severity.value, 5))

        if not findings:
            findings.append(Finding(
                title="No Dangerous Ports Detected",
                description="No commonly dangerous ports are publicly accessible.",
                severity=Severity.INFO,
                recommendation="Continue monitoring for newly exposed ports."
            ))

        return ScannerResult(scanner="Port Scanner", status="completed", findings=findings, raw=raw)

    except Exception as e:
        return ScannerResult(scanner="Port Scanner", status="error", findings=[], raw={"error": str(e)})