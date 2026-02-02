# Sample Benchmark Result

This is an example of what a benchmark result looks like.

## JSON Format

```json
{
  "run_id": "gcp-intel-20260201-143022",
  "timestamp": "2026-02-01T14:30:22.123456",
  "cloud": "gcp",
  "region": "us-central1",
  "zone": "us-central1-a",
  "node_pool": {
    "machine_type": "n2-standard-4",
    "cpu_vendor": "intel",
    "cpu_generation": "Ice Lake",
    "node_count": 3,
    "source": "configuration"
  },
  "load_profile": {
    "duration_seconds": 600,
    "start_time": "2026-02-01T14:20:22.123456",
    "end_time": "2026-02-01T14:30:22.123456"
  },
  "metrics": {
    "avg_cpu_util_pct": 63.2,
    "p95_cpu_util_pct": 81.4,
    "cpu_throttled_seconds": 12.7,
    "avg_memory_mb": 1240.5,
    "request_rate_rps": 125.3
  },
  "normalized_metrics": {
    "cpu_seconds_per_request": 0.018,
    "memory_mb_per_request": 9.89
  }
}
```

## CSV Format

| Column | Example Value | Description |
|--------|---------------|-------------|
| run_id | gcp-intel-20260201-143022 | Unique identifier |
| timestamp | 2026-02-01T14:30:22 | When benchmark completed |
| cloud | gcp | Cloud provider |
| region | us-central1 | Cloud region |
| zone | us-central1-a | Availability zone |
| machine_type | n2-standard-4 | Machine/instance type |
| cpu_vendor | intel | CPU vendor |
| cpu_generation | Ice Lake | CPU generation |
| node_count | 3 | Number of nodes |
| duration_seconds | 600 | Benchmark duration |
| avg_cpu_util_pct | 63.2 | Average CPU usage % |
| p95_cpu_util_pct | 81.4 | 95th percentile CPU % |
| cpu_throttled_seconds | 12.7 | CPU throttling |
| avg_memory_mb | 1240.5 | Average memory MB |
| request_rate_rps | 125.3 | Requests per second |
| cpu_seconds_per_request | 0.018 | Normalized CPU efficiency |
| memory_mb_per_request | 9.89 | Normalized memory efficiency |

## Interpreting Results

### Key Metrics

**CPU Utilization (avg_cpu_util_pct)**
- Lower values indicate more efficient CPU usage
- Compare across different CPU vendors/generations
- Typical range: 40-80%

**P95 CPU Utilization (p95_cpu_util_pct)**
- Shows peak CPU usage under load
- Should be below 90% to avoid saturation
- High values may indicate need for more resources

**CPU Throttling (cpu_throttled_seconds)**
- Time spent throttled due to CPU limits
- Should be minimal (< 5% of duration)
- High values indicate insufficient CPU allocation

**Memory Usage (avg_memory_mb)**
- Should be consistent across comparable runs
- Compare to resource limits in Kubernetes
- Watch for memory leaks (increasing over time)

**Request Rate (request_rate_rps)**
- Higher is better (more throughput)
- Should be consistent across runs
- Varies based on load generator configuration

### Normalized Metrics

**CPU Seconds per Request**
- Measures CPU efficiency per request
- Lower is better
- Compare across different CPU types

**Memory MB per Request**
- Measures memory efficiency per request
- Should be relatively constant
- Helps identify memory-intensive workloads

## Comparison Example

### Intel Ice Lake vs AMD Milan

| Metric | Intel (n2-standard-4) | AMD (n2d-standard-4) | Winner |
|--------|----------------------|---------------------|---------|
| Avg CPU % | 63.2 | 58.7 | AMD (lower usage) |
| P95 CPU % | 81.4 | 76.3 | AMD (better peak) |
| CPU/request | 0.018 | 0.016 | AMD (more efficient) |
| Memory MB | 1240 | 1235 | Tie (similar) |
| RPS | 125.3 | 132.1 | AMD (higher throughput) |

**Conclusion:** In this example, AMD Milan shows better performance and efficiency.
