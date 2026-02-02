# System Architecture Diagram

## Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BENCHMARK ORCHESTRATION LAYER                        │
│                                                                              │
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
│  │  │   Runner     │  │   (JSON/CSV output)              │          │    │
│  │  └──────────────┘  └──────────────────────────────────┘          │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└───────────────┬────────────────────────────────────────────┬────────────────┘
                │                                            │
                ▼                                            ▼
┌───────────────────────────────────┐    ┌──────────────────────────────────┐
│    INFRASTRUCTURE LAYER           │    │     BENCHMARK ARTIFACTS          │
│                                   │    │                                  │
│  ┌─────────────────────────────┐ │    │  ┌────────────────────────────┐ │
│  │   Terraform (IaC)           │ │    │  │  benchmarks/*.json         │ │
│  │                             │ │    │  │  - Machine metadata        │ │
│  │  ┌──────┐  ┌──────┐        │ │    │  │  - Performance metrics     │ │
│  │  │ GCP  │  │ AWS  │ ...    │ │    │  │  - Normalized results      │ │
│  │  └──────┘  └──────┘        │ │    │  └────────────────────────────┘ │
│  │                             │ │    │                                  │
│  │  Creates:                   │ │    │  ┌────────────────────────────┐ │
│  │  - Kubernetes clusters      │ │    │  │  benchmarks/*.csv          │ │
│  │  - Fixed node pools         │ │    │  │  - Comparison-ready format │ │
│  │  - Node labels (CPU info)   │ │    │  └────────────────────────────┘ │
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

## Component Details

### 1. Orchestration Layer
- **Python Scripts**: Main automation logic
- **Modules**: Specialized components for each task
- **Configuration**: Parameterized for different scenarios

### 2. Infrastructure Layer
- **Terraform**: Cloud-agnostic IaC
- **Multi-cloud Support**: GCP (implemented), AWS/Azure (planned)
- **Fixed Configuration**: Ensures reproducible benchmarks

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

## Data Flow

```
1. User initiates benchmark
   └─> Python Orchestrator

2. Provision infrastructure
   └─> Terraform creates K8s cluster with fixed config

3. Deploy applications
   ├─> Helm deploys Online Boutique
   └─> Helm deploys Prometheus/Grafana

4. Execute benchmark
   └─> Load generator creates traffic for N seconds

5. Collect metrics
   └─> Python queries Prometheus API (PromQL)

6. Generate artifacts
   ├─> JSON file with complete results
   └─> CSV file for easy comparison

7. Analyze (Future)
   └─> AI Agent provides insights
```

## Key Design Principles

1. **Reproducibility**: Fixed configurations ensure comparable results
2. **Cloud-agnostic**: Kubernetes abstraction enables portability
3. **Automation-first**: Minimal manual intervention
4. **Separation of concerns**: Distinct tools for distinct tasks
5. **Observability**: Comprehensive metrics collection
6. **Extensibility**: Modular design supports future enhancements

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
├── terraform/              # Infrastructure as Code
│   ├── gcp/               # GCP configuration (implemented)
│   ├── aws/               # AWS configuration (template)
│   └── azure/             # Azure configuration (template)
├── kubernetes/            # K8s manifests and Helm values
│   ├── online-boutique/   # Application deployment
│   └── monitoring/        # Prometheus + Grafana
├── automation/            # Python orchestration
│   ├── main.py           # Entry point
│   ├── modules/          # Automation modules
│   └── requirements.txt  # Dependencies
├── benchmarks/           # Output artifacts (JSON/CSV)
├── docs/                 # Documentation
│   ├── diagrams/         # Architecture diagrams
│   └── AI_AGENT_ARCHITECTURE.md
└── README.md            # Project overview
```
