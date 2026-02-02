# AI Agent Architecture Document

## Executive Summary

This document describes the architecture for an AI-powered operational intelligence agent designed to assist with the Online Boutique benchmarking pipeline. The agent provides metrics analysis, deployment assistance, and automated recommendations to enhance operational efficiency and decision-making.

## Table of Contents

1. [Overview](#overview)
2. [Use Cases](#use-cases)
3. [Technology Stack](#technology-stack)
4. [System Architecture](#system-architecture)
5. [Data Flow](#data-flow)
6. [Integration Points](#integration-points)
7. [User Interface](#user-interface)
8. [Security Considerations](#security-considerations)
9. [Scalability & Performance](#scalability--performance)
10. [Cost Management](#cost-management)
11. [Implementation Roadmap](#implementation-roadmap)
12. [Code Examples](#code-examples)

---

## Overview

The AI Agent is designed to provide operational intelligence on top of the benchmarking infrastructure by leveraging Large Language Models (LLMs) to:
- Analyze collected metrics and detect anomalies
- Answer questions about deployment status and configuration
- Provide optimization recommendations based on observed patterns

The agent acts as a read-only observer and advisor, never making direct changes to infrastructure.

---

## Use Cases

### 1. Metrics Analysis Agent

**Capabilities:**
- Analyze time-series metrics from Prometheus
- Detect anomalies and performance degradations
- Correlate events across services
- Generate natural language insights

**Example Queries:**
- "What caused the CPU spike at 2pm yesterday?"
- "Are there any performance anomalies in the last benchmark run?"
- "Compare memory usage between the checkout and cart services"
- "Show me services that were CPU-throttled during the benchmark"

### 2. Deployment Assistant

**Capabilities:**
- Query deployment status and configuration
- Provide troubleshooting guidance
- Explain service dependencies
- Answer "how-to" questions

**Example Queries:**
- "Which services are consuming the most memory?"
- "How do I scale the frontend service?"
- "What's the current status of the checkout service?"
- "Why is my pod in CrashLoopBackOff?"
- "Show me the resource limits for all services"

### 3. Automated Recommendations

**Capabilities:**
- Analyze resource utilization patterns
- Suggest resource optimization opportunities
- Identify cost-saving measures
- Recommend scaling strategies

**Example Outputs:**
- "The cart service is consistently using 30% of its CPU limit. Consider reducing the request from 200m to 100m."
- "Services are being CPU-throttled 15% of the time. Increase CPU limits or reduce load."
- "Node utilization is at 40%. Consider using smaller machine types for cost optimization."

---

## Technology Stack

### Programming Language
**Python 3.11+**
- Chosen for consistency with the automation pipeline
- Rich ecosystem for AI/ML and API integration
- Strong async support for concurrent operations

### LLM Provider
**OpenAI GPT-4 / Azure OpenAI Service** (Primary)
- Proven reliability and performance
- Strong reasoning capabilities for technical analysis
- Function calling for structured data retrieval

**Alternatives:**
- Anthropic Claude (strong at analysis)
- Google Gemini (good Kubernetes knowledge)
- Self-hosted Llama 3 (cost-effective, privacy-focused)

### Frameworks & Libraries

#### LLM Orchestration
**LangChain** (Primary framework)
- Agent framework for tool use
- Memory management for conversation context
- Pre-built integrations with data sources

#### Data Access
- **Prometheus HTTP API Client** (`prometheus-api-client`)
- **Kubernetes Python Client** (`kubernetes`)
- **pandas** (data manipulation and analysis)
- **numpy** (numerical computations)

#### API Framework
**FastAPI**
- Modern async Python web framework
- Automatic OpenAPI documentation
- WebSocket support for streaming responses

#### CLI
**Click** or **Typer**
- User-friendly command-line interface
- Auto-completion support

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface Layer                     │
│  ┌──────────┐  ┌──────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   CLI    │  │ REST API │  │  Web UI     │  │  Slack Bot  │ │
│  │  (Typer) │  │(FastAPI) │  │  (React)    │  │  (Bolt)     │ │
│  └──────────┘  └──────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AI Agent Service                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              LLM Orchestration (LangChain)              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Query Parser │  │ Tool Selector│  │Response Gen. │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Agent Tools                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Prometheus   │  │  Kubernetes  │  │  Benchmark   │  │   │
│  │  │   Tool       │  │    Tool      │  │   Archive    │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Context & Memory Management                 │   │
│  │  - Conversation history                                  │   │
│  │  - Recent metrics cache                                  │   │
│  │  - System state snapshot                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Prometheus  │  │  Kubernetes  │  │  Benchmark   │          │
│  │  (Metrics)   │  │  API Server  │  │  JSON Files  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

#### User Interface Layer
Multiple interfaces for different use cases:
- **CLI**: Quick queries for operators
- **REST API**: Programmatic access for automation
- **Web UI**: Rich visualization and exploration
- **Slack Bot**: Collaborative operational insights

#### AI Agent Service
The core service orchestrating all operations:
- **Query Parser**: Understands user intent
- **Tool Selector**: Chooses appropriate data sources
- **Response Generator**: Formats insights for users

#### Agent Tools
Specialized components for data access:
- **Prometheus Tool**: Query time-series metrics
- **Kubernetes Tool**: Inspect cluster state
- **Benchmark Archive Tool**: Access historical benchmarks

#### Context Management
Maintains state across interactions:
- Conversation history for follow-up questions
- Cached metrics to reduce API calls
- System state for context-aware responses

---

## Data Flow

### Example: Metrics Analysis Query

```
1. User Query: "Why did CPU spike at 2pm?"
   ↓
2. CLI/API receives query → Agent Service
   ↓
3. LLM parses intent:
   - Needs: CPU metrics around 2pm
   - Needs: Correlation with other events
   ↓
4. Agent selects tools:
   - Prometheus Tool (CPU metrics)
   - Kubernetes Tool (pod events)
   ↓
5. Tools execute in parallel:
   - Query CPU metrics for 2pm ±30min
   - Query pod events for 2pm ±30min
   ↓
6. LLM analyzes results:
   - Correlates CPU spike with checkout service restarts
   - Identifies OOMKilled events
   ↓
7. Response generated:
   "CPU spiked at 2:03pm when checkout service was OOMKilled
    and restarted. Memory usage exceeded 128Mi limit. Consider
    increasing memory limit to 256Mi."
   ↓
8. Response delivered to user
```

---

## Integration Points

### 1. Prometheus Integration

**Access Method:**
- HTTP API via port-forward or ingress
- Read-only service account

**Data Retrieved:**
- Time-series metrics (PromQL queries)
- Alert states
- Target health

**Example Tool Function:**
```python
def query_prometheus_range(query: str, start: datetime, end: datetime, step: str = "15s"):
    """Query Prometheus for time-series data"""
    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        "query": query,
        "start": start.timestamp(),
        "end": end.timestamp(),
        "step": step
    }
    response = requests.get(url, params=params)
    return response.json()
```

### 2. Kubernetes Integration

**Access Method:**
- Kubernetes Python client
- Read-only RBAC role

**Data Retrieved:**
- Pod status and events
- Resource usage (via metrics-server)
- Service configuration
- Deployment specs

**Example Tool Function:**
```python
def get_pod_status(namespace: str = "default"):
    """Get status of all pods in namespace"""
    v1 = client.CoreV1Api()
    pods = v1.list_namespaced_pod(namespace)
    return [
        {
            "name": pod.metadata.name,
            "status": pod.status.phase,
            "restarts": sum(c.restart_count for c in pod.status.container_statuses or [])
        }
        for pod in pods.items
    ]
```

### 3. Benchmark Archive Integration

**Access Method:**
- Direct file system access
- JSON parsing

**Data Retrieved:**
- Historical benchmark results
- Metadata (machine type, CPU vendor)
- Performance metrics

**Example Tool Function:**
```python
def get_benchmark_history(days: int = 30):
    """Retrieve benchmark results from last N days"""
    benchmark_dir = Path("benchmarks")
    cutoff = datetime.now() - timedelta(days=days)
    
    results = []
    for file in benchmark_dir.glob("*.json"):
        with open(file) as f:
            data = json.load(f)
            if datetime.fromisoformat(data["timestamp"]) > cutoff:
                results.append(data)
    
    return sorted(results, key=lambda x: x["timestamp"], reverse=True)
```

---

## User Interface

### 1. Command-Line Interface (CLI)

**Primary interface for quick queries and automation**

```bash
# Interactive mode
$ benchmark-agent chat
Agent: How can I help you analyze your benchmarks?
You: What was the CPU usage in the last benchmark?
Agent: The last benchmark (run gcp-intel-20260201-143022) showed...

# Single query mode
$ benchmark-agent query "Compare memory usage between Intel and AMD runs"

# Specific analysis
$ benchmark-agent analyze-anomalies --last 7d

# Generate report
$ benchmark-agent report --run-id gcp-intel-20260201-143022 --format markdown
```

### 2. REST API

**Programmatic access for integration**

```http
POST /api/v1/query
Content-Type: application/json

{
  "query": "What caused the performance degradation?",
  "context": {
    "run_id": "gcp-intel-20260201-143022",
    "time_range": "2024-02-01T14:00:00Z/2024-02-01T15:00:00Z"
  }
}

Response:
{
  "response": "Performance degradation was caused by...",
  "confidence": 0.85,
  "sources": [
    {"type": "prometheus", "query": "..."},
    {"type": "kubernetes", "resource": "..."}
  ],
  "recommendations": [...]
}
```

### 3. Web UI (Future)

**Rich interface for exploration and visualization**

- Dashboard with key metrics
- Interactive chat interface
- Metric visualization with annotations
- Benchmark comparison tool
- Recommendation panel

---

## Security Considerations

### 1. Access Control

**Agent Permissions:**
- **Read-only** access to all data sources
- Cannot modify cluster state
- Cannot execute commands on nodes
- Cannot delete or modify benchmarks

**RBAC Configuration:**
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: benchmark-agent-reader
rules:
- apiGroups: [""]
  resources: ["pods", "services", "events"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments", "replicasets"]
  verbs: ["get", "list"]
```

### 2. Data Privacy

**Sensitive Data Handling:**
- No PII in metrics or logs
- Cluster credentials stored in secure vault
- LLM API keys in environment variables
- Audit logging for all agent queries

### 3. LLM Security

**Prompt Injection Protection:**
- Input sanitization
- Query validation
- System prompts with strict boundaries
- Output filtering

**Example System Prompt:**
```
You are a read-only assistant for Kubernetes benchmarking.
You can only retrieve and analyze data, never modify it.
If asked to make changes, politely decline and explain you are read-only.
```

### 4. Network Security

- Agent runs in isolated namespace
- Network policies restrict egress
- TLS for all external communication
- No direct internet access except LLM API

---

## Scalability & Performance

### 1. Response Time Targets

- Simple queries: < 5 seconds
- Complex analysis: < 30 seconds
- Report generation: < 2 minutes

### 2. Caching Strategy

**Metric Cache:**
- 5-minute TTL for recent metrics
- Reduces Prometheus load
- Invalidate on cluster changes

**LLM Response Cache:**
- Cache identical queries for 1 hour
- Semantic similarity matching
- Significant cost savings

### 3. Rate Limiting

**LLM API Calls:**
- Max 100 requests/hour (adjustable)
- Queue requests during high load
- Provide estimated wait time

**Prometheus Queries:**
- Batch queries when possible
- Use recording rules for common patterns
- Limit query time range

### 4. Horizontal Scaling

- Stateless agent service
- Load balancer for multiple replicas
- Shared cache (Redis) for coordination

---

## Cost Management

### 1. LLM Cost Optimization

**Strategies:**
- Use GPT-3.5 for simple queries, GPT-4 for complex analysis
- Implement aggressive caching
- Compress context windows
- Use function calling instead of long prompts

**Estimated Costs (OpenAI pricing):**
- Simple query: $0.002 - $0.01
- Complex analysis: $0.02 - $0.10
- Daily usage (50 queries): $0.50 - $5.00

### 2. Infrastructure Costs

**Agent Service:**
- 1 replica: 0.5 CPU, 1GB RAM (~$10/month)
- 3 replicas (HA): ~$30/month

**Total Estimated Cost:**
- Development: $50-100/month
- Production: $100-300/month

### 3. Cost Monitoring

- Track tokens used per query
- Alert on unusual usage patterns
- Daily cost reports
- Budget limits with graceful degradation

---

## Implementation Roadmap

### Phase 1: MVP (4-6 weeks)
- ✓ CLI interface
- ✓ Prometheus integration
- ✓ Basic metrics analysis
- ✓ Benchmark archive access

### Phase 2: Enhanced Analysis (4-6 weeks)
- ✓ Kubernetes integration
- ✓ Anomaly detection
- ✓ Correlation analysis
- ✓ REST API

### Phase 3: Advanced Features (6-8 weeks)
- ✓ Automated recommendations
- ✓ Web UI
- ✓ Slack integration
- ✓ Custom dashboards

### Phase 4: Production Hardening (4 weeks)
- ✓ HA deployment
- ✓ Comprehensive testing
- ✓ Security audit
- ✓ Performance optimization

---

## Code Examples

### Example 1: Agent Service Core

```python
from langchain.agents import initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.tools import Tool

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0)

# Define tools
tools = [
    Tool(
        name="QueryPrometheus",
        func=prometheus_tool.query,
        description="Query Prometheus for metrics. Input: PromQL query string"
    ),
    Tool(
        name="GetPodStatus",
        func=k8s_tool.get_pods,
        description="Get Kubernetes pod status. Input: namespace name"
    ),
    Tool(
        name="GetBenchmarkHistory",
        func=benchmark_tool.get_history,
        description="Get historical benchmark results. Input: number of days"
    ),
]

# Initialize agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    max_iterations=5
)

# Process query
def process_query(user_query: str) -> str:
    """Process user query and return response"""
    system_prompt = """
    You are an expert Kubernetes and benchmarking assistant.
    You help analyze performance metrics and provide insights.
    You have read-only access to metrics and cluster state.
    """
    
    response = agent.run(f"{system_prompt}\n\nUser query: {user_query}")
    return response
```

### Example 2: Prometheus Tool

```python
class PrometheusTool:
    """Tool for querying Prometheus metrics"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def query(self, promql: str, time_range: Optional[dict] = None) -> dict:
        """
        Execute PromQL query
        
        Args:
            promql: Prometheus query string
            time_range: Optional dict with 'start', 'end', 'step'
        
        Returns:
            Processed query results
        """
        if time_range:
            endpoint = f"{self.base_url}/api/v1/query_range"
            params = {
                "query": promql,
                "start": time_range["start"],
                "end": time_range["end"],
                "step": time_range.get("step", "15s")
            }
        else:
            endpoint = f"{self.base_url}/api/v1/query"
            params = {"query": promql}
        
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data["status"] != "success":
            raise ValueError(f"Query failed: {data.get('error')}")
        
        return self._process_results(data["data"]["result"])
    
    def _process_results(self, results: list) -> dict:
        """Process and summarize Prometheus results"""
        if not results:
            return {"values": [], "summary": "No data found"}
        
        # Extract values and calculate statistics
        all_values = []
        for series in results:
            values = series.get("values", [[0, series.get("value", [0, 0])[1]]])
            all_values.extend([float(v[1]) for v in values])
        
        return {
            "count": len(all_values),
            "min": min(all_values) if all_values else 0,
            "max": max(all_values) if all_values else 0,
            "avg": sum(all_values) / len(all_values) if all_values else 0,
            "values": all_values[:100],  # Limit to first 100 for context
        }
```

### Example 3: CLI Implementation

```python
import typer
from rich.console import Console
from rich.markdown import Markdown

app = typer.Typer()
console = Console()

@app.command()
def query(
    question: str = typer.Argument(..., help="Your question"),
    run_id: Optional[str] = typer.Option(None, help="Specific benchmark run ID"),
    format: str = typer.Option("text", help="Output format: text, json, markdown")
):
    """Ask the AI agent a question about your benchmarks"""
    
    console.print(f"[blue]Analyzing...[/blue]")
    
    # Build context
    context = {"run_id": run_id} if run_id else {}
    
    # Query agent
    response = agent_service.process_query(question, context)
    
    # Format output
    if format == "markdown":
        console.print(Markdown(response))
    elif format == "json":
        console.print_json(response)
    else:
        console.print(response)

@app.command()
def chat():
    """Start an interactive chat session"""
    console.print("[green]Benchmark AI Agent - Interactive Mode[/green]")
    console.print("Type 'exit' to quit\n")
    
    while True:
        question = typer.prompt("You")
        
        if question.lower() in ["exit", "quit"]:
            break
        
        response = agent_service.process_query(question, {})
        console.print(f"[blue]Agent:[/blue] {response}\n")

if __name__ == "__main__":
    app()
```

### Example 4: Anomaly Detection

```python
def detect_anomalies(metrics: dict, historical_data: list) -> list:
    """
    Detect anomalies in current metrics compared to historical baselines
    
    Args:
        metrics: Current benchmark metrics
        historical_data: List of historical benchmark results
    
    Returns:
        List of detected anomalies with severity and description
    """
    anomalies = []
    
    if not historical_data:
        return anomalies
    
    # Calculate baselines
    cpu_values = [h["metrics"]["avg_cpu_util_pct"] for h in historical_data]
    mem_values = [h["metrics"]["avg_memory_mb"] for h in historical_data]
    
    cpu_mean = statistics.mean(cpu_values)
    cpu_std = statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0
    
    mem_mean = statistics.mean(mem_values)
    mem_std = statistics.stdev(mem_values) if len(mem_values) > 1 else 0
    
    # Check for anomalies (>2 standard deviations)
    current_cpu = metrics["avg_cpu_util_pct"]
    if cpu_std > 0 and abs(current_cpu - cpu_mean) > 2 * cpu_std:
        anomalies.append({
            "type": "cpu",
            "severity": "high" if abs(current_cpu - cpu_mean) > 3 * cpu_std else "medium",
            "description": f"CPU usage ({current_cpu:.1f}%) is significantly different from baseline ({cpu_mean:.1f}% ± {cpu_std:.1f}%)",
            "recommendation": "Investigate workload changes or system issues"
        })
    
    current_mem = metrics["avg_memory_mb"]
    if mem_std > 0 and abs(current_mem - mem_mean) > 2 * mem_std:
        anomalies.append({
            "type": "memory",
            "severity": "high" if abs(current_mem - mem_mean) > 3 * mem_std else "medium",
            "description": f"Memory usage ({current_mem:.0f}MB) is significantly different from baseline ({mem_mean:.0f}MB ± {mem_std:.0f}MB)",
            "recommendation": "Check for memory leaks or configuration changes"
        })
    
    return anomalies
```

---

## Conclusion

This AI agent architecture provides a solid foundation for operational intelligence in the benchmarking pipeline. The design prioritizes:

- **Safety**: Read-only access prevents unintended changes
- **Flexibility**: Multiple interfaces for different use cases
- **Scalability**: Stateless design supports horizontal scaling
- **Cost-effectiveness**: Caching and rate limiting control expenses
- **Extensibility**: Tool-based architecture enables easy feature additions

The phased implementation approach allows for iterative development and validation, ensuring each component delivers value before moving to the next phase.

---

## References

- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/)
- [Prometheus API](https://prometheus.io/docs/prometheus/latest/querying/api/)
- [Kubernetes Python Client](https://github.com/kubernetes-client/python)
- [FastAPI](https://fastapi.tiangolo.com/)
