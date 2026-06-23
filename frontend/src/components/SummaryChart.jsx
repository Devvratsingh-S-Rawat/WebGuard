import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts"

const COLORS = {
  critical: "#e24b4a",
  high:     "#ef9f27",
  medium:   "#f5c542",
  low:      "#3b8bd4",
  info:     "#64748b",
}

const LABELS = {
  critical: "Critical",
  high:     "High",
  medium:   "Medium",
  low:      "Low",
  info:     "Info",
}

function SummaryChart({ summary }) {
  const data = Object.entries(summary)
    .filter(([_, value]) => value > 0)
    .map(([key, value]) => ({
      name: LABELS[key],
      value,
      color: COLORS[key],
    }))

  if (data.length === 0) return null

  return (
    <div className="p-6 rounded-2xl border border-[#2d2d3d] bg-[#111118] mb-8">
      <h3 className="text-sm font-semibold text-white mb-4">Vulnerability Breakdown</h3>
      <div className="flex flex-col md:flex-row items-center gap-6">
        <ResponsiveContainer width={220} height={220}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={3}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={entry.color} strokeWidth={0} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#111118",
                border: "1px solid #2d2d3d",
                borderRadius: "8px",
                color: "#e2e8f0",
                fontSize: "12px",
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex flex-col gap-3 flex-1">
          {data.map((entry) => (
            <div key={entry.name} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full" style={{ background: entry.color }} />
                <span className="text-sm text-slate-300">{entry.name}</span>
              </div>
              <span className="text-sm font-bold text-white">{entry.value}</span>
            </div>
          ))}
          <div className="mt-2 pt-3 border-t border-[#2d2d3d] flex items-center justify-between">
            <span className="text-xs text-slate-400">Total Findings</span>
            <span className="text-sm font-bold text-[#00d4aa]">
              {data.reduce((a, b) => a + b.value, 0)}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SummaryChart