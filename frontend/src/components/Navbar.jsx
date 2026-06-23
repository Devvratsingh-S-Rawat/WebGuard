import { ShieldCheck } from "lucide-react"

function Navbar() {
  return (
    <nav className="flex items-center justify-between px-8 py-4 border-b border-[#1e1e2e]">
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-lg bg-[#00d4aa]/10 border border-[#00d4aa]/20 flex items-center justify-center">
          <ShieldCheck className="w-4 h-4 text-[#00d4aa]" />
        </div>
        <span className="text-white font-medium text-base tracking-tight">
          Web<span className="text-[#00d4aa]">Guard</span>
        </span>
      </div>
      <div className="flex items-center gap-6">
        <span className="text-sm text-slate-500 cursor-pointer hover:text-slate-300 transition-colors">Docs</span>
        <span className="text-sm text-slate-500 cursor-pointer hover:text-slate-300 transition-colors">About</span>
        <span className="text-xs px-3 py-1.5 rounded-full border border-[#00d4aa]/20 text-[#00d4aa] bg-[#00d4aa]/5 flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00d4aa] animate-pulse inline-block" />
          v1.0 Live
        </span>
      </div>
    </nav>
  )
}

export default Navbar