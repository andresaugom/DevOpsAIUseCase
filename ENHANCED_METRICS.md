# Enhanced Prometheus Metrics Collection

## Overview

The Prometheus metrics collector has been significantly enhanced to provide comprehensive, granular performance data at multiple levels: cluster-wide, per-pod, per-node, and per-service.

## Key Improvements

### 1. **Multi-Level Metrics Collection**

The enhanced collector now gathers metrics at four distinct levels:

- **Cluster-level**: Aggregate metrics across the entire cluster
- **Pod-level**: Detailed metrics for each individual pod/container
- **Node-level**: Infrastructure metrics for each Kubernetes node
- **Service-level**: Application-specific metrics for Online Boutique microservices

### 2. **Enhanced Metrics Quality**

All improvements address the following requirements:

✅ **No Null Values**: All metrics default to `0.0` instead of `null` for consistent analysis  
✅ **Per-Pod Granularity**: CPU throttling at the pod level is now visible (e.g., 300 users @ 50 RPS showing 0.2 CPU throttling)  
✅ **Machine Type Specs**: Comprehensive GCP machine type dictionary with vCPUs, memory, and platform details  
✅ **Statistical Analysis**: Mean, median, min, max, P95, P99, and standard deviation for key metrics  

### 3. **Comprehensive CPU Metrics**

#### Cluster Level
- Average CPU utilization (%)
- Maximum CPU utilization (%)
- P95 CPU utilization (%)
- P99 CPU utilization (%)
- Total throttled seconds
- Throttling percentage

#### Pod Level
- Average, min, max CPU utilization per pod
- P95, P99 CPU utilization
- Standard deviation (showing variability)
- Throttled seconds (average, max, total)
- CPU limit allocation

### 4. **Memory Metrics**

#### Cluster Level
- Average memory usage (MB)
- Maximum memory usage (MB)
- Memory utilization percentage

#### Pod Level
- Average, min, max memory usage
- P95 memory usage
- Working set bytes tracking

### 5. **Network Metrics**

- Network received (MB/sec)
- Network transmitted (MB/sec)

### 6. **Machine Type Specifications**

A comprehensive dictionary of GCP machine types including:

- **N2 Series** (Intel Ice Lake): n2-standard-{2,4,8,16,32,48,64,80}
- **N2D Series** (AMD EPYC Milan): n2d-standard-{2,4,8,16,32,48,64,80,96,128,224}
- **T2A Series** (ARM Ampere Altra): t2a-standard-{1,2,4,8,16,32,48}
- **N1 Series** (Intel Skylake/Broadwell/Haswell)
- **E2 Series** (Cost-Optimized)

Each specification includes:
- vCPUs count
- Memory (GB)
- CPU platform/generation
- Maximum network bandwidth
- Vendor information

## Artifact Structure

### JSON Artifact

The main artifact (`{run_id}.json`) now includes:

```json
{
  "run_id": "gcp-intel-20260211-143022",
  "timestamp": "2026-02-11T14:30:22",
  "cloud": "gcp",
  "region": "us-central1",
  "zone": "us-central1-a",
  
  "node_pool": {
    "machine_type": "n2-standard-4",
    "cpu_vendor": "intel",
    "cpu_generation": "Ice Lake",
    "node_count": 3,
    "machine_specs": {
      "vcpus": 4,
      "memory_gb": 16,
      "cpu_platform": "Intel Ice Lake",
      "max_bandwidth_gbps": 10
    }
  },
  
  "load_profile": {
    "duration_seconds": 600,
    "users_count": 300,
    "rps": 50,
    "start_time": "...",
    "end_time": "..."
  },
  
  "metrics": {
    "cpu": {
      "avg_utilization_pct": 45.23,
      "max_utilization_pct": 89.45,
      "p95_utilization_pct": 78.12,
      "p99_utilization_pct": 85.67,
      "throttled_seconds": 12.45,
      "throttled_percentage": 2.34
    },
    "memory": { ... },
    "network": { ... },
    "request_rate_rps": 50.2
  },
  
  "pods": [
    {
      "pod_name": "frontend-abc123",
      "container_name": "frontend",
      "metrics": {
        "cpu": {
          "avg_utilization_pct": 20.5,
          "max_utilization_pct": 95.2,
          "min_utilization_pct": 5.1,
          "p95_utilization_pct": 85.3,
          "p99_utilization_pct": 92.1,
          "std_dev": 15.4
        },
        "cpu_throttling": {
          "avg_throttled_seconds": 0.025,
          "max_throttled_seconds": 0.15,
          "total_throttled_seconds": 15.2
        },
        "memory": {
          "avg_usage_mb": 256.8,
          "max_usage_mb": 312.5,
          "min_usage_mb": 200.1,
          "p95_usage_mb": 290.3
        }
      },
      "resource_limits": {
        "cpu_limit_cores": 0.2
      }
    }
    // ... more pods
  ],
  
  "nodes": [
    {
      "node_name": "gke-cluster-pool-1-node-abc",
      "metrics": {
        "cpu": {
          "avg_utilization_pct": 55.2,
          "max_utilization_pct": 78.5,
          "min_utilization_pct": 30.1
        },
        "memory": {
          "avg_utilization_pct": 62.3,
          "max_utilization_pct": 75.8,
          "min_utilization_pct": 45.2
        }
      }
    }
    // ... more nodes
  ],
  
  "services": {
    "frontend": {
      "cpu_avg_pct": 25.3,
      "cpu_max_pct": 89.2,
      "memory_avg_mb": 280.5,
      "memory_max_mb": 350.8
    }
    // ... more services
  },
  
  "summary": {
    "total_pods": 12,
    "total_nodes": 3,
    "total_services": 10,
    "pod_cpu_stats": {
      "mean": 32.5,
      "median": 28.3,
      "max": 95.2,
      "min": 5.1
    },
    "pod_memory_stats": {
      "mean_mb": 245.7,
      "median_mb": 240.2,
      "max_mb": 350.8,
      "min_mb": 150.3
    }
  }
}
```

### CSV Artifacts

Three CSV files are generated for easy analysis:

#### 1. `cluster_summary.csv`
Aggregated cluster-level metrics with one row per benchmark run. Perfect for comparing different machine types, CPU vendors, or configurations.

**Columns include:**
- run_id, timestamp, cloud, region, zone
- machine_type, cpu_vendor, cpu_generation, vcpus, memory_gb
- duration_seconds, users_count, rps
- cpu_avg_util_pct, cpu_max_util_pct, cpu_p95_util_pct, cpu_throttled_pct
- memory_avg_mb, memory_max_mb
- network_rx_mb_per_sec, network_tx_mb_per_sec
- request_rate_rps
- cpu_seconds_per_request, memory_mb_per_request
- total_pods, total_nodes, total_services

#### 2. `{run_id}_pods.csv`
Per-pod detailed metrics. Use this to identify bottlenecks, throttling issues, and resource-constrained pods.

**Columns include:**
- run_id, pod_name, container_name
- cpu_avg_pct, cpu_max_pct, cpu_min_pct, cpu_p95_pct, cpu_p99_pct, cpu_std_dev
- cpu_throttled_avg_sec, cpu_throttled_max_sec, cpu_throttled_total_sec
- memory_avg_mb, memory_max_mb, memory_min_mb, memory_p95_mb
- cpu_limit_cores

#### 3. `{run_id}_nodes.csv`
Per-node infrastructure metrics. Use this to understand node-level resource utilization.

**Columns include:**
- run_id, node_name
- cpu_avg_pct, cpu_max_pct, cpu_min_pct
- memory_avg_util_pct, memory_max_util_pct, memory_min_util_pct

## Usage Examples

### Running a Benchmark

```bash
cd automation
python main.py \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --duration 600 \
  --users-count 300 \
  --rps 50 \
  --cleanup
```

### Output

```
Benchmark Pipeline Completed Successfully!
============================================================
Cluster: gke-benchmark-20260211
Machine Type: n2-standard-4
CPU Vendor: intel
Region: us-central1
Zone: us-central1-a
Duration: 600s
Load Profile: 300 users @ 50 RPS

Metrics Summary:
  - Pods monitored: 12
  - Nodes monitored: 3
  - Services tracked: 10
  - Avg CPU: 45.23%
  - CPU Throttling: 2.34%

Artifacts Generated:
  - Main artifact: benchmarks/gcp-intel-20260211-143022.json
  - Cluster summary: benchmarks/cluster_summary.csv
  - Per-pod metrics: benchmarks/gcp-intel-20260211-143022_pods.csv
  - Per-node metrics: benchmarks/gcp-intel-20260211-143022_nodes.csv

Grafana Dashboard: http://35.123.45.67:3000
============================================================
```

