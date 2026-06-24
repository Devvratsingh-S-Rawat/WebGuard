import { useState, useEffect } from "react"
import Navbar from "./components/Navbar"
import Hero from "./components/Hero"
import ScanForm from "./components/ScanForm"
import ScanResults from "./components/ScanResults"
import LiveProgress from "./components/LiveProgress"
import ScanHistory from "./components/ScanHistory"
import CompareScan from "./components/CompareScan"

const MAX_HISTORY = 10

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [scannedUrl, setScannedUrl] = useState("")
  const [progress, setProgress] = useState([])
  const [currentScanner, setCurrentScanner] = useState("")
  const [history, setHistory] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("webguard_history") || "[]")
    } catch {
      return []
    }
  })
  const [compareMode, setCompareMode] = useState(false)
  const [compareA, setCompareA] = useState(null)
  const [compareB, setCompareB] = useState(null)

  useEffect(() => {
    localStorage.setItem("webguard_history", JSON.stringify(history))
  }, [history])

  const saveToHistory = (data) => {
    const entry = {
      ...data,
      scanned_at: new Date().toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      }),
    }
    setHistory(prev => {
      const filtered = prev.filter(h => h.target !== entry.target)
      return [entry, ...filtered].slice(0, MAX_HISTORY)
    })
  }

  const handleReset = () => {
    setResults(null)
    setProgress([])
    setScannedUrl("")
    setError(null)
    setCompareMode(false)
    setCompareA(null)
    setCompareB(null)
  }

  const handleSelectHistory = (item) => {
    if (compareMode) {
      if (!compareA) {
        setCompareA(item)
      } else if (!compareB) {
        setCompareB(item)
      }
    } else {
      setResults(item)
      setScannedUrl(`https://${item.target}`)
    }
  }

  const handleScan = (url) => {
    setLoading(true)
    setError(null)
    setResults(null)
    setProgress([])
    setCurrentScanner("")
    setScannedUrl(url)
    setCompareMode(false)

    const wsUrl = import.meta.env.VITE_API_URL
      ? import.meta.env.VITE_API_URL.replace("https://", "wss://").replace("http://", "ws://")
      : "ws://localhost:5000"
    const ws = new WebSocket(`${wsUrl}/api/ws/scan`)

    ws.onopen = () => {
      ws.send(JSON.stringify({ url }))
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      if (data.type === "start") {
        setProgress([{ message: data.message, status: "info" }])
      }
      else if (data.type === "progress") {
        setCurrentScanner(data.scanner)
        setProgress(prev => [...prev, {
          message: data.message,
          status: "running",
          scanner: data.scanner
        }])
      }
      else if (data.type === "scanner_done") {
        setProgress(prev => prev.map(p =>
          p.scanner === data.scanner
            ? { ...p, status: "done", message: data.message }
            : p
        ))
      }
      else if (data.type === "complete") {
        setResults(data)
        saveToHistory(data)
        setLoading(false)
        setCurrentScanner("")
      }
      else if (data.type === "error") {
        setError(data.message)
        setLoading(false)
      }
    }

    ws.onerror = () => {
      setError("Connection failed. Make sure the backend is running.")
      setLoading(false)
    }

    ws.onclose = () => {
      if (loading) setLoading(false)
    }
  }

  const showCompare = compareMode && compareA && compareB
  const showHome = !results && !loading && !showCompare

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex flex-col">
      <Navbar />

      {/* HOME STATE */}
      {showHome && (
        <>
          <Hero />
          <div className="flex flex-col items-center w-full px-6 pb-20">
            <div className="w-full max-w-2xl">
              <ScanForm onScan={handleScan} loading={false} />
              {history.length > 0 && (
                <>
                  <ScanHistory
                    history={history}
                    onSelect={handleSelectHistory}
                    onClear={() => setHistory([])}
                    compareMode={compareMode}
                    compareA={compareA}
                    compareB={compareB}
                    onToggleCompare={() => {
                      setCompareMode(prev => !prev)
                      setCompareA(null)
                      setCompareB(null)
                    }}
                  />
                  {compareMode && (
                    <div className="mt-3 p-3 rounded-xl border border-[#00d4aa]/20 bg-[#00d4aa]/5 text-xs text-[#00d4aa] text-center">
                      {!compareA
                        ? "Select the first scan to compare"
                        : !compareB
                        ? `✓ ${compareA.target} selected — now select the second scan`
                        : "Both selected!"}
                    </div>
                  )}
                </>
              )}
            </div>
          </div>
        </>
      )}

      {/* LOADING STATE */}
      {loading && (
        <div className="flex flex-col items-center justify-center flex-1 px-6 pb-20">
          <div className="w-full max-w-2xl">
            <LiveProgress progress={progress} currentScanner={currentScanner} />
          </div>
        </div>
      )}

      {/* ERROR STATE */}
      {error && (
        <div className="flex flex-col items-center w-full px-6 pb-20">
          <div className="w-full max-w-2xl">
            <div className="mt-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-sm text-center">
              ⚠️ {error}
            </div>
            <div className="mt-4">
              <ScanForm onScan={handleScan} loading={false} />
            </div>
          </div>
        </div>
      )}

      {/* RESULTS STATE */}
      {results && !showCompare && (
        <div className="w-full max-w-4xl mx-auto px-6 pb-20">
          <ScanResults
            results={results}
            url={scannedUrl}
            onReset={handleReset}
          />
        </div>
      )}

      {/* COMPARE STATE */}
      {showCompare && (
        <div className="w-full max-w-4xl mx-auto px-6 pb-20">
          <CompareScan
            scanA={compareA}
            scanB={compareB}
            onClose={handleReset}
          />
        </div>
      )}

      <footer className="text-center py-6 border-t border-[#1e1e2e] mt-auto">
        <p className="text-xs text-slate-700">
          Generated by <span className="text-[#00d4aa]">WebGuard</span> — For authorized testing purposes only
        </p>
      </footer>
    </div>
  )
}

export default App