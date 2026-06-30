# 🚀 InsightPilot AI

**An AI-Powered Business Intelligence Dashboard built with FastAPI, Google Gemini, Google ADK, MCP, and Plotly.**

InsightPilot AI transforms raw CSV datasets into actionable business intelligence through an intelligent multi-agent pipeline. Users can upload datasets, automatically clean and analyze data, generate interactive visualizations, and receive AI-powered business insights.

---

# 📌 Features

- 📂 Upload CSV datasets
- 🧹 Automatic data cleaning
- 📊 Statistical analysis
- 📈 Interactive Plotly visualizations
- 🤖 AI-generated business insights using Google Gemini
- 🧠 Multi-Agent architecture
- ⚙️ Google Agent Development Kit (ADK) integration
- 🔌 Model Context Protocol (MCP) server
- 📑 Dataset preview
- 📉 Correlation analysis
- 📋 Automatic data quality reports

---

# 🏗 Architecture

```
                    CSV Upload
                         │
                         ▼
                Coordinator Agent
                         │
 ┌─────────────┬──────────────┬──────────────┬──────────────┐
 ▼             ▼              ▼              ▼
Cleaner     Analyzer     Visualizer     Insight Agent
 Agent        Agent         Agent        (Gemini API)
 │             │              │              │
 └─────────────┴──────────────┴──────────────┘
                         │
                         ▼
            Business Intelligence Dashboard
```

---

# 🧠 Multi-Agent Workflow

### Cleaner Agent
- Detects missing values
- Removes duplicate rows
- Infers column data types

### Analyzer Agent
- Calculates descriptive statistics
- Correlation matrix
- Categorical summaries
- Dataset preview

### Visualizer Agent
Automatically generates:

- Histogram
- Bar Chart
- Pie Chart
- Line Chart

using Plotly.

### Insight Agent

Uses **Google Gemini 2.5 Flash** to generate:

- Executive Summary
- Key Business Findings
- Actionable Recommendations

---

# 🔌 MCP Integration

InsightPilot AI includes a standalone MCP server exposing dataset tools.

Available MCP Tools:

- list_datasets
- get_dataset_metadata
- get_dataset_schema
- get_dataset_preview

---

# 🤖 Google ADK Integration

The project demonstrates orchestration using Google Agent Development Kit.

Workflow:

```
START
   │
Cleaner
   │
Analyzer
   │
Visualizer
   │
Insight Agent
   │
 END
```

---

# 🛠 Tech Stack

## Backend

- FastAPI
- Python
- Pandas
- Plotly
- Google Gemini API
- Google ADK
- MCP

## Frontend

- HTML
- CSS
- JavaScript

---

# 📁 Project Structure

```
InsightPilot-AI
│
├── backend
│   ├── agents
│   ├── api
│   ├── adk
│   ├── mcp
│   ├── services
│   └── utils
│
├── frontend
│
├── run_adk_demo.py
├── run_mcp_demo.py
├── requirements.txt
└── README.md
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/Zero-085/insightpilot-ai.git
```

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-2.5-flash
```

Run the application

```bash
uvicorn backend.main:app --reload
```

Open

```
http://127.0.0.1:8000
```

---

# ▶ Running ADK Demo

```bash
python run_adk_demo.py
```

---

# ▶ Running MCP Demo

```bash
python run_mcp_demo.py
```

---

# 📊 Sample Dashboard

(Add screenshots here)

- Dashboard
- Charts
- AI Insights
- Upload page

---

# 🎯 Future Improvements

- PDF report generation
- Authentication
- Database integration
- Multi-file analysis
- Real-time dashboards
- Cloud deployment
- RAG-enabled document analysis

---

# 👨‍💻 Author

**Himanshu Mishra**

B.Tech (AI & ML)

Aspiring Data Analyst

GitHub: https://github.com/Zero-085