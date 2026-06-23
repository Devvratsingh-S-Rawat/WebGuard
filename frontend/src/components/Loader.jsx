import { Shield } from "lucide-react"

function Loader() {
  return (
    <div className="flex flex-col items-center justify-center py-20 gap-6">
      <div className="relative">
        <div className="w-20 h-20 rounded-full border-2 border-[#00d4aa]/20 animate-ping absolute inset-0" />
        <div className="w-20 h-20 rounded-full border-2 border-t-[#00d4aa] border-[#00d4aa]/10 animate-spin" />
        <div className="absolute inset-0 flex items-center justify-center">
          <Shield className="w-8 h-8 text-[#00d4aa]" />
        </div>
      </div>
      <div className="text-center">
        <p className="text-white font-semibold text-lg">Scanning target...</p>
        <p className="text-slate-400 text-sm mt-1">
          Running all scanners in parallel. This may take 20-30 seconds.
        </p>
      </div>
      <div className="flex flex-col gap-2 w-64">
        {["SSL/TLS Analysis", "HTTP Headers Audit", "Port Scanning", "WHOIS & DNS Lookup"].map((step, i) => (
          <div key={step} className="flex items-center gap-3">
            <div
              className="w-2 h-2 rounded-full bg-[#00d4aa] animate-pulse"
              style={{ animationDelay: `${i * 0.3}s` }}
            />
            <span className="text-slate-400 text-xs">{step}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Loader