# Getting Started Guide

This guide will help you set up and run your first benchmark.

## Prerequisites

### Required Tools
- Python 3.11 or later
- Terraform >= 1.0
- kubectl
- Helm 3
- Cloud provider CLI (gcloud for GCP)

### Cloud Provider Setup

#### Google Cloud Platform (GCP)

1. **Create a GCP Project** (or use existing)
   ```bash
   gcloud projects create my-benchmark-project
   gcloud config set project my-benchmark-project
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable container.googleapis.com
   gcloud services enable compute.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   gcloud iam service-accounts create benchmark-sa \
     --display-name="Benchmark Service Account"
   
   gcloud projects add-iam-policy-binding my-benchmark-project \
     --member="serviceAccount:benchmark-sa@my-benchmark-project.iam.gserviceaccount.com" \
     --role="roles/container.admin"
   
   gcloud projects add-iam-policy-binding my-benchmark-project \
     --member="serviceAccount:benchmark-sa@my-benchmark-project.iam.gserviceaccount.com" \
     --role="roles/compute.admin"
   ```

4. **Download Service Account Key**
   ```bash
   gcloud iam service-accounts keys create ~/benchmark-key.json \
     --iam-account=benchmark-sa@my-benchmark-project.iam.gserviceaccount.com
   
   export GOOGLE_APPLICATION_CREDENTIALS=~/benchmark-key.json
   ```

5. **Configure Default Project**
   ```bash
   export GCP_PROJECT_ID=my-benchmark-project
   ```

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/andresaugom/DevOpsAIUseCase.git
cd DevOpsAIUseCase
```

### 2. Install Python Dependencies

```bash
cd automation
pip install -r requirements.txt
```

### 3. Verify Tools

```bash
# Check versions
terraform --version
kubectl version --client
helm version
python --version

# Verify cloud authentication
gcloud auth list
```

## Running Your First Benchmark

### Quick Start (Recommended)

This will provision infrastructure, run a benchmark, and clean up automatically:

```bash
cd automation

python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --cpu-generation "Ice Lake" \
  --duration 300 \
  --node-count 3 \
  --cleanup
```

**Note:** This takes approximately 20-30 minutes:
- Infrastructure provisioning: 8-10 minutes
- Application deployment: 5-7 minutes
- Benchmark execution: 5 minutes (as specified)
- Metrics collection: 1-2 minutes
- Cleanup: 5-8 minutes

### Step-by-Step Process

If you want more control, run each phase separately:

#### Phase 1: Provision Infrastructure

```bash
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --duration 0 \
  --skip-benchmark
```

#### Phase 2: Access Grafana

```bash
# Get Grafana URL
kubectl get service -n monitoring prometheus-grafana

# Port-forward if no external IP
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Visit http://localhost:3000
- Username: `admin`
- Password: `admin`

#### Phase 3: Run Benchmark

```bash
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --duration 600 \
  --skip-provision
```

#### Phase 4: View Results

```bash
ls -lh ../benchmarks/
cat ../benchmarks/*.json
```

#### Phase 5: Cleanup

```bash
python main.py --cloud gcp --cleanup-only
```

## Understanding the Output

### Benchmark Artifacts

Each benchmark creates two files in `benchmarks/`:

**JSON File** (`gcp-intel-YYYYMMDD-HHMMSS.json`):
```json
{
  "run_id": "gcp-intel-20260201-143022",
  "timestamp": "2026-02-01T14:30:22",
  "cloud": "gcp",
  "region": "us-central1",
  "zone": "us-central1-a",
  "node_pool": {
    "machine_type": "n2-standard-4",
    "cpu_vendor": "intel",
    "cpu_generation": "Ice Lake",
    "node_count": 3
  },
  "metrics": {
    "avg_cpu_util_pct": 63.2,
    "p95_cpu_util_pct": 81.4,
    "cpu_throttled_seconds": 12.7,
    "avg_memory_mb": 1240,
    "request_rate_rps": 125.3
  },
  "normalized_metrics": {
    "cpu_seconds_per_request": 0.018,
    "memory_mb_per_request": 9.89
  }
}
```

**CSV File** (`gcp-intel-YYYYMMDD-HHMMSS.csv`):
Ready for import into Excel/Google Sheets for comparison.

## Comparing Different CPUs

### Intel vs AMD Example

```bash
# Run Intel benchmark
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --cpu-generation "Ice Lake" \
  --duration 600 \
  --cleanup

# Run AMD benchmark
python main.py \
  --cloud gcp \
  --machine-type n2d-standard-4 \
  --cpu-vendor amd \
  --cpu-generation "Milan" \
  --duration 600 \
  --cleanup

# Compare results
ls -l benchmarks/
```

### Analyzing Results

Key metrics to compare:
1. **avg_cpu_util_pct**: Lower is more efficient
2. **cpu_throttled_seconds**: Should be minimal
3. **avg_memory_mb**: Should be consistent across runs
4. **cpu_seconds_per_request**: Lower means better CPU efficiency
5. **request_rate_rps**: Higher means better throughput

## Customization

### Change Benchmark Duration

```bash
python main.py --cloud gcp --machine-type n2-standard-4 --duration 1200  # 20 minutes
```

### Use Different Machine Type

```bash
# Larger instance
python main.py --cloud gcp --machine-type n2-standard-8 --duration 600

# ARM-based instance
python main.py --cloud gcp --machine-type t2a-standard-4 --cpu-vendor arm --duration 600
```

### Modify Resource Limits

Edit `kubernetes/online-boutique/values.yaml` to change CPU/memory limits for services.

### Change Load Profile

Edit `kubernetes/online-boutique/values.yaml` to modify load generator settings.

## Troubleshooting

### "Permission denied" errors

**Solution:** Verify cloud credentials are configured:
```bash
gcloud auth list
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### "Cluster already exists" error

**Solution:** Use a unique cluster name or delete existing cluster:
```bash
gcloud container clusters delete benchmark-cluster --zone us-central1-a
```

### "Pods not ready" timeout

**Solution:** Check pod status and logs:
```bash
kubectl get pods --all-namespaces
kubectl logs -n default <pod-name>
kubectl describe pod -n default <pod-name>
```

### "Prometheus query failed"

**Solution:** Verify Prometheus is running:
```bash
kubectl get pods -n monitoring
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# Visit http://localhost:9090
```

### "Insufficient resources" error

**Solution:** Increase node count or use larger machine type:
```bash
python main.py --cloud gcp --machine-type n2-standard-8 --node-count 4 --duration 600
```

## Next Steps

1. **Run Multiple Benchmarks**: Compare different machine types
2. **Analyze Trends**: Look for patterns across runs
3. **Optimize Configuration**: Adjust resource limits based on results
4. **Explore AI Agent**: See `docs/AI_AGENT_ARCHITECTURE.md` for future enhancements
5. **Customize Load**: Modify load generator for your use case

## Cost Considerations

**Estimated GCP Costs per Benchmark:**
- n2-standard-4 (3 nodes): ~$0.50/hour
- 30-minute benchmark: ~$0.25
- Daily benchmarking (4 runs): ~$1.00

**Cost-Saving Tips:**
1. Use `--cleanup` to delete resources after each run
2. Run benchmarks during off-peak hours
3. Use preemptible nodes (requires Terraform modification)
4. Delete unused benchmarks and artifacts

## Additional Resources

- [Main README](../README.md) - Project overview
- [Architecture Documentation](../docs/ARCHITECTURE.md) - System design
- [AI Agent Architecture](../docs/AI_AGENT_ARCHITECTURE.md) - Future features
- [Automation README](../automation/README.md) - Detailed automation docs
- [Terraform README](../terraform/README.md) - Infrastructure details
- [Kubernetes README](../kubernetes/README.md) - Deployment details

## Getting Help

If you encounter issues:

1. Check logs: `kubectl logs -n <namespace> <pod-name>`
2. Verify configuration: Review Terraform/Helm values
3. Test connectivity: `kubectl get pods --all-namespaces`
4. Review documentation in `docs/` directory

## Best Practices

1. **Always use version control**: Commit benchmark artifacts for history
2. **Document machine types**: Note CPU generation in metadata
3. **Consistent duration**: Use same duration for all comparable runs
4. **Monitor during runs**: Watch Grafana to verify behavior
5. **Regular cleanup**: Don't leave clusters running unnecessarily
