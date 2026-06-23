function RiskScore({ risk }) {
  if (!risk) return null

  const circumference = 2 * Math.PI * 54
  const offset = circumference - (risk.score / 100) * circumference

  return (
    <div className="p-6 rounded-2xl border border-[#1e1e2e] bg-[#111118] mb-6">
      <h3 className="text-sm font-medium text-slate-500 uppercase tracking-wider mb-4">
        Security Risk Score
      </h3>
      <div className="flex items-center gap-8">

        {/* Circular progress */}
        <div className="relative flex-shrink-0">
          <svg width="130" height="130" viewBox="0 0 130 130">
            {/* Background circle */}
            <circle
              cx="65" cy="65" r="54"
              fill="none"
              stroke="#1e1e2e"
              strokeWidth="10"
            />
            {/* Progress circle */}
            <circle
              cx="65" cy="65" r="54"
              fill="none"
              stroke={risk.color}
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              transform="rotate(-90 65 65)"
              style={{ transition: "stroke-dashoffset 1s ease" }}
            />
            {/* Score text */}
            <text
              x="65" y="58"
              textAnchor="middle"
              fontSize="26"
              fontWeight="600"
              fill="#ffffff"
            >
              {risk.score}
            </text>
            <text
              x="65" y="76"
              textAnchor="middle"
              fontSize="11"
              fill="#64748b"
            >
              out of 100
            </text>
          </svg>
        </div>

        {/* Grade and details */}
        <div className="flex flex-col gap-4 flex-1">
          <div className="flex items-center gap-3">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold"
              style={{ background: `${risk.color}15`, border: `1px solid ${risk.color}30`, color: risk.color }}
            >
              {risk.grade}
            </div>
            <div>
              <div className="text-white font-medium text-base">{risk.label}</div>
              <div className="text-slate-500 text-xs mt-0.5">Overall security rating</div>
            </div>
          </div>

          {/* Score bar */}
          <div className="w-full">
            <div className="flex justify-between text-xs text-slate-600 mb-1.5">
              <span>0</span>
              <span>25</span>
              <span>50</span>
              <span>75</span>
              <span>100</span>
            </div>
            <div className="w-full h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-1000"
                style={{ width: `${risk.score}%`, background: risk.color }}
              />
            </div>
            <div className="flex justify-between text-xs mt-1.5">
              <span style={{ color: "#e24b4a" }}>F — Critical</span>
              <span style={{ color: "#ef9f27" }}>D — Poor</span>
              <span style={{ color: "#f5c542" }}>C — Moderate</span>
              <span style={{ color: "#3b8bd4" }}>B — Good</span>
              <span style={{ color: "#00d4aa" }}>A — Excellent</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskScore