# Quick Reference Card

## 🐳 Docker Commands (Recommended)

### Build Docker Image
```bash
docker build -t devops-benchmark:latest .
```

### Run Benchmark with Docker
```bash
# Using wrapper script (easiest)
export GCP_PROJECT_ID="your-project-id"
./benchmark.sh gcp n2-standard-4 600 --cleanup

# Using Docker directly
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600 --cleanup
```

### Docker Compose
```bash
docker-compose build
docker-compose run --rm devops-benchmark --cloud gcp --machine-type n2-standard-4 --duration 600
```

### Docker Shell (Debugging)
```bash
./benchmark.sh gcp n2-standard-4 600 --shell
# or
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  /bin/bash
```

---

## Essential Commands

### Run a Complete Benchmark
```bash
cd automation
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --cpu-generation "Ice Lake" \
  --duration 600 \
  --cleanup
```

### Machine Type Quick Reference

#### GCP
| Machine Type | CPU Vendor | CPU Generation | Cores | RAM |
|-------------|-----------|---------------|-------|-----|
| n2-standard-4 | Intel | Ice Lake | 4 | 16GB |
| n2-standard-8 | Intel | Ice Lake | 8 | 32GB |
| n2d-standard-4 | AMD | EPYC Milan | 4 | 16GB |
| n2d-standard-8 | AMD | EPYC Milan | 8 | 32GB |
| t2a-standard-4 | ARM | Ampere Altra | 4 | 16GB |
| t2a-standard-8 | ARM | Ampere Altra | 8 | 16GB |

#### AWS (Future)
| Instance Type | CPU Vendor | CPU Generation |
|--------------|-----------|---------------|
| m6i.xlarge | Intel | Ice Lake |
| m6a.xlarge | AMD | EPYC 3rd Gen |
| m7g.xlarge | ARM | Graviton3 |

#### Azure (Future)
| VM Size | CPU Vendor | CPU Generation |
|---------|-----------|---------------|
| Standard_D4s_v5 | Intel | Ice Lake |
| Standard_D4as_v4 | AMD | EPYC Milan |
| Standard_D4ps_v5 | ARM | Ampere Altra |

### Common Use Cases

#### Test Intel vs AMD
```bash
# Intel
python main.py --cloud gcp --machine-type n2-standard-4 --cpu-vendor intel --duration 600 --cleanup

# AMD
python main.py --cloud gcp --machine-type n2d-standard-4 --cpu-vendor amd --duration 600 --cleanup
```

#### Use Existing Cluster
```bash
python main.py --cloud gcp --machine-type n2-standard-4 --duration 600 --skip-provision
```

#### Cleanup Only
```bash
python main.py --cloud gcp --cleanup-only
```

### Kubernetes Commands

#### Check Pod Status
```bash
kubectl get pods --all-namespaces
kubectl get pods -n default
kubectl get pods -n monitoring
```

#### View Logs
```bash
kubectl logs -n default <pod-name>
kubectl logs -n monitoring prometheus-operated-0
```

#### Access Grafana
```bash
# Get external IP
kubectl get svc -n monitoring prometheus-grafana

# Or port-forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
# Visit http://localhost:3000 (admin/admin)
```

#### Access Prometheus
```bash
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# Visit http://localhost:9090
```

### Viewing Results

#### List Benchmarks
```bash
ls -lh benchmarks/
```

#### View JSON Result
```bash
cat benchmarks/gcp-intel-*.json | python -m json.tool
```

#### Open CSV in Excel
```bash
open benchmarks/gcp-intel-*.csv
# or
libreoffice benchmarks/gcp-intel-*.csv
```

### Terraform Commands

#### Initialize
```bash
cd terraform/gcp
terraform init
```

#### Plan
```bash
terraform plan
```

#### Apply
```bash
terraform apply
```

#### Destroy
```bash
terraform destroy
```

#### Show State
```bash
terraform show
```

### Environment Setup

#### GCP
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
export GCP_PROJECT_ID=your-project-id
gcloud auth application-default login
gcloud config set project your-project-id
```

#### AWS (Future)
```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-west-2
```

#### Azure (Future)
```bash
az login
export AZURE_SUBSCRIPTION_ID=your-subscription-id
```

### Troubleshooting

#### Check Terraform State
```bash
cd terraform/gcp
terraform state list
terraform output
```

#### Verify kubectl Context
```bash
kubectl config current-context
kubectl cluster-info
```

#### Force Delete Stuck Pods
```bash
kubectl delete pod <pod-name> -n <namespace> --grace-period=0 --force
```

#### Check Node Resources
```bash
kubectl top nodes
kubectl top pods -n default
```

#### View Events
```bash
kubectl get events -n default --sort-by='.lastTimestamp'
```

### Cost Management

#### Estimate Costs
- n2-standard-4: ~$0.17/hour (GCP)
- 3 nodes: ~$0.50/hour
- 1-hour benchmark: ~$0.50

#### Always Cleanup
```bash
# Use --cleanup flag
python main.py --cloud gcp --machine-type n2-standard-4 --duration 600 --cleanup

# Or cleanup manually
python main.py --cloud gcp --cleanup-only
```

### File Locations

| What | Where |
|------|-------|
| Benchmark results | `benchmarks/*.json`, `benchmarks/*.csv` |
| Terraform state | `terraform/gcp/.terraform/` |
| Python logs | Console output |
| Kubernetes configs | `~/.kube/config` |
| Cloud credentials | `~/.config/gcloud/` (GCP) |
| **Docker files** | `Dockerfile`, `.dockerignore`, `docker-compose.yml` |
| **Docker wrapper** | `benchmark.sh` |
| **Docker docs** | `docs/DOCKER.md` |

### Metrics Reference

| Metric | Good Value | Units |
|--------|-----------|-------|
| avg_cpu_util_pct | 40-80 | % |
| p95_cpu_util_pct | < 90 | % |
| cpu_throttled_seconds | < 30 (5%) | seconds |
| avg_memory_mb | Varies | MB |
| request_rate_rps | > 100 | req/sec |
| cpu_seconds_per_request | Lower is better | seconds |

### Documentation Links

| Topic | File |
|-------|------|
| **Docker Usage** | `docs/DOCKER.md` |
| Quick Start | `docs/GETTING_STARTED.md` |
| Architecture | `docs/ARCHITECTURE.md` |
| AI Agent Design | `docs/AI_AGENT_ARCHITECTURE.md` |
| Implementation Status | `docs/IMPLEMENTATION.md` |
| Project Overview | `PROJECT_OVERVIEW.md` |
| Terraform Guide | `terraform/README.md` |
| Kubernetes Guide | `kubernetes/README.md` |
| Automation Guide | `automation/README.md` |

### Support

1. Check documentation in `docs/`
2. Review module READMEs
3. Check logs: `kubectl logs <pod>`
4. Verify configuration files
5. Test connectivity: `kubectl get pods --all-namespaces`

---

**Print this card and keep it handy!**
