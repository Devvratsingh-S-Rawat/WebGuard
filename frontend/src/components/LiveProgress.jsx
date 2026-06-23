import { CheckCircle, Loader, Info, Terminal } from "lucide-react"

function LiveProgress({ progress, currentScanner }) {
  return (
    <div className="w-full max-w-2xl mx-auto mt-16">
      {/* Terminal header */}
      <div className="flex items-center gap-2 px-4 py-3 rounded-t-2xl border border-b-0 border-[#1e1e2e] bg-[#0d0d1a]">
        <div className="flex gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-500/60" />
          <div className="w-3 h-3 rounded-full bg-yellow-500/60" />
          <div className="w-3 h-3 rounded-full bg-green-500/60" />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Terminal className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-xs text-slate-500 font-mono">webguard — scan</span>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 rounded-full bg-[#00d4aa] animate-pulse" />
          <span className="text-xs text-[#00d4aa] font-mono">scanning...</span>
        </div>
      </div>

      {/* Terminal body */}
      <div className="px-5 py-4 rounded-b-2xl border border-[#1e1e2e] bg-[#0d0d1a] font-mono">
        <div className="flex flex-col gap-2.5">
          {progress.map((item, i) => (
            <div key={i} className="flex items-center gap-3">
              {item.status === "done" ? (
                <CheckCircle className="w-3.5 h-3.5 text-[#00d4aa] flex-shrink-0" />
              ) : item.status === "running" ? (
                <Loader className="w-3.5 h-3.5 text-yellow-400 flex-shrink-0 animate-spin" />
              ) : (
                <Info className="w-3.5 h-3.5 text-slate-500 flex-shrink-0" />
              )}
              <span className={`text-xs ${
                item.status === "done"
                  ? "text-[#00d4aa]"
                  : item.status === "running"
                  ? "text-yellow-400"
                  : "text-slate-500"
              }`}>
                {item.status === "running" && (
                  <span className="text-slate-600 mr-1">$</span>
                )}
                {item.message}
              </span>
            </div>
          ))}

          {/* Blinking cursor */}
          {currentScanner && (
            <div className="flex items-center gap-3 mt-1">
              <span className="text-slate-600 text-xs">$</span>
              <span className="text-xs text-slate-600">
                Running <span className="text-[#00d4aa]">{currentScanner}</span>
              </span>
              <span className="inline-block w-2 h-3.5 bg-[#00d4aa] animate-pulse ml-0.5" />
            </div>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-slate-600 mb-1.5">
          <span>{progress.filter(p => p.status === "done").length} of 8 scanners complete</span>
          <span>{Math.round((progress.filter(p => p.status === "done").length / 8) * 100)}%</span>
        </div>
        <div className="w-full h-1 bg-[#1e1e2e] rounded-full overflow-hidden">
          <div
            className="h-full bg-[#00d4aa] rounded-full transition-all duration-500"
            style={{ width: `${(progress.filter(p => p.status === "done").length / 8) * 100}%` }}
          />
        </div>
      </div>
    </div>
  )
}

export default LiveProgress