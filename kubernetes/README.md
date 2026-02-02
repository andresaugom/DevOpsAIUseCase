# Kubernetes Configurations

This directory contains Kubernetes manifests and Helm values files for deploying the Online Boutique application and monitoring stack.

## Directory Structure

```
kubernetes/
├── online-boutique/          # Online Boutique application
│   └── values.yaml          # Helm values for consistent benchmarking
└── monitoring/              # Monitoring stack
    └── prometheus-values.yaml  # Prometheus + Grafana configuration
```

## Online Boutique Deployment

The Online Boutique is deployed using the official Helm chart with custom resource requests and limits for reproducible benchmarks.

### Install Online Boutique

```bash
# Add the Helm repository
helm repo add google-samples https://googlecloudplatform.github.io/microservices-demo
helm repo update

# Install with custom values
helm install online-boutique google-samples/online-boutique \
  --namespace default \
  --values kubernetes/online-boutique/values.yaml \
  --create-namespace
```

### Verify Deployment

```bash
kubectl get pods
kubectl get services
```

The frontend service will be exposed via LoadBalancer. Get the external IP:

```bash
kubectl get service frontend-external
```

## Monitoring Stack Deployment

The monitoring stack includes Prometheus and Grafana deployed via the kube-prometheus-stack Helm chart.

### Install Prometheus + Grafana

```bash
# Add the Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install with custom values
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values kubernetes/monitoring/prometheus-values.yaml \
  --create-namespace
```

### Access Grafana

Get the Grafana service external IP:

```bash
kubectl get service -n monitoring prometheus-grafana
```

Default credentials (change in production):
- Username: `admin`
- Password: `admin`

### Access Prometheus

Port-forward to access Prometheus UI:

```bash
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
```

Then visit: http://localhost:9090

## Resource Configuration

All services have fixed resource requests and limits to ensure reproducible benchmark results:

### Online Boutique Services
- Frontend: 100m CPU, 64Mi RAM (request)
- Cart Service: 200m CPU, 64Mi RAM (request)
- Checkout Service: 100m CPU, 64Mi RAM (request)
- And more... (see values.yaml)

### Load Generator
- Enabled by default
- 300m CPU, 256Mi RAM (request)

## Node Affinity

All Online Boutique pods are scheduled on nodes with the `workload: benchmark` label to ensure they run on the benchmark node pool.

## Service Monitors

Prometheus automatically discovers and scrapes metrics from:
- Kubernetes API server
- Kubelet
- cAdvisor (container metrics)
- Node exporter
- Kube-state-metrics
- Online Boutique services (if they expose /metrics)

## Useful PromQL Queries

### CPU Usage by Container
```promql
rate(container_cpu_usage_seconds_total{namespace="default"}[5m])
```

### Memory Usage by Container
```promql
container_memory_working_set_bytes{namespace="default"}
```

### Request Rate
```promql
rate(http_requests_total[5m])
```

## Cleanup

```bash
helm uninstall online-boutique
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```
