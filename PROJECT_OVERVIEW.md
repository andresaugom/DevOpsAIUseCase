# Project Overview

## What is This Project?

This repository implements an **automated Cloud Infrastructure Benchmarking pipeline** to evaluate CPU performance across different cloud providers using the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) microservices application as a realistic workload.

## Quick Links

- [Getting Started Guide](docs/GETTING_STARTED.md) - Start here!
- [System Architecture](docs/ARCHITECTURE.md) - How it all works
- [AI Agent Design](docs/AI_AGENT_ARCHITECTURE.md) - Future enhancements
- [Implementation Status](docs/IMPLEMENTATION.md) - What's been built

## What's Included

This repository provides a **complete, working foundation** with:

### 1. Infrastructure Automation (Terraform)
- GCP/GKE implementation (ready to use)
- AWS/Azure templates (ready to extend)
- Reproducible, fixed configurations
- CPU vendor/generation tracking

### 2. Application Deployment (Kubernetes/Helm)
- Online Boutique microservices
- Prometheus + Grafana monitoring
- Fixed resource limits for consistency
- Pre-configured dashboards

### 3. Automation Orchestrator (Python)
- End-to-end workflow automation
- Metrics collection from Prometheus
- Benchmark artifact generation
- Command-line interface

### 4. Documentation
- Architecture diagrams
- AI agent design (23+ pages)
- Getting started guides
- Troubleshooting tips

## One Command Benchmark

```bash
cd automation

python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --duration 600 \
  --cleanup
```

**Output:**
- Live Grafana dashboard with metrics
- JSON file with complete results
- CSV file for easy comparison

## Use Cases

### 1. CPU Performance Comparison
Compare Intel vs AMD vs ARM processors:
```bash
# Intel Ice Lake
python main.py --cloud gcp --machine-type n2-standard-4 --cpu-vendor intel --duration 600

# AMD Milan
python main.py --cloud gcp --machine-type n2d-standard-4 --cpu-vendor amd --duration 600

# ARM (Ampere Altra)
python main.py --cloud gcp --machine-type t2a-standard-4 --cpu-vendor arm --duration 600
```

### 2. Multi-Cloud Comparison
Test same workload across GCP, AWS, Azure (after implementing AWS/Azure):
```bash
python main.py --cloud gcp --machine-type n2-standard-4 --duration 600
python main.py --cloud aws --machine-type m6i.xlarge --duration 600
python main.py --cloud azure --machine-type Standard_D4s_v5 --duration 600
```

### 3. Historical Trend Analysis
Run benchmarks regularly to track performance over time:
- All results saved in `benchmarks/` directory
- Compare JSON files or import CSV to spreadsheet
- Identify performance trends and regressions

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Infrastructure** | Terraform | Cloud-agnostic cluster provisioning |
| **Orchestration** | Kubernetes | Standardized container orchestration |
| **Application** | Helm | Package management and deployment |
| **Monitoring** | Prometheus + Grafana | Metrics collection and visualization |
| **Automation** | Python 3.11+ | End-to-end workflow orchestration |
| **Workload** | Online Boutique | Realistic microservices application |

## Repository Structure

```
DevOpsAIUseCase/
├── terraform/          # Infrastructure as Code
│   ├── gcp/           # GKE (implemented)
│   ├── aws/           # EKS (template)
│   └── azure/         # AKS (template)
├── kubernetes/        # Application configs
│   ├── online-boutique/
│   └── monitoring/
├── automation/        # Python orchestrator
│   ├── main.py
│   └── modules/
├── benchmarks/        # Output artifacts
├── docs/              # Documentation
│   ├── GETTING_STARTED.md
│   ├── ARCHITECTURE.md
│   ├── AI_AGENT_ARCHITECTURE.md
│   └── IMPLEMENTATION.md
└── README.md          # This file
```

## Key Features

### Reproducibility
- Fixed machine types and node counts
- Consistent resource limits
- Deterministic metric collection
- Immutable benchmark artifacts

### Cloud-Agnostic
- Kubernetes abstraction layer
- Terraform for infrastructure
- Helm for application deployment
- Portable across providers

### Comprehensive Metrics
- CPU utilization (avg, P95)
- Memory usage
- CPU throttling
- Request rate
- Normalized efficiency metrics

### Production-Quality
- Error handling and logging
- Modular, maintainable code
- Comprehensive documentation
- Security best practices

### Future-Ready
- AI agent architecture designed
- Extensible module structure
- Integration points defined
- Scalable design

## Getting Started

### Prerequisites
- Python 3.11+
- Terraform >= 1.0
- kubectl
- Helm 3
- Cloud provider account (GCP, AWS, or Azure)

### Quick Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/andresaugom/DevOpsAIUseCase.git
   cd DevOpsAIUseCase
   ```

2. **Install dependencies**
   ```bash
   cd automation
   pip install -r requirements.txt
   ```

3. **Configure cloud credentials**
   ```bash
   # For GCP
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   export GCP_PROJECT_ID=your-project-id
   ```

4. **Run your first benchmark**
   ```bash
   python main.py \
     --cloud gcp \
     --machine-type n2-standard-4 \
     --duration 300 \
     --cleanup
   ```

**See [Getting Started Guide](docs/GETTING_STARTED.md) for detailed instructions.**

## Benchmark Output

Each benchmark produces two files in `benchmarks/`:

### JSON File (Complete Results)
```json
{
  "run_id": "gcp-intel-20260201-143022",
  "cloud": "gcp",
  "node_pool": {
    "machine_type": "n2-standard-4",
    "cpu_vendor": "intel",
    "cpu_generation": "Ice Lake"
  },
  "metrics": {
    "avg_cpu_util_pct": 63.2,
    "avg_memory_mb": 1240,
    "request_rate_rps": 125.3
  },
  "normalized_metrics": {
    "cpu_seconds_per_request": 0.018
  }
}
```

### CSV File (Easy Comparison)
Ready for import into Excel/Google Sheets for side-by-side comparison.

## AI Agent (Designed, Not Implemented)

The repository includes a comprehensive **AI Agent Architecture Document** that describes:

- Technology stack (Python, LangChain, OpenAI)
- System architecture and data flow
- Integration with Prometheus and Kubernetes
- User interfaces (CLI, API, Web)
- Security and cost considerations
- Implementation roadmap
- Code examples

**See [AI Agent Architecture](docs/AI_AGENT_ARCHITECTURE.md) for details.**

The AI agent would provide:
- **Metrics Analysis**: Anomaly detection, correlation analysis
- **Deployment Assistant**: Status queries, troubleshooting
- **Recommendations**: Resource optimization, cost savings

## Architecture Diagrams

Visual representations of the system:

1. **Overall System Architecture** - Component interactions
2. **Data Flow** - How data moves through the pipeline
3. **Network Topology** - Kubernetes cluster layout
4. **AI Agent Architecture** - Future enhancement design

**See [Architecture Documentation](docs/ARCHITECTURE.md) for diagrams.**

## Design Principles

1. **Reproducibility**: Same inputs = same outputs
2. **Cloud-Agnostic**: Portable across providers
3. **Automation-First**: Minimal manual steps
4. **Separation of Concerns**: Modular components
5. **Observability**: Comprehensive metrics
6. **Extensibility**: Easy to enhance

## Cost Considerations

**Typical benchmark cost (GCP):**
- n2-standard-4 (3 nodes): ~$0.50/hour
- 30-minute benchmark: ~$0.25
- 4 benchmarks/day: ~$1.00

**Cost-saving tips:**
- Use `--cleanup` flag to delete resources
- Run during off-peak hours
- Use smaller machine types for testing
- Delete unused clusters

## Use Case: Processor Evaluation

**Scenario:** Your company needs to choose between Intel Ice Lake and AMD Milan processors for production workloads.

**Solution with this pipeline:**

1. Run benchmark on Intel (n2-standard-4)
2. Run benchmark on AMD (n2d-standard-4)
3. Compare results:
   - CPU efficiency (cpu_seconds_per_request)
   - Memory usage
   - Request throughput
   - Cost per request
4. Make data-driven decision

## Documentation Index

| Document | Description |
|----------|-------------|
| [GETTING_STARTED.md](docs/GETTING_STARTED.md) | Installation and first benchmark |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and diagrams |
| [AI_AGENT_ARCHITECTURE.md](docs/AI_AGENT_ARCHITECTURE.md) | AI agent design (23 pages) |
| [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) | What's been built |
| [terraform/README.md](terraform/README.md) | Infrastructure details |
| [kubernetes/README.md](kubernetes/README.md) | Deployment details |
| [automation/README.md](automation/README.md) | Automation details |
| [benchmarks/README.md](benchmarks/README.md) | Results interpretation |

## Contributing

This project welcomes contributions:

1. **Add cloud providers**: Implement AWS/Azure
2. **Enhance metrics**: Add custom PromQL queries
3. **Improve automation**: Add features to orchestrator
4. **Implement AI agent**: Follow architecture document
5. **Create dashboards**: Design new Grafana dashboards

## Roadmap

### Phase 1: Foundation (Complete)
- GCP/GKE implementation
- Python automation
- Documentation
- AI agent design

### Phase 2: Validation
- Test GCP implementation
- Collect sample benchmarks
- Refine metrics

### Phase 3: Multi-Cloud
- Implement AWS EKS
- Implement Azure AKS
- Cross-cloud comparison

### Phase 4: AI Agent
- Implement basic CLI
- Add Prometheus integration
- Create REST API

### Phase 5: Production
- Security hardening
- CI/CD integration
- Advanced features

## Support

For issues or questions:

1. Review documentation in `docs/`
2. Check Terraform/Kubernetes READMEs
3. Look at troubleshooting guides
4. Check logs: `kubectl logs <pod-name>`

## License

This project is for educational and benchmarking purposes. The Online Boutique application is licensed by Google under Apache 2.0.

## Acknowledgments

- **Online Boutique**: Google Cloud Platform microservices demo
- **Prometheus**: Metrics collection and monitoring
- **Kubernetes**: Container orchestration
- **Terraform**: Infrastructure as Code

---

## Quick Command Reference

```bash
# Run a complete benchmark with cleanup
python automation/main.py --cloud gcp --machine-type n2-standard-4 --duration 600 --cleanup

# Run without provisioning (use existing cluster)
python automation/main.py --cloud gcp --machine-type n2-standard-4 --duration 600 --skip-provision

# Cleanup only
python automation/main.py --cloud gcp --cleanup-only

# View results
ls -lh benchmarks/
cat benchmarks/*.json
```

---

**This is a complete, working foundation for Cloud Infrastructure Benchmarking. Start with the [Getting Started Guide](docs/GETTING_STARTED.md)!**
