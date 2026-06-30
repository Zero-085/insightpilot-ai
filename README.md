# InsightPilot AI

InsightPilot AI is a modular AI-powered Business Intelligence web application that converts uploaded CSV datasets into actionable business insights using a multi-agent architecture.

## Architecture

This project is organized as a modular application split into a FastAPI backend and a responsive frontend:

- **Backend**: Python-based FastAPI web server containing:
  - **Agents**: Distinct multi-agent framework subdirectories (`coordinator`, `cleaner`, `analyzer`, `visualizer`, `insight`).
  - **Models**: Database and application models.
  - **API**: Router pathways for endpoints.
  - **MCP**: Model Context Protocol configurations.
  - **Security**: Security and authentication layers.
  - **Skills**: Actions and tasks executed by agents.
  - **Utils**: Helper modules.
- **Frontend**: Clean and responsive HTML/CSS/JS dashboard layout presenting data analytics, CSV previews, metrics, visualizations, and generated text.

## Running the Application

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Setup
Clone the repository, initialize your virtual environment, and install dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Server
Start the backend server using Uvicorn:

```bash
uvicorn backend.main:app --reload
```

The application will start, by default, on `http://127.0.0.1:8000`. You can inspect the health endpoint at `http://127.0.0.1:8000/health`.
