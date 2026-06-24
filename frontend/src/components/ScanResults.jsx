import { CheckCircle, AlertTriangle, AlertOctagon, Info, XCircle, Download, RotateCcw } from "lucide-react"
import SummaryChart from "./SummaryChart"
import RiskScore from "./RiskScore"

const SEVERITY_CONFIG = {
  critical: { color: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", leftColor: "#e24b4a", icon: XCircle,      label: "Critical" },
  high:     { color: "text-orange-400", bg: "bg-orange-500/10", border: "border-orange-500/30", leftColor: "#ef9f27", icon: AlertOctagon,  label: "High" },
  medium:   { color: "text-yellow-400", bg: "bg-yellow-500/10", border: "border-yellow-500/30", leftColor: "#f5c542", icon: AlertTriangle, label: "Medium" },
  low:      { color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30", leftColor: "#3b8bd4", icon: Info,         label: "Low" },
  info:     { color: "text-slate-400", bg: "bg-slate-500/10", border: "border-slate-500/30", leftColor: "#475569", icon: CheckCircle,   label: "Info" },
}

function SeverityBadge({ severity }) {
  const config = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.info
  const Icon = config.icon
  return (
    <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full border ${config.color} ${config.bg} ${config.border} whitespace-nowrap`}>
      <Icon className="w-3 h-3" />
      {config.label}
    </span>
  )
}

function SummaryBar({ summary }) {
  const items = [
    { key: "critical", label: "Critical", color: "#e24b4a" },
    { key: "high",     label: "High",     color: "#ef9f27" },
    { key: "medium",   label: "Medium",   color: "#f5c542" },
    { key: "low",      label: "Low",      color: "#3b8bd4" },
    { key: "info",     label: "Info",     color: "#475569" },
  ]
  return (
    <div className="grid grid-cols-5 gap-3 mb-6">
      {items.map(({ key, label, color }, i) => (
        <div
          key={key}
          className={`flex flex-col items-center p-4 rounded-xl bg-[#111118] border border-[#1e1e2e] hover:border-[#00d4aa]/20 transition-colors animate-fade-in-up delay-${i + 1}`}
        >
          <div className="w-2 h-2 rounded-full mb-2" style={{ background: color }} />
          <span className="text-2xl font-medium text-white">{summary[key] || 0}</span>
          <span className="text-xs text-slate-600 mt-1">{label}</span>
        </div>
      ))}
    </div>
  )
}

function FindingCard({ finding }) {
  const config = SEVERITY_CONFIG[finding.severity] || SEVERITY_CONFIG.info
  return (
    <div
      className="p-4 rounded-xl bg-[#111118] border border-[#1e1e2e] hover:border-[#2d2d3d] transition-all duration-200"
      style={{ borderLeft: `2px solid ${config.leftColor}` }}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <h4 className="text-sm font-medium text-white leading-snug">{finding.title}</h4>
        <SeverityBadge severity={finding.severity} />
      </div>
      <p className="text-xs text-slate-500 mb-3 leading-relaxed">{finding.description}</p>
      <div className="text-xs text-[#00d4aa] bg-[#00d4aa]/5 border border-[#00d4aa]/10 rounded-lg px-3 py-2 leading-relaxed">
        💡 {finding.recommendation}
      </div>
    </div>
  )
}

function ScannerBlock({ result, index }) {
  return (
    <div className={`mb-6 animate-fade-in-up delay-${Math.min(index + 1, 6)}`}>
      <div className="flex items-center gap-3 mb-3">
        <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{result.scanner}</span>
        <span className={`text-xs px-2 py-0.5 rounded-full ${
          result.status === "completed"
            ? "bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20"
            : "bg-red-500/10 text-red-400 border border-red-500/20"
        }`}>
          {result.status}
        </span>
        <span className="text-xs text-slate-700">{result.findings.length} finding{result.findings.length !== 1 ? "s" : ""}</span>
      </div>
      <div className="flex flex-col gap-2">
        {result.findings.map((finding, i) => (
          <FindingCard key={i} finding={finding} />
        ))}
      </div>
    </div>
  )
}

function ScanResults({ results, url, onReset }) {
  const handleDownload = async () => {
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:5000"
    const res = await fetch(`${apiUrl}/api/scan/report`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    })
    const blob = await res.blob()
    const link = document.createElement("a")
    link.href = URL.createObjectURL(blob)
    link.download = `webguard-${results.target}.pdf`
    link.click()
  }

  return (
    <div className="mt-8 animate-fade-in">
      <div className="mb-6 flex items-start justify-between flex-wrap gap-4 animate-fade-in-up">
        <div>
          <h2 className="text-lg font-medium text-white">Scan Results</h2>
          <p className="text-slate-500 text-sm mt-1">
            Target: <span className="text-[#00d4aa]">{results.target}</span>
            <span className="mx-2 text-slate-700">·</span>
            {results.total_findings} findings
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={onReset}
            className="flex items-center gap-2 px-4 py-2 rounded-xl border border-[#1e1e2e] text-slate-400 text-sm hover:border-[#00d4aa]/30 hover:text-white transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            New Scan
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#00d4aa] text-black font-medium text-sm hover:bg-[#00bfa0] transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Download PDF
          </button>
        </div>
      </div>

      <RiskScore risk={results.risk_score} />
      <SummaryBar summary={results.summary} />
      <SummaryChart summary={results.summary} />
      <div className="border-t border-[#1e1e2e] mb-6" />

      <div>
        {results.results.map((result, i) => (
          <ScannerBlock key={i} result={result} index={i} />
        ))}
      </div>
    </div>
  )
}

export default ScanResults