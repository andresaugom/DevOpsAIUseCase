# Online Boutique Cloud‑Agnostic Benchmarking Pipeline

## 1. Objective and Scope

### Objective

Design and implement a **cloud‑agnostic, automated benchmarking pipeline** to deploy the *Online Boutique* microservices application on Kubernetes clusters across different cloud providers, collect performance metrics (CPU and memory), and generate reproducible benchmark artifacts for processor comparison.

The system must be reusable, repeatable, and extensible for future runs and additional environments.

### Scope

* **Implemented**:

  * Infrastructure provisioning (one cloud for PoC)
  * Application deployment
  * Monitoring and dashboards
  * Automated benchmark execution and metric extraction
* **Designed only**:

  * AI agent architecture for operational intelligence

---

## 2. Design Principles

1. **Cloud‑agnostic at the Kubernetes layer**
   Portability is achieved by standardizing on Kubernetes, Helm, and Prometheus.

2. **Reproducibility over convenience**
   Every benchmark run must be repeatable with the same inputs and comparable outputs.

3. **Separation of concerns**
   Infrastructure, application deployment, monitoring, and orchestration are handled by distinct tools.

4. **Automation‑first**
   Manual steps are minimized; orchestration is scripted and parameterized.

---

## 3. Technology Stack

### Infrastructure Layer

* **Terraform**

  * Purpose: Provision cloud infrastructure
  * Manages:

    * Kubernetes cluster
    * Node pools (machine type, CPU vendor, core count)
    * Networking and IAM (minimal)

Terraform abstracts cloud provider APIs (GCP/AWS/Azure) behind a consistent declarative interface. The **cloud machine type** requested (e.g., `n2-standard-4`) is treated as the authoritative identifier for the underlying CPU generation, based on official cloud provider documentation.

Node pools are provisioned with **fixed machine types**, autoscaling disabled during benchmarks, and a single region/zone to ensure hardware consistency.

---

### Kubernetes & Application Layer

* **Kubernetes** (managed service per cloud)
* **Helm** (package manager for Kubernetes)

Helm is used to deploy:

* Online Boutique application
* Prometheus monitoring stack
* Load generation components

Helm enables versioning, configuration overrides, and repeatable installs.

---

### Monitoring & Observability

* **Prometheus** (kube‑prometheus‑stack)

  * Metrics collection:

    * Container CPU usage (usage, throttling)
    * Container memory usage (working set)
    * Pod restarts
    * Replica counts
    * Node‑level CPU and memory metrics
    * Request rate and latency (when available)

* **Grafana**

  * Live dashboards for benchmark visualization

Prometheus is self‑managed (Helm‑deployed), not cloud‑provider‑managed, to ensure portability and consistent metric semantics across providers.

---

### Load Generation

* **`loadgenerator`** (from **Online Boutique** microservices)

  * Another load generation options:
    
    * Locust (reliable and customizable)
    * K8

Load generation is mandatory to correlate performance metrics with traffic.

---

### Automation & Orchestration

* **Python** (primary automation language)

Python orchestrates:

1. Terraform execution
2. Helm deployments
3. Load test execution
4. Timed benchmark runs
5. Prometheus metric queries
6. Benchmark artifact generation

Python is chosen for:

* Strong JSON handling
* Prometheus querying support
* Readability and testability
* Reuse for AI agent implementation

---

### Benchmark Storage

* **JSON files** (primary)
* Optional CSV export

Each benchmark run produces an immutable artifact capturing:

* Environment metadata
* Load profile
* Aggregated performance metrics

No database is used, as benchmarks are batch‑oriented and append‑only.

---

## 4. High‑Level Architecture

```text
[ Terraform ]
      |
      v
[ Kubernetes Cluster ]
      |
      +-- Helm → Online Boutique
      +-- Helm → Prometheus + Grafana
      +-- Helm → Load Generator
      |
      v
[ Python Orchestrator ]
      |
      +-- Trigger load tests
      +-- Query Prometheus (PromQL)
      +-- Export benchmark JSON
      |
      v
[ Benchmark Artifacts ]
```

---

## 5. Benchmark Contract (Core Definition)

A **benchmark run** is defined as:

* Fixed cluster configuration (machine type, node count)
* Fixed Kubernetes resource requests and limits per service
* Fixed load profile
* Fixed execution duration
* Deterministic metric aggregation window

Hardware identity is defined by the **cloud machine type** used for the node pool. CPU vendor and generation are inferred from official cloud provider specifications and recorded as benchmark metadata.

### Metrics Collected (Minimum)

* Average CPU utilization per service
* P95 CPU utilization per service
* CPU throttling time per service
* Average memory working‑set usage per service
* Node‑level CPU utilization
* Request rate (RPS)
* Optional: P95 request latency

### Normalized Metrics (Derived)

* CPU seconds per request
* Memory usage per request

### Output Format (Example)

````json
{
  "run_id": "gke‑intel‑n2‑2026‑02‑01",
  "cloud": "gcp",
  "region": "us‑central1",
  "node_pool": {
    "machine_type": "n2‑standard‑8",
    "cpu_vendor": "intel",
    "cpu_generation": "per cloud provider specification",
    "source": "cloud‑provider‑docs"
  },
  "load_profile": "500rps‑10min",
  "metrics": {
    "avg_cpu_util_pct": 63.2,
    "p95_cpu_util_pct": 81.4,
    "cpu_throttled_seconds": 12.7,
    "avg_memory_mb": 1240,
    "cpu_seconds_per_request": 0.018
  }
}
````

> Note: `output.node_pool` can be extended if more information about machine specifications can be collected. This is minimum. The same for `output.metrics`. 

---

## 6. Automation Workflow

1. Provision Kubernetes cluster and fixed node pool with Terraform
2. Apply node labels based on machine type and provider metadata
3. Deploy Online Boutique via Helm with fixed resource requests/limits and node affinity
4. Deploy Prometheus & Grafana via Helm
5. Enable integrated Online Boutique loadgenerator
6. Execute load test for a fixed duration
7. Query Prometheus using predefined PromQL expressions
8. Aggregate raw metrics and compute normalized metrics
9. Export immutable benchmark artifact (JSON/CSV)
10. Visualize live metrics in Grafana

---

## 7. Required Artifacts (Deliverables)

* Running Online Boutique application
* Grafana dashboard with live metrics
* Benchmark JSON/CSV files
* Automation scripts (Python)
* Architecture diagram
* AI agent architecture design document

---

## 8. AI Agent Architecture (Design Only)

### Purpose

Provide operational intelligence on top of collected metrics.

### Use Cases

* Metrics analysis and anomaly detection
* Deployment status and troubleshooting queries
* Automated optimization recommendations

### Proposed Stack

* **Language**: Python
* **LLM Provider**: OpenAI / Azure OpenAI (pluggable)
* **Frameworks**:

  * LangChain or similar orchestration layer
  * Prometheus HTTP API client

### Architecture Overview

```text
[ User (CLI / API) ]
        |
        v
[ AI Agent Service ]
        |
        +-- Prometheus API
        +-- Benchmark JSON store
        +-- Kubernetes API (read‑only)
```

### Data Access

* Real‑time metrics via Prometheus queries
* Historical benchmarks via JSON artifacts

### Interface

* CLI (initial)
* REST API (extensible)

### Non‑Functional Considerations

* Read‑only access to cluster
* Rate‑limited LLM calls
* Stateless agent service
* Cost‑aware query summarization

---

## 9. Success Criteria

* Pipeline runs end‑to‑end with a single command
* Metrics are reproducible across runs
* Benchmarks are portable across cloud providers
* Architecture clearly supports future AI agent integration

