import { ShieldCheck } from "lucide-react"

function Hero() {
  return (
    <header className="relative text-center py-16 px-6 flex flex-col items-center overflow-hidden">
      {/* Background glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ background: "radial-gradient(ellipse, #00d4aa 0%, transparent 70%)" }}
      />

      {/* Eyebrow badge */}
      <div className="relative inline-flex items-center gap-2 text-xs text-[#00d4aa] bg-[#00d4aa]/5 border border-[#00d4aa]/20 rounded-full px-3 py-1.5 mb-6">
        <ShieldCheck className="w-3 h-3" />
        Black Box Security Scanner
      </div>

      {/* Title */}
      <h1 className="relative text-5xl font-medium text-white tracking-tight leading-tight mb-4">
        Find vulnerabilities<br />
        before <span className="text-[#00d4aa]">hackers do</span>
      </h1>

      {/* Subtitle */}
      <p className="relative text-slate-500 text-base max-w-lg mx-auto leading-relaxed mb-8 text-center">
        Enter any website URL and WebGuard runs 8 security scanners in real time — SSL, headers, ports, DNS, SQLi, XSS, CMS, and broken links.
      </p>

      {/* Tags */}
      <div className="relative flex items-center justify-center gap-2 flex-wrap mb-8">
        {["SSL / TLS", "HTTP Headers", "Open Ports", "WHOIS & DNS", "SQL Injection", "XSS Detection", "CMS Detection", "Broken Links"].map((tag) => (
          <span key={tag} className="text-xs px-3 py-1 rounded-full border border-[#1e1e2e] text-slate-500 hover:border-[#00d4aa]/20 hover:text-slate-400 transition-colors">
            {tag}
          </span>
        ))}
      </div>
    </header>
  )
}

export default Hero