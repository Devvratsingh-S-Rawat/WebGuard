import { useState } from "react"
import { Radar } from "lucide-react"

function ScanForm({ onScan, loading }) {
  const [url, setUrl] = useState("")

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!url.trim()) return
    onScan(url.trim())
  }

  return (
    <div className="w-full flex flex-col items-center">
      <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
        <div
          className="flex items-center p-1.5 rounded-2xl transition-all duration-300"
          style={{
            background: "#13131f",
            border: "1.5px solid #3f3f5a",
            boxShadow: "0 4px 24px rgba(0,0,0,0.4)"
          }}
          onFocus={() => {}}
        >
          <span className="pl-4 pr-2 text-slate-400 flex-shrink-0">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="2" y1="12" x2="22" y2="12"/>
              <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </span>
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com"
            disabled={loading}
            className="flex-1 bg-transparent px-3 py-3 text-white placeholder-slate-500 outline-none text-sm min-w-0"
          />
          <button
            type="submit"
            disabled={loading || !url.trim()}
            className="flex items-center gap-2 px-6 py-3 rounded-xl bg-[#00d4aa] text-black font-medium text-sm hover:bg-[#00bfa0] active:scale-95 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
          >
            <Radar className="w-4 h-4" />
            {loading ? "Scanning..." : "Scan Now"}
          </button>
        </div>
      </form>

      <div className="flex items-center justify-center gap-12 mt-6 pb-6 border-b border-[#1e1e2e] w-full max-w-2xl mx-auto">
        {[["8", "Scanners"], ["OWASP", "Standard"], ["Live", "Progress"], ["PDF", "Reports"]].map(([num, label]) => (
          <div key={label} className="text-center">
            <div className="text-lg font-medium text-white">{num}</div>
            <div className="text-xs text-slate-600 mt-0.5">{label}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default ScanForm