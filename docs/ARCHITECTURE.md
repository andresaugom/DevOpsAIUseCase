# System Architecture Documentation

> **Last Updated:** February 2026 | **Version:** 2.0 (Enhanced Metrics)

## Overview

This document describes the architecture of the **Cloud-Agnostic Performance Benchmarking Platform**, a fully Dockerized system that automates infrastructure provisioning, application deployment, and performance analysis for processor comparison across cloud providers.

**Key Features:**
- 🐳 **Fully containerized** with pinned tool versions
- 📊 **Enhanced metrics v2.0** with per-pod and per-node granularity
- 🔄 **One-command execution** via Docker wrapper (`benchmark.sh`)
- 🌐 **Cloud-agnostic** design (GCP production-ready, AWS/Azure templated)
- 📈 **4-file artifact output** for comprehensive analysis

---

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE LAYER                                │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              Docker Container (benchmark.sh wrapper)                │    │
│  │  All dependencies included: Terraform, Helm, kubectl, gcloud, etc.  │    │
│  │  Pinned versions: TF 1.7.5, Helm 3.14.0, kubectl 1.29.2            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    ▼                                         │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                      Python Orchestrator (main.py)                  │    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐          │    │
│  │  │  Terraform   │  │     Helm     │  │   Prometheus   │          │    │
│  │  │   Executor   │  │   Deployer   │  │     Client     │          │    │
│  │  └──────────────┘  └──────────────┘  └────────────────┘          │    │
│  │                                                                     │    │
│  │  ┌──────────────┐  ┌──────────────────────────────────┐          │    │
│  │  │  Benchmark   │  │      Artifact Generator          │          │    │
│  │  │   Runner     │  │   (4-file output: JSON + 3 CSVs) │          │    │
│  │  └──────────────┘  └──────────────────────────────────┘          │    │
│  │                                                                     │    │
│  │  ┌──────────────────────────────────────────────────────┐         │    │
│  │  │      Machine Specs (GCP metadata enrichment)          │         │    │
│  │  │  CPU vendor, generation, vCPUs, memory, bandwidth     │         │    │
│  │  └──────────────────────────────────────────────────────┘         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└───────────────┬────────────────────────────────────────────┬────────────────┘
                │                                            │
                ▼                                            ▼
┌───────────────────────────────────┐    ┌──────────────────────────────────┐
│    INFRASTRUCTURE LAYER           │    │     BENCHMARK ARTIFACTS (v2.0)   │
│                                   │    │                                  │
│  ┌─────────────────────────────┐ │    │  ┌────────────────────────────┐ │
│  │   Terraform (IaC)           │ │    │  │  <cloud>-<vendor>-<ts>.json│ │
│  │                             │ │    │  │  - Complete metrics        │ │
│  │  ┌──────┐  ┌──────┐        │ │    │  │  - Machine specs           │ │
│  │  │ GCP  │  │ AWS  │ ...    │ │    │  │  - Per-pod data            │ │
│  │  │ ✅    │  │  📋  │        │ │    │  │  - Per-node data           │ │
│  │  └──────┘  └──────┘        │ │    │  └────────────────────────────┘ │
│  │                             │ │    │                                  │
│  │  Creates:                   │ │    │  ┌────────────────────────────┐ │
│  │  - Kubernetes clusters      │ │    │  │  cluster_summary.csv       │ │
│  │  - Fixed node pools         │ │    │  │  <run-id>_nodes.csv        │ │
│  │  - Node labels (CPU info)   │ │    │  │  <run-id>_pods.csv         │ │
│  │  - Auto-generated .tfvars   │ │    │  └────────────────────────────┘ │
│  └─────────────────────────────┘ │    │                                  │
└───────────────┬───────────────────┘    └──────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                        KUBERNETES CLUSTER LAYER                             │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Application Workloads                         │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │              Online Boutique (Helm Chart)                     │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │  │
│  │  │  │ Frontend │  │   Cart   │  │ Checkout │  │  Payment   │  │  │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐  │  │  │
│  │  │  │Recommend │  │  Product │  │ Currency │  │  Shipping  │  │  │  │
│  │  │  └──────────┘  └──────────┘  └──────────┘  └────────────┘  │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │  │  │
│  │  │  │  Email   │  │    Ad    │  │   Load Generator         │  │  │  │
│  │  │  └──────────┘  └──────────┘  └──────────────────────────┘  │  │  │
│  │  │                                                               │  │  │
│  │  │  Resource Limits: Fixed for reproducibility                  │  │  │
│  │  │  Node Affinity: workload=benchmark                           │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                     Monitoring & Observability                       │  │
│  │                                                                      │  │
│  │  ┌──────────────────────────────────────────────────────────────┐  │  │
│  │  │              kube-prometheus-stack (Helm Chart)              │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌────────────────┐            ┌─────────────────┐          │  │  │
│  │  │  │  Prometheus    │            │    Grafana      │          │  │  │
│  │  │  │                │            │                 │          │  │  │
│  │  │  │  - Scrapes     │◄───────────┤  - Dashboards   │          │  │  │
│  │  │  │    metrics     │            │  - Alerts       │          │  │  │
│  │  │  │  - Stores      │            │  - Queries      │          │  │  │
│  │  │  │    time-series │            │                 │          │  │  │
│  │  │  │  - PromQL API  │            │  LoadBalancer   │          │  │  │
│  │  │  │                │            │  (External IP)  │          │  │  │
│  │  │  └────────────────┘            └─────────────────┘          │  │  │
│  │  │                                                               │  │  │
│  │  │  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐ │  │  │
│  │  │  │ Node Exporter  │  │ Kube-State   │  │   cAdvisor      │ │  │  │
│  │  │  │ (Node metrics) │  │   Metrics    │  │ (Container)     │ │  │  │
│  │  │  └────────────────┘  └──────────────┘  └─────────────────┘ │  │  │
│  │  └──────────────────────────────────────────────────────────────┘  │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Metrics Flow
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                          AI AGENT LAYER (Future)                            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        AI Agent Service                              │  │
│  │                                                                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐ │  │
│  │  │  Prometheus  │  │  Kubernetes  │  │   Benchmark Archive      │ │  │
│  │  │     Tool     │  │     Tool     │  │        Tool              │ │  │
│  │  └──────────────┘  └──────────────┘  └──────────────────────────┘ │  │
│  │         ▲                  ▲                      ▲                  │  │
│  │         └──────────────────┴──────────────────────┘                  │  │
│  │                            │                                          │  │
│  │                    ┌───────┴────────┐                                │  │
│  │                    │  LLM (GPT-4)   │                                │  │
│  │                    │   Orchestrator │                                │  │
│  │                    └───────┬────────┘                                │  │
│  │                            │                                          │  │
│  │         ┌──────────────────┼──────────────────┐                      │  │
│  │         ▼                  ▼                  ▼                      │  │
│  │    ┌────────┐         ┌────────┐        ┌─────────┐                │  │
│  │    │  CLI   │         │  API   │        │ Web UI  │                │  │
│  │    └────────┘         └────────┘        └─────────┘                │  │
│  │                                                                      │  │
│  │  Capabilities:                                                       │  │
│  │  - Metrics Analysis & Anomaly Detection                             │  │
│  │  - Deployment Status & Troubleshooting                              │  │
│  │  - Optimization Recommendations                                     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

## Control Flow & Responsibilities

### Who Manages What?

This diagram clarifies the separation of concerns between components:

```
User Command:
  python automation/main.py --cloud gcp --machine-type n2-standard-4 --duration 600

                            ↓
┌────────────────────────────────────────────────────────────────┐
│ Python Orchestrator (automation/main.py)                       │
│ ├─ Parses CLI arguments                                        │
│ ├─ Generates benchmark run ID                                  │
│ └─ Orchestrates entire pipeline                                │
└─────┬──────────────────────┬──────────────────┬────────────────┘
      │                      │                  │
      ▼                      ▼                  ▼
┌─────────────┐    ┌──────────────────┐   ┌────────────────┐
│  Terraform  │    │      Helm        │   │  Prometheus    │
│  Executor   │    │    Deployer      │   │    Client      │
└─────┬───────┘    └────┬─────────────┘   └────┬───────────┘
      │                 │                      │
      │ Creates         │ Deploys to          │ Queries
      │ terraform.tfvars│ existing cluster    │ metrics from
      │ Runs: init,     │                     │ running cluster
      │ plan, apply     │                     │
      ▼                 ▼                      ▼
┌──────────────┐   ┌─────────────────┐   ┌──────────────────┐
│ Terraform    │   │  Applications   │   │  Time-series     │
│ (main.tf)    │   │  - Boutique     │   │  Metrics         │
│ Provisions:  │   │  - Prometheus   │   │  - CPU/Memory    │
│ - GKE cluster│   │  - Grafana      │   │  - Network       │
│ - Node pools │   │                 │   │  - Throttling    │
└──────────────┘   └─────────────────┘   └──────────────────┘
```

### Responsibility Matrix

| Component | Manages | Input Source | Configuration Method | Can Run Standalone? |
|-----------|---------|--------------|---------------------|---------------------|
| **Python Orchestrator** | End-to-end workflow, error handling, artifact generation | CLI arguments from user | `automation/main.py --help` | ✅ Yes (primary interface) |
| **Terraform** | Kubernetes cluster lifecycle (create/destroy) | Auto-generated `terraform.tfvars` by Python | Python creates config dynamically | ⚠️ Yes, but not recommended* |
| **Helm** | Application deployment to existing cluster | Orchestrator commands | Python calls helm commands | ❌ No (needs cluster from Terraform) |
| **Prometheus** | Metrics scraping and storage | Helm deployment | Python queries via API | ❌ No (deployed by Helm) |

\* *You can run Terraform manually, but you lose the automation, metrics collection, and artifact generation that make the benchmarking useful.*

### Key Design Decisions

1. **Python is the Primary Interface**
   - Users interact only with `automation/main.py` CLI
   - All configuration happens via CLI arguments
   - Terraform, Helm, and Prometheus are internal tools

2. **Terraform Configuration is Auto-Generated**
   - Python creates `terraform.tfvars` on every run
   - Ensures consistency between CLI args and infrastructure
   - Eliminates configuration drift

3. **Fixed Infrastructure Settings**
   - Many Terraform settings are intentionally hardcoded (no autoscaling, fixed monitoring, etc.)
   - This ensures reproducible benchmarks across runs
   - Users control only what affects CPU performance: machine_type, node_count, region

4. **Ephemeral Clusters**
   - Clusters are created, tested, and destroyed
   - No persistent infrastructure management needed
   - Simplifies workflow and reduces costs

## Component Details

### 1. Orchestration Layer
- **Python Scripts**: Main automation logic that drives the entire pipeline
- **Modules**: Specialized components (TerraformExecutor, HelmDeployer, PrometheusClient)
- **Configuration**: All settings come from CLI arguments, no config files needed

### 2. Infrastructure Layer
- **Terraform**: Provisions Kubernetes clusters via declarative IaC
- **Multi-cloud Support**: GCP (implemented), AWS/Azure (templated, not implemented)
- **Fixed Configuration**: Reproducibility over flexibility - many settings are intentionally immutable

### 3. Kubernetes Cluster
- **Online Boutique**: Production-like microservices workload
- **Monitoring Stack**: Prometheus + Grafana for metrics
- **Fixed Resources**: Consistent resource allocation

### 4. Metrics & Storage
- **Time-series Metrics**: Collected by Prometheus
- **Benchmark Artifacts**: JSON/CSV files for comparison
- **Historical Data**: Enables trend analysis

### 5. AI Agent (Design)
- **Read-only Access**: Safe operational intelligence
- **Multiple Interfaces**: CLI, API, Web UI
- **LLM-powered**: Natural language queries and insights

## PlantUML Architecture Diagrams

### System Component Diagram

The following PlantUML diagram provides a visual representation of the system architecture with clear component relationships:

```plantuml
@startuml Benchmark Pipeline Architecture

!define RECTANGLE class

skinparam componentStyle rectangle
skinparam backgroundColor #FEFEFE
skinparam component {
    BackgroundColor<<orchestration>> #E1F5FF
    BackgroundColor<<infrastructure>> #FFF3E0
    BackgroundColor<<application>> #E8F5E9
    BackgroundColor<<monitoring>> #FCE4EC
    BackgroundColor<<ai>> #F3E5F5
    BorderColor #333333
    FontSize 12
}

package "Orchestration Layer" <<orchestration>> {
    [Python Orchestrator] as Orchestrator
    [Terraform Executor] as TerraformExec
    [Helm Deployer] as HelmDeploy
    [Prometheus Client] as PrometheusClient
    [Benchmark Runner] as BenchmarkRunner
    [Artifact Generator] as ArtifactGen
}

package "Infrastructure Layer" <<infrastructure>> {
    [Terraform IaC] as Terraform
    cloud "Cloud Provider" {
        [GCP/GKE] as GCP
        [AWS/EKS] as AWS
        [Azure/AKS] as Azure
    }
}

package "Kubernetes Cluster" <<application>> {
    package "Application Namespace" {
        [Online Boutique\nMicroservices] as OnlineBoutique
        [Load Generator] as LoadGen
    }
    
    package "Monitoring Namespace" {
        [Prometheus] as Prometheus
        [Grafana] as Grafana
        [Node Exporter] as NodeExporter
        [cAdvisor] as cAdvisor
    }
}

package "Data Storage" {
    database "Benchmark\nArtifacts" as Artifacts {
        file "JSON Files" as JSON
        file "CSV Files" as CSV
    }
}

package "AI Agent Layer (Future)" <<ai>> {
    [AI Agent Service] as AIAgent
    [LLM (GPT-4)] as LLM
    [Grafana AI] as GrafanaAI
}

' Orchestrator connections
Orchestrator --> TerraformExec : controls
Orchestrator --> HelmDeploy : controls
Orchestrator --> BenchmarkRunner : controls
Orchestrator --> PrometheusClient : queries
Orchestrator --> ArtifactGen : generates

' Infrastructure provisioning
TerraformExec --> Terraform : executes
Terraform --> GCP : provisions
Terraform --> AWS : provisions (future)
Terraform --> Azure : provisions (future)

' Application deployment
HelmDeploy --> OnlineBoutique : deploys
HelmDeploy --> Prometheus : deploys
HelmDeploy --> Grafana : deploys

' Monitoring flow
OnlineBoutique --> Prometheus : exposes metrics
LoadGen --> OnlineBoutique : generates traffic
NodeExporter --> Prometheus : node metrics
cAdvisor --> Prometheus : container metrics
Grafana --> Prometheus : queries

' Data collection
PrometheusClient --> Prometheus : queries (PromQL)
ArtifactGen --> JSON : creates
ArtifactGen --> CSV : creates

' AI Agent integration
AIAgent --> Prometheus : queries metrics
AIAgent --> JSON : reads history
AIAgent --> LLM : uses
GrafanaAI --> Grafana : integrated
GrafanaAI --> Prometheus : queries

note right of Orchestrator
  Single entry point for
  all benchmark operations
end note

note right of Terraform
  Cloud-agnostic infrastructure
  Fixed configurations for
  reproducible benchmarks
end note

note right of Prometheus
  Collects time-series metrics:
  - CPU utilization
  - Memory usage
  - Request rates
  - Latency
end note

note right of AIAgent
  Provides operational intelligence:
  - Metrics analysis
  - Anomaly detection
  - Recommendations
end note

@enduml
```

### Data Flow Sequence Diagram

This PlantUML sequence diagram illustrates the complete benchmark execution workflow:

```plantuml
@startuml Benchmark Execution Flow

skinparam backgroundColor #FEFEFE
skinparam sequenceArrowThickness 2
skinparam roundcorner 10
skinparam maxmessagesize 150

actor Operator
participant "Python\nOrchestrator" as Orch
participant "Terraform" as TF
participant "GCP/Cloud" as Cloud
participant "Helm" as Helm
participant "Kubernetes" as K8s
participant "Online\nBoutique" as App
participant "Prometheus" as Prom
participant "Grafana" as Graf
database "Benchmark\nArtifacts" as Artifacts

== Infrastructure Provisioning ==
Operator -> Orch: Run benchmark command
activate Orch

Orch -> TF: terraform apply
activate TF
TF -> Cloud: Create GKE cluster
activate Cloud
Cloud --> TF: Cluster ready
deactivate Cloud
TF --> Orch: Infrastructure provisioned
deactivate TF

== Application Deployment ==
Orch -> Helm: Deploy Online Boutique
activate Helm
Helm -> K8s: Create deployments
activate K8s
K8s -> App: Start microservices
activate App
App --> K8s: Pods running
K8s --> Helm: Deployment successful
deactivate K8s
Helm --> Orch: Application deployed
deactivate Helm

Orch -> Helm: Deploy Prometheus/Grafana
activate Helm
Helm -> K8s: Create monitoring stack
activate K8s
K8s -> Prom: Start Prometheus
activate Prom
K8s -> Graf: Start Grafana
activate Graf
K8s --> Helm: Monitoring deployed
deactivate K8s
Helm --> Orch: Monitoring ready
deactivate Helm

== Benchmark Execution ==
Orch -> App: Enable load generator
App -> App: Generate traffic (N seconds)
note right: Fixed duration\nFixed load profile

App -> Prom: Export metrics
Prom -> Prom: Collect & store\ntime-series data

== Metrics Collection ==
Orch -> Prom: Query metrics (PromQL)
Prom --> Orch: Return time-series data
deactivate Prom

== Artifact Generation ==
Orch -> Orch: Aggregate metrics
Orch -> Orch: Calculate normalized metrics
Orch -> Artifacts: Write JSON file
Orch -> Artifacts: Write CSV file
Artifacts --> Orch: Artifacts saved

== Visualization ==
Operator -> Graf: View dashboard
Graf -> Prom: Query metrics
Prom --> Graf: Return data
Graf --> Operator: Display visualizations
deactivate Graf

== Cleanup (Optional) ==
Orch -> TF: terraform destroy
activate TF
TF -> Cloud: Delete resources
activate Cloud
Cloud --> TF: Resources deleted
deactivate Cloud
TF --> Orch: Cleanup complete
deactivate TF

Orch --> Operator: Benchmark complete
deactivate Orch
deactivate App

note over Operator, Artifacts
  Complete benchmark cycle: 20-30 minutes
  - Provisioning: 8-10 min
  - Deployment: 5-7 min
  - Execution: 5-10 min
  - Collection: 1-2 min
  - Cleanup: 5-8 min
end note

@enduml
```

### Deployment Architecture Diagram

This diagram shows the Kubernetes cluster internal structure:

```plantuml
@startuml Kubernetes Deployment Architecture

!define RECTANGLE class

skinparam component {
    BackgroundColor<<namespace>> #E3F2FD
    BackgroundColor<<service>> #C8E6C9
    BackgroundColor<<monitoring>> #FFE0B2
    BorderColor #333333
}

package "Kubernetes Cluster" {
    
    package "default namespace" <<namespace>> {
        component "Frontend\nService" as Frontend <<service>>
        component "Cart\nService" as Cart <<service>>
        component "Checkout\nService" as Checkout <<service>>
        component "Payment\nService" as Payment <<service>>
        component "Product Catalog\nService" as Product <<service>>
        component "Currency\nService" as Currency <<service>>
        component "Shipping\nService" as Shipping <<service>>
        component "Recommendation\nService" as Recommend <<service>>
        component "Email\nService" as Email <<service>>
        component "Ad\nService" as Ad <<service>>
        component "Redis\nCart" as Redis <<service>>
        component "Load\nGenerator" as LoadGen <<service>>
    }
    
    package "monitoring namespace" <<namespace>> {
        component "Prometheus" as Prom <<monitoring>>
        component "Grafana" as Graf <<monitoring>>
        component "Node\nExporter" as NodeExp <<monitoring>>
        component "Kube State\nMetrics" as KubeMet <<monitoring>>
        component "cAdvisor" as cAdv <<monitoring>>
    }
    
    component "Node Pool\n(Fixed Machine Type)" as NodePool {
        component "Node 1" as Node1
        component "Node 2" as Node2
        component "Node 3" as Node3
    }
}

' Service connections
LoadGen --> Frontend : HTTP traffic
Frontend --> Cart : gRPC
Frontend --> Product : gRPC
Frontend --> Currency : gRPC
Frontend --> Recommend : gRPC
Frontend --> Ad : gRPC
Frontend --> Shipping : gRPC
Cart --> Redis : TCP
Checkout --> Cart : gRPC
Checkout --> Product : gRPC
Checkout --> Currency : gRPC
Checkout --> Shipping : gRPC
Checkout --> Email : gRPC
Checkout --> Payment : gRPC

' Monitoring connections
Frontend --> Prom : metrics
Cart --> Prom : metrics
Checkout --> Prom : metrics
Payment --> Prom : metrics
Product --> Prom : metrics
Currency --> Prom : metrics
Shipping --> Prom : metrics
Recommend --> Prom : metrics
Email --> Prom : metrics
Ad --> Prom : metrics
Redis --> Prom : metrics

NodeExp --> Prom : node metrics
KubeMet --> Prom : K8s metrics
cAdv --> Prom : container metrics

Graf --> Prom : queries

' Node placement
Frontend -[hidden]-> Node1
Cart -[hidden]-> Node2
Checkout -[hidden]-> Node3
Prom -[hidden]-> Node1
Graf -[hidden]-> Node2

note right of NodePool
  Fixed configuration:
  - Machine type (e.g., n2-standard-4)
  - CPU vendor labeled
  - No autoscaling
  - Single zone
  - Pinned Kubernetes version
end note

note right of Prom
  Metrics collected (v2.0):
  - CPU utilization (cluster, pod, node)
  - Memory usage (all levels)
  - CPU throttling (per-pod)
  - Request rates
  - Network I/O
  - 30s scrape interval
end note

@enduml
```

### How to Use PlantUML Diagrams

To render these diagrams:

1. **Online**: Visit [PlantUML Online Editor](http://www.plantuml.com/plantuml/uml/)
2. **VS Code**: Install "PlantUML" extension
3. **Command Line**: Install PlantUML and run:
   ```bash
   plantuml diagram.puml
   ```
4. **Documentation**: Many documentation platforms (Confluence, GitHub with plugins) support PlantUML rendering

These diagrams can be embedded in documentation, presentations, or exported as PNG/SVG for reports.

## Data Flow

```
1. User initiates benchmark
   └─> Docker Container (benchmark.sh wrapper)
        └─> Python Orchestrator (main.py)

2. Provision infrastructure
   └─> Terraform creates K8s cluster with fixed config
       - Auto-generates terraform.tfvars from CLI args
       - Provisions GKE with n2/n2d/t2a nodes
       - Applies CPU vendor labels

3. Deploy applications
   ├─> Helm deploys Online Boutique
   └─> Helm deploys Prometheus/Grafana stack

4. Execute benchmark
   └─> Load generator creates traffic for N seconds
       - Configurable users (default: 300)
       - Configurable RPS (default: 50)

5. Collect metrics (v2.0 Enhanced)
   └─> Python queries Prometheus API (PromQL)
       - Cluster-level aggregates
       - Per-pod granular metrics
       - Per-node infrastructure metrics
       - Machine specs enrichment

6. Generate artifacts (4 files)
   ├─> Complete JSON with all data
   ├─> Cluster summary CSV (quick comparison)
   ├─> Per-node CSV (infrastructure view)
   └─> Per-pod CSV (application bottlenecks)

7. Cleanup (optional)
   └─> Terraform destroys all resources

8. Analyze (Future)
   └─> AI Agent provides insights from artifacts
```

## Key Design Principles

1. **Reproducibility**: Fixed configurations and pinned tool versions ensure comparable results
2. **Containerization**: Docker eliminates "works on my machine" problems
3. **Cloud-agnostic**: Kubernetes abstraction enables portability
4. **Automation-first**: One command from setup to results
5. **Separation of concerns**: Distinct tools for distinct tasks (Terraform/Helm/Python)
6. **Observability**: Comprehensive metrics collection at multiple granularities
7. **Extensibility**: Modular design supports future enhancements
8. **Version Control**: Pinned dependencies (Terraform 1.7.5, Helm 3.14.0, kubectl 1.29.2)

## Network Topology

```
┌──────────────────────────────────────────────────────────────┐
│                    Cloud Provider Network                     │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Kubernetes Cluster (VPC)                   │  │
│  │                                                          │  │
│  │  ┌─────────────────┐      ┌─────────────────────────┐  │  │
│  │  │  Namespace:     │      │  Namespace: monitoring  │  │  │
│  │  │  default        │      │                         │  │  │
│  │  │                 │      │  ┌──────────────────┐   │  │  │
│  │  │  ┌───────────┐  │      │  │   Prometheus     │   │  │  │
│  │  │  │  Online   │  │      │  │   (ClusterIP)    │   │  │  │
│  │  │  │ Boutique  │  │      │  └────────┬─────────┘   │  │  │
│  │  │  │ Services  │──scrape─────────────┘             │  │  │
│  │  │  └───────────┘  │      │                         │  │  │
│  │  │        │        │      │  ┌──────────────────┐   │  │  │
│  │  │  ┌─────▼─────┐ │      │  │    Grafana       │   │  │  │
│  │  │  │LoadBalancer│◄─────query──│ (LoadBalancer) │   │  │  │
│  │  │  │(External) │ │      │  └──────────────────┘   │  │  │
│  │  │  └───────────┘ │      └─────────────────────────┘  │  │
│  │  └─────────────────┘                                   │  │
│  │                                                         │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         │ External Access
                         │
                 ┌───────┴────────┐
                 │   Operator     │
                 │  (kubectl)     │
                 └────────────────┘
```

## Security Layers

1. **Network**: VPC isolation, network policies
2. **Access**: RBAC, service accounts
3. **Credentials**: Secrets management, encrypted at rest
4. **Audit**: Logging of all operations
5. **Agent**: Read-only permissions, no cluster modifications

## File Structure

```
DevOpsAIUseCase/
├── Dockerfile                 # Complete pipeline containerization
├── docker-compose.yml         # Optional: Compose configuration
├── benchmark.sh               # Docker wrapper script (primary interface)
├── .dockerignore              # Docker build exclusions
├── terraform/                 # Infrastructure as Code
│   ├── gcp/                  # GCP configuration (✅ production-ready)
│   ├── aws/                  # AWS configuration (📋 template)
│   └── azure/                # Azure configuration (📋 template)
├── kubernetes/                # K8s manifests and Helm values
│   ├── online-boutique/      # Application deployment
│   └── monitoring/           # Prometheus + Grafana
├── automation/                # Python orchestration
│   ├── main.py              # Entry point
│   ├── modules/             # Automation modules
│   │   ├── terraform_executor.py
│   │   ├── helm_deployer.py
│   │   ├── prometheus_client.py
│   │   ├── benchmark_runner.py
│   │   ├── artifact_generator.py
│   │   └── machine_specs.py     # ✨ GCP machine metadata (v2.0)
│   └── requirements.txt     # Python dependencies
├── benchmarks/                # Output artifacts (4 files per run)
│   ├── <cloud>-<vendor>-<timestamp>.json
│   ├── cluster_summary.csv
│   ├── <run-id>_nodes.csv
│   └── <run-id>_pods.csv
├── docs/                      # Documentation
│   ├── ARCHITECTURE.md       # This file
│   ├── DOCKER.md             # Docker usage guide
│   ├── IMPLEMENTATION.md     # Implementation status
│   ├── QUICK_REFERENCE.md    # Command cheat sheet
│   ├── GETTING_STARTED.md    # (Archived - see README)
│   └── AI_AGENT_ARCHITECTURE.md
└── README.md                  # Comprehensive guide (consolidated)
```
