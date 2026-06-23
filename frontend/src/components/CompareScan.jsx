import { X, ArrowLeft } from "lucide-react"

const SEVERITY_WEIGHTS = { critical: 4, high: 3, medium: 2, low: 1, info: 0 }

function getGradeColor(grade) {
  const colors = { A: "#00d4aa", B: "#3b8bd4", C: "#f5c542", D: "#ef9f27", F: "#e24b4a" }
  return colors[grade] || "#475569"
}

function ScoreCircle({ score, grade, color }) {
  const circumference = 2 * Math.PI * 36
  const offset = circumference - (score / 100) * circumference
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width="90" height="90" viewBox="0 0 90 90">
        <circle cx="45" cy="45" r="36" fill="none" stroke="#1e1e2e" strokeWidth="8" />
        <circle
          cx="45" cy="45" r="36"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          transform="rotate(-90 45 45)"
        />
        <text x="45" y="49" textAnchor="middle" fontSize="18" fontWeight="600" fill="#fff">{score}</text>
      </svg>
      <div
        className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold"
        style={{ background: `${color}15`, border: `1px solid ${color}30`, color }}
      >
        {grade}
      </div>
    </div>
  )
}

function SeverityRow({ label, colorHex, left, right }) {
  const max = Math.max(left, right, 1)
  const leftWorse = left > right
  const rightWorse = right > left
  return (
    <div className="grid grid-cols-3 gap-3 items-center py-2 border-b border-[#1e1e2e]">
      <div className="text-right">
        <span
          className="text-sm font-medium"
          style={{ color: leftWorse ? colorHex : "#e2e8f0" }}
        >
          {left}
          {leftWorse && " ▲"}
        </span>
      </div>
      <div className="flex items-center justify-center gap-2">
        <div className="w-2 h-2 rounded-full" style={{ background: colorHex }} />
        <span className="text-xs text-slate-500">{label}</span>
      </div>
      <div className="text-left">
        <span
          className="text-sm font-medium"
          style={{ color: rightWorse ? colorHex : "#e2e8f0" }}
        >
          {rightWorse && "▲ "}
          {right}
        </span>
      </div>
    </div>
  )
}

function CompareScan({ scanA, scanB, onClose }) {
  const scoreA = scanA.risk_score?.score ?? 0
  const scoreB = scanB.risk_score?.score ?? 0
  const gradeA = scanA.risk_score?.grade ?? "?"
  const gradeB = scanB.risk_score?.grade ?? "?"
  const colorA = getGradeColor(gradeA)
  const colorB = getGradeColor(gradeB)
  const winner = scoreA > scoreB ? "A" : scoreB > scoreA ? "B" : "tie"

  return (
    <div className="mt-8">
      <div className="flex items-center gap-3 mb-6">
        <button
          onClick={onClose}
          className="flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <h2 className="text-lg font-medium text-white">Compare Scans</h2>
      </div>

      {/* Header */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="p-4 rounded-2xl border border-[#1e1e2e] bg-[#111118] text-center"
          style={{ borderColor: winner === "A" ? `${colorA}40` : "#1e1e2e" }}>
          <div className="text-sm font-medium text-white mb-1 truncate">{scanA.target}</div>
          <div className="text-xs text-slate-500 mb-3">{scanA.scanned_at}</div>
          <ScoreCircle score={scoreA} grade={gradeA} color={colorA} />
          <div className="text-xs mt-2" style={{ color: colorA }}>{scanA.risk_score?.label}</div>
          {winner === "A" && (
            <div className="mt-2 text-xs px-2 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20 inline-block">
              🏆 More Secure
            </div>
          )}
        </div>

        <div className="flex flex-col items-center justify-center gap-2">
          <div className="text-2xl font-bold text-slate-700">VS</div>
          <div className="text-xs text-slate-600 text-center">
            {winner === "tie"
              ? "Both sites are equally secure"
              : `${winner === "A" ? scanA.target : scanB.target} is more secure`}
          </div>
          <div className="text-xs text-slate-700 mt-1">
            Δ {Math.abs(scoreA - scoreB)} points difference
          </div>
        </div>

        <div className="p-4 rounded-2xl border border-[#1e1e2e] bg-[#111118] text-center"
          style={{ borderColor: winner === "B" ? `${colorB}40` : "#1e1e2e" }}>
          <div className="text-sm font-medium text-white mb-1 truncate">{scanB.target}</div>
          <div className="text-xs text-slate-500 mb-3">{scanB.scanned_at}</div>
          <ScoreCircle score={scoreB} grade={gradeB} color={colorB} />
          <div className="text-xs mt-2" style={{ color: colorB }}>{scanB.risk_score?.label}</div>
          {winner === "B" && (
            <div className="mt-2 text-xs px-2 py-1 rounded-full bg-[#00d4aa]/10 text-[#00d4aa] border border-[#00d4aa]/20 inline-block">
              🏆 More Secure
            </div>
          )}
        </div>
      </div>

      {/* Severity comparison */}
      <div className="p-5 rounded-2xl border border-[#1e1e2e] bg-[#111118] mb-6">
        <h3 className="text-xs font-medium text-slate-500 uppercase tracking-wider mb-4">
          Findings Comparison
        </h3>
        <div className="grid grid-cols-3 gap-3 mb-2">
          <div className="text-center text-xs font-medium text-slate-400 truncate">{scanA.target}</div>
          <div className="text-center text-xs text-slate-600">Severity</div>
          <div className="text-center text-xs font-medium text-slate-400 truncate">{scanB.target}</div>
        </div>
        {[
          { key: "critical", label: "Critical", color: "#e24b4a" },
          { key: "high",     label: "High",     color: "#ef9f27" },
          { key: "medium",   label: "Medium",   color: "#f5c542" },
          { key: "low",      label: "Low",      color: "#3b8bd4" },
          { key: "info",     label: "Info",     color: "#475569" },
        ].map(({ key, label, color }) => (
          <SeverityRow
            key={key}
            label={label}
            colorHex={color}
            left={scanA.summary?.[key] ?? 0}
            right={scanB.summary?.[key] ?? 0}
          />
        ))}
        <div className="grid grid-cols-3 gap-3 items-center pt-3">
          <div className="text-right text-sm font-bold text-white">{scanA.total_findings} total</div>
          <div className="text-center text-xs text-slate-600">Total</div>
          <div className="text-left text-sm font-bold text-white">{scanB.total_findings} total</div>
        </div>
      </div>
    </div>
  )
}

export default CompareScan