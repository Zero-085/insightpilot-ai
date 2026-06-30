# Google Agent Development Kit (ADK) Integration

This folder integrates the **Google Agent Development Kit (ADK)** into the InsightPilot AI multi-agent architecture as a demonstration of a structured, code-first multi-agent orchestration.

## Why Google ADK is Used
- **Session-Based State Management**: Using ADK's `InMemorySessionService` and `Context.state` allows agents to store, update, and fetch shared execution states dynamically and safely.
- **Structured Orchestration**: Replaces manual procedural orchestration with an ADK `Workflow` Graph defining edges between agent nodes.
- **Traceability and Logging**: Automatically records start, completion, execution duration, and full failure tracebacks for all agent tasks.
- **Resilience and Error Isolation**: Exception handling inside nodes allows the pipeline to isolate failures, log tracebacks, and preserve outputs from successful upstream agents instead of causing a cascade crash.

## Agent Responsibilities
1. **CleanerAgent**: Accepts a raw CSV, performs duplicate removal, detects missing value structures, infers column datatypes, and saves a cleaned dataset copy.
2. **AnalyzerAgent**: Reads the clean dataset, runs statistical computations (null distributions, descriptive metrics, correlations), and aggregates findings.
3. **VisualizerAgent**: Examines column metadata and distributions to automatically generate Plotly histogram, bar, trend line, and pie chart configs.
4. **InsightAgent**: Sends summarized analytical results and cleaning details to Gemini, returning structured findings and recommendations.

## Orchestration Flow
The pipeline is modeled as a sequential DAG workflow:
```
  [START]
     ↓
[CleanerAgent]   ---> Saves clean dataset, records datatype metadata
     ↓
[AnalyzerAgent]  ---> Computes metrics, correlation matrices
     ↓
[VisualizerAgent]---> Creates Plotly configurations
     ↓
[InsightAgent]   ---> Generates Gemini structured summaries and recommendations
     ↓
[Combined Result]
```
The [ADKCoordinator](file:///c:/Users/HIMANSHU%20MISHRA/Desktop/InsightPilot-AI/backend/adk/coordinator.py) manages this workflow, wrapping each agent as an ADK compatible node block.