## Analyzing Results

### Identifying CPU Throttling

Look in the per-pod CSV for pods with high `cpu_throttled_total_sec`:

```bash
# Sort pods by throttling
csvlook benchmarks/*_pods.csv | grep -v "^|" | sort -t, -k10 -rn | head
```

### Finding Resource-Constrained Pods

Check for pods where `cpu_max_pct` approaches `cpu_limit_cores * 100`:

```bash
# Example: Pod with 0.2 CPU limit hitting 95% utilization
# means it's using 0.19 cores and likely throttled
```

### Comparing Machine Types

```bash
# Compare cluster summaries across different machine types
csvlook benchmarks/cluster_summary.csv | grep "n2-standard"
csvlook benchmarks/cluster_summary.csv | grep "n2d-standard"
csvlook benchmarks/cluster_summary.csv | grep "t2a-standard"
```

### Visualizing in Spreadsheet

1. Import `cluster_summary.csv` for high-level comparisons
2. Import `{run_id}_pods.csv` for detailed pod analysis
3. Create pivot tables to aggregate by service or pod name pattern
4. Plot CPU throttling vs. load profile to find breaking points

## Technical Details

### Prometheus Queries

The enhanced collector uses optimized PromQL queries:

- **CPU Utilization**: `rate(container_cpu_usage_seconds_total[5m]) * 100`
- **CPU Throttling**: `rate(container_cpu_cfs_throttled_seconds_total[5m])`
- **Memory Usage**: `container_memory_working_set_bytes / 1024 / 1024`
- **Percentiles**: Calculated from time series data in Python

### Statistical Methods

- **Percentiles**: Linear interpolation method
- **Standard Deviation**: Population standard deviation
- **Mean/Median**: Calculated from all data points in time range

### Error Handling

- All queries have timeout protection (30 seconds)
- Failed queries default to 0.0 instead of failing the entire collection
- Empty results are handled gracefully with default values
- Warnings logged for missing metrics without crashing

## Troubleshooting

### No Pod Metrics

**Symptom**: `total_pods: 0` in summary

**Solutions**:
1. Check Prometheus is scraping pod metrics: `kubectl get servicemonitors -n monitoring`
2. Verify pods are in `default` namespace: `kubectl get pods -n default`
3. Check Prometheus targets: Visit Grafana → Status → Targets

### High CPU Throttling

**Symptom**: `cpu_throttled_percentage > 5%`

**Solutions**:
1. Increase CPU limits in Online Boutique deployment
2. Reduce load (decrease `--users-count` or `--rps`)
3. Use larger machine type (more vCPUs per node)

### Memory Metrics Missing

**Symptom**: `memory_avg_mb: 0.0` for all pods

**Solutions**:
1. Check cAdvisor is running: `kubectl get pods -n kube-system | grep cadvisor`
2. Verify memory metrics in Prometheus: Query `container_memory_working_set_bytes`
3. Wait 2-3 minutes after deployment for metrics to populate

## Future Enhancements

- [ ] Add disk I/O metrics per pod
- [ ] Include network metrics per pod (RX/TX bytes)
- [ ] Implement cost estimation based on machine specs
- [ ] Add automated anomaly detection (e.g., sudden CPU spikes)
- [ ] Generate HTML reports with charts
- [ ] Add comparison mode to diff two benchmark runs

## Files Modified

- `automation/modules/prometheus_client.py` - Enhanced metrics collection
- `automation/modules/artifact_generator.py` - Multi-level artifact generation
- `automation/modules/machine_specs.py` - GCP machine type specifications (NEW)
- `automation/main.py` - Integration and improved logging

## References

- [Prometheus Query Examples](https://prometheus.io/docs/prometheus/latest/querying/examples/)
- [Kubernetes Monitoring Architecture](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-metrics-pipeline/)
- [GCP Machine Types](https://cloud.google.com/compute/docs/machine-types)
- [Online Boutique Microservices](https://github.com/GoogleCloudPlatform/microservices-demo)
