# 🛡️ WebGuard — Website Vulnerability Scanner

A full-stack black-box security scanner that analyzes websites for vulnerabilities in real time.

🔗 **Live Demo:** [web-guard-flame.vercel.app](https://web-guard-flame.vercel.app)

---

## ✨ Features

- 🔍 **8 Security Scanners** running in parallel
  - SSL/TLS Analysis
  - HTTP Headers Audit
  - Port Scanning
  - WHOIS & DNS Lookup
  - SQL Injection Detection
  - XSS Detection
  - CMS Detection
  - Broken Links Scanner
- 📊 **Risk Score** (0–100, Grade A–F)
- ⚡ **Live Progress Terminal** via WebSockets
- 📄 **PDF Report Generation** with ReportLab
- 🕓 **Scan History** (last 10 scans, localStorage)
- 🔄 **Compare Two Scans** side by side
- 📈 **Recharts Donut Chart** for vulnerability breakdown

---

## 🛠️ Tech Stack

**Frontend**
- React + Vite
- Tailwind CSS
- Recharts
- WebSocket API

**Backend**
- FastAPI (Python)
- Uvicorn
- ThreadPoolExecutor (parallel scanning)
- ReportLab (PDF generation)
- WebSockets

**Deployment**
- Frontend → Vercel
- Backend → Render

---

## 🚀 Run Locally

**Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 5000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173`
Backend runs on `http://localhost:5000`

---

## 📁 Project Structure
WebGuard/

├── backend/

│   ├── main.py

│   ├── models.py

│   ├── requirements.txt

│   ├── routers/

│   │   └── scan.py

│   ├── scanners/

│   │   ├── ssl_scanner.py

│   │   ├── headers_scanner.py

│   │   ├── port_scanner.py

│   │   ├── whois_scanner.py

│   │   ├── sqli_scanner.py

│   │   ├── xss_scanner.py

│   │   ├── cms_scanner.py

│   │   └── broken_links_scanner.py

│   └── utils/

│       └── pdf_generator.py

└── frontend/

├── src/

│   ├── App.jsx

│   ├── components/

│   │   ├── ScanForm.jsx

│   │   ├── ScanResults.jsx

│   │   ├── LiveProgress.jsx

│   │   ├── RiskScore.jsx

│   │   ├── SummaryChart.jsx

│   │   ├── ScanHistory.jsx

│   │   └── CompareScan.jsx

│   └── main.jsx

└── index.html

---

## ⚠️ Disclaimer

WebGuard is built for **educational purposes** and **authorized security testing only**.
Do not scan websites without permission.

---

**Built by [Devvratsingh S. Rawat](https://github.com/Devvratsingh-S-Rawat)**
