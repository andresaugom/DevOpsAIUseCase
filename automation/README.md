# Automation Scripts

This directory contains the Python automation orchestrator for the Online Boutique benchmarking pipeline.

## Overview

The automation orchestrator coordinates all phases of the benchmark:
1. Infrastructure provisioning (Terraform)
2. Application deployment (Helm)
3. Monitoring setup (Prometheus + Grafana)
4. Benchmark execution
5. Metrics collection
6. Artifact generation

## Quick Start

### Install Dependencies

```bash
cd automation
pip install -r requirements.txt
```

### Run a Benchmark

```bash
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --cpu-generation "Ice Lake" \
  --duration 600 \
  --node-count 3
```

### Full Lifecycle (Provision + Benchmark + Cleanup)

```bash
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --duration 600 \
  --cleanup
```

### Use Existing Cluster

```bash
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --duration 600 \
  --skip-provision
```

### Cleanup Only

```bash
python main.py \
  --cloud gcp \
  --cleanup-only
```

## Architecture

### Main Components

```
main.py                    # Entry point and orchestration
├── modules/
│   ├── terraform_executor.py      # Infrastructure provisioning
│   ├── helm_deployer.py           # Application deployment
│   ├── prometheus_client.py       # Metrics collection
│   ├── benchmark_runner.py        # Benchmark execution
│   └── artifact_generator.py      # Results generation
```

### Workflow

```
┌─────────────────────────────────────────────────┐
│            BenchmarkOrchestrator                │
│                                                 │
│  1. TerraformExecutor.provision_cluster()       │
│     └─> Creates K8s cluster with fixed config   │
│                                                 │
│  2. HelmDeployer.deploy_online_boutique()       │
│     └─> Installs microservices with load gen    │
│                                                 │
│  3. HelmDeployer.deploy_monitoring()            │
│     └─> Installs Prometheus + Grafana           │
│                                                 │
│  4. HelmDeployer.wait_for_services()            │
│     └─> Ensures all pods are running            │
│                                                 │
│  5. BenchmarkRunner.run_benchmark(duration)     │
│     └─> Waits while load is applied             │
│                                                 │
│  6. PrometheusClient.collect_metrics()          │
│     └─> Queries CPU, memory, throttling, etc.   │
│                                                 │
│  7. ArtifactGenerator.generate()                │
│     └─> Creates JSON/CSV benchmark artifacts    │
│                                                 │
│  8. [Optional] cleanup()                        │
│     └─> Removes applications and infrastructure │
│                                                 │
└─────────────────────────────────────────────────┘
```

## Module Details

### terraform_executor.py

Manages Terraform operations:
- Initializes Terraform
- Creates `terraform.tfvars` from config
- Provisions infrastructure
- Retrieves outputs (cluster info)
- Destroys infrastructure

**Key Methods:**
- `provision_cluster()`: Create K8s cluster
- `destroy_cluster()`: Remove infrastructure
- `_get_outputs()`: Retrieve Terraform outputs

### helm_deployer.py

Manages Helm deployments:
- Adds Helm repositories
- Deploys Online Boutique with custom values
- Deploys Prometheus + Grafana stack
- Waits for services to be ready
- Uninstalls releases

**Key Methods:**
- `deploy_online_boutique()`: Install application
- `deploy_monitoring()`: Install monitoring stack
- `wait_for_services()`: Wait for pods to be Running
- `uninstall_all()`: Remove all Helm releases

### prometheus_client.py

Queries Prometheus metrics:
- Executes PromQL queries
- Aggregates time-series data
- Collects benchmark metrics

**Metrics Collected:**
- Average CPU utilization
- P95 CPU utilization
- CPU throttling seconds
- Average memory usage
- Request rate

**Key Methods:**
- `collect_metrics(start_time, end_time)`: Get all metrics
- `_query_range()`: Execute range query
- `_query_instant()`: Execute instant query

### benchmark_runner.py

Executes benchmarks:
- Runs for specified duration
- Logs progress
- Records start/end times

**Key Methods:**
- `run_benchmark(duration)`: Execute benchmark run

### artifact_generator.py

Generates output artifacts:
- Creates JSON with full results
- Exports CSV for comparison
- Calculates normalized metrics

**Output Format:**
```json
{
  "run_id": "gcp-intel-20260201-143022",
  "cloud": "gcp",
  "node_pool": {
    "machine_type": "n2-standard-4",
    "cpu_vendor": "intel"
  },
  "metrics": {
    "avg_cpu_util_pct": 63.2,
    "avg_memory_mb": 1240
  }
}
```

**Key Methods:**
- `generate()`: Create artifact dictionary
- `save_artifact()`: Write JSON and CSV files

## Configuration

The orchestrator accepts configuration via command-line arguments:

| Argument | Description | Default |
|----------|-------------|---------|
| `--cloud` | Cloud provider (gcp, aws, azure) | Required |
| `--machine-type` | Machine type (e.g., n2-standard-4) | Required |
| `--cpu-vendor` | CPU vendor (intel, amd, arm) | intel |
| `--cpu-generation` | CPU generation name | Ice Lake |
| `--duration` | Benchmark duration in seconds | 600 |
| `--node-count` | Number of nodes | 3 |
| `--skip-provision` | Skip infrastructure provisioning | False |
| `--cleanup` | Cleanup after benchmark | False |
| `--cleanup-only` | Only perform cleanup | False |

## Environment Variables

Required for cloud provider authentication:

### GCP
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
export GCP_PROJECT_ID=your-project-id
```

### AWS (Future)
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=us-west-2
```

### Azure (Future)
```bash
export AZURE_SUBSCRIPTION_ID=your-subscription-id
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret
```

## Output

### Benchmark Artifacts

Created in `../benchmarks/` directory:

**JSON Format:**
- Complete benchmark results
- Machine and cluster metadata
- All collected metrics
- Normalized metrics

**CSV Format:**
- Flattened data for spreadsheet import
- Easy comparison across runs

### Example Output

```
benchmarks/
├── gcp-intel-20260201-143022.json
├── gcp-intel-20260201-143022.csv
├── gcp-amd-20260201-150530.json
└── gcp-amd-20260201-150530.csv
```

## Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=modules tests/
```

## Code Quality

Format code:

```bash
black .
```

Lint code:

```bash
pylint modules/*.py
flake8 modules/
```

Type check:

```bash
mypy modules/
```

## Troubleshooting

### "Cluster not found"
- Ensure cloud credentials are configured
- Verify project/account has necessary permissions
- Check Terraform state

### "Services not ready"
- Increase timeout in `wait_for_services()`
- Check pod logs: `kubectl logs -n default <pod-name>`
- Verify node resources are sufficient

### "Prometheus query failed"
- Verify Prometheus is running: `kubectl get pods -n monitoring`
- Port-forward to test: `kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090`
- Check PromQL syntax

### "Permission denied"
- Verify cloud credentials
- Check service account permissions
- Ensure kubectl is configured

## Contributing

When adding new features:

1. Add module in `modules/` directory
2. Update `main.py` to integrate
3. Add tests in `tests/`
4. Update this README
5. Run code quality checks

## Future Enhancements

- [ ] AWS EKS support
- [ ] Azure AKS support
- [ ] Multi-region benchmarks
- [ ] Advanced load profiles (ramp-up, spike tests)
- [ ] Real-time metric streaming
- [ ] Benchmark comparison tool
- [ ] AI agent integration
- [ ] Web UI for orchestration

## See Also

- [Main README](../README.md) - Project overview
- [Terraform Documentation](../terraform/README.md) - Infrastructure details
- [Kubernetes Documentation](../kubernetes/README.md) - Deployment details
- [AI Agent Architecture](../docs/AI_AGENT_ARCHITECTURE.md) - Future AI features
