import { History, Trash2, ExternalLink, GitCompare } from "lucide-react"

function ScanHistory({ history, onSelect, onClear, compareMode, compareA, compareB, onToggleCompare }) {
  if (!history || history.length === 0) return null

  const getGradeColor = (grade) => {
    const colors = { A: "#00d4aa", B: "#3b8bd4", C: "#f5c542", D: "#ef9f27", F: "#e24b4a" }
    return colors[grade] || "#475569"
  }

  const isSelected = (item) => {
    return (compareA?.target === item.target) || (compareB?.target === item.target)
  }

  return (
    <div className="mt-8 mb-2">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">
            Recent Scans
          </span>
        </div>
        <div className="flex items-center gap-3">
          {history.length >= 2 && (
            <button
              onClick={onToggleCompare}
              className={`flex items-center gap-1.5 text-xs transition-colors ${
                compareMode
                  ? "text-[#00d4aa]"
                  : "text-slate-600 hover:text-[#00d4aa]"
              }`}
            >
              <GitCompare className="w-3.5 h-3.5" />
              {compareMode ? "Cancel Compare" : "Compare"}
            </button>
          )}
          <button
            onClick={onClear}
            className="flex items-center gap-1.5 text-xs text-slate-600 hover:text-red-400 transition-colors"
          >
            <Trash2 className="w-3 h-3" />
            Clear
          </button>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        {history.map((item, i) => {
          const selected = isSelected(item)
          return (
            <div
              key={i}
              onClick={() => onSelect(item)}
              className="flex items-center justify-between p-3 rounded-xl bg-[#111118] border transition-all duration-200 group cursor-pointer"
              style={{
                borderColor: selected ? "#00d4aa40" : "#1e1e2e",
                background: selected ? "#00d4aa08" : "#111118"
              }}
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
                  style={{
                    background: `${getGradeColor(item.risk_score?.grade)}15`,
                    border: `1px solid ${getGradeColor(item.risk_score?.grade)}30`,
                    color: getGradeColor(item.risk_score?.grade)
                  }}
                >
                  {item.risk_score?.grade || "?"}
                </div>
                <div>
                  <div className="text-sm font-medium text-white">{item.target}</div>
                  <div className="text-xs text-slate-600 mt-0.5">
                    {item.total_findings} findings · {item.scanned_at}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3">
                {selected && (
                  <span className="text-xs text-[#00d4aa]">
                    {compareA?.target === item.target ? "①" : "②"}
                  </span>
                )}
                <span
                  className="text-xs font-medium"
                  style={{ color: getGradeColor(item.risk_score?.grade) }}
                >
                  {item.risk_score?.score}/100
                </span>
                <ExternalLink className="w-3.5 h-3.5 text-slate-700 group-hover:text-[#00d4aa] transition-colors" />
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ScanHistory