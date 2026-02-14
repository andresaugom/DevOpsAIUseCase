# Migration Guide - Enhanced Metrics

## For Existing Users

If you've been using the benchmark pipeline before these enhancements, here's what you need to know:

## ✅ Backward Compatibility

**Good news**: Your existing scripts and workflows will continue to work!

- All existing command-line arguments work the same way
- The main JSON artifact structure is enhanced but backward compatible
- Existing cluster-level metrics are still available under `metrics['cluster']`

## 🆕 What's New

### 1. Additional Files Generated

**Before** (per benchmark run):
```
benchmarks/
  └── gcp-intel-20260211-143022.json
  └── gcp-intel-20260211-143022.csv
```

**After** (per benchmark run):
```
benchmarks/
  ├── gcp-intel-20260211-143022.json          # Enhanced with pod/node data
  ├── cluster_summary.csv                      # NEW: Aggregated summary (all runs)
  ├── gcp-intel-20260211-143022_pods.csv      # NEW: Per-pod metrics
  └── gcp-intel-20260211-143022_nodes.csv     # NEW: Per-node metrics
```

### 2. Enhanced JSON Structure

**Old JSON** (still available):
```json
{
  "metrics": {
    "avg_cpu_util_pct": 45.2,
    "p95_cpu_util_pct": 78.1,
    ...
  }
}
```

**New JSON** (enhanced):
```json
{
  "metrics": {
    "cpu": {
      "avg_utilization_pct": 45.2,  // Same value, nested structure
      "max_utilization_pct": 89.4,  // NEW
      "p95_utilization_pct": 78.1,  // Same as before
      "p99_utilization_pct": 85.6,  // NEW
      ...
    },
    "memory": { ... }
  },
  "pods": [...],      // NEW: Detailed per-pod metrics
  "nodes": [...],     // NEW: Per-node metrics
  "services": {...}   // NEW: Per-service aggregates
}
```

### 3. Command-Line Enhancements

**Optional improvements** (not required):

```bash
# Before: Had to specify CPU vendor/generation manually
python main.py --cloud gcp --machine-type n2-standard-4 \
  --cpu-vendor intel --cpu-generation "Ice Lake" \
  --duration 600

# After: Auto-detected from machine type (but old way still works!)
python main.py --cloud gcp --machine-type n2-standard-4 \
  --duration 600  # cpu-vendor and cpu-generation optional now
```

## 📊 Accessing Old Metrics

If your existing analysis scripts rely on the old structure, you can still access everything:

### Python Example

```python
import json

# Load artifact
with open('benchmarks/gcp-intel-20260211-143022.json') as f:
    artifact = json.load(f)

# OLD WAY (still works with cluster-level metrics)
avg_cpu = artifact['metrics']['cluster']['avg_cpu_utilization']
p95_cpu = artifact['metrics']['cluster']['p95_cpu_utilization']

# NEW WAY (more organized)
avg_cpu = artifact['metrics']['cpu']['avg_utilization_pct']
p95_cpu = artifact['metrics']['cpu']['p95_utilization_pct']

# NEW FEATURES (per-pod analysis)
for pod in artifact['pods']:
    print(f"{pod['pod_name']}: {pod['metrics']['cpu']['avg_utilization_pct']}%")
```

### CSV Analysis

```bash
# OLD CSV (still generated as cluster_summary.csv)
cat benchmarks/cluster_summary.csv | csvlook

# NEW CSVs (additional granularity)
cat benchmarks/*_pods.csv | csvlook    # Per-pod details
cat benchmarks/*_nodes.csv | csvlook   # Per-node details
```

## 🔄 Updated Fields

Some metrics have been renamed for consistency:

| Old Name | New Location | Notes |
|----------|-------------|-------|
| `metrics.avg_cpu_util_pct` | `metrics.cpu.avg_utilization_pct` | Same value |
| `metrics.p95_cpu_util_pct` | `metrics.cpu.p95_utilization_pct` | Same value |
| `metrics.cpu_throttled_seconds` | `metrics.cpu.throttled_seconds` | Same value |
| `metrics.avg_memory_mb` | `metrics.memory.avg_usage_mb` | Same value |

**For CSV**: `cluster_summary.csv` uses the old flat column names for compatibility.

## ⚠️ Breaking Changes

### None! 

All changes are additive. The only thing to note:

1. **Additional files**: 3 CSVs instead of 1 per run
2. **JSON structure**: Nested but backward-compatible via `metrics['cluster']`
3. **Null values**: Now default to `0.0` instead of `null` (better for analysis)

## 🚀 Recommended Migration Steps

### Step 1: Update Your Scripts (Optional)

If you want to take advantage of new features:

```python
# OLD: Simple average across cluster
avg_cpu = artifact['metrics']['avg_cpu_util_pct']

# NEW: Access per-pod details
throttled_pods = [
    pod for pod in artifact['pods']
    if pod['metrics'].get('cpu_throttling', {}).get('total_throttled_seconds', 0) > 10
]
print(f"Found {len(throttled_pods)} throttled pods")
```

### Step 2: Update Your Analysis

Add new CSVs to your analysis workflow:

```bash
# Import to spreadsheet
# 1. cluster_summary.csv - For cross-run comparison (like before)
# 2. *_pods.csv - For detailed pod analysis (NEW)
# 3. *_nodes.csv - For node-level infrastructure view (NEW)
```

### Step 3: Enjoy Enhanced Insights

No changes required - just run your benchmarks as before and get:
- ✅ No null values
- ✅ Per-pod CPU throttling visibility
- ✅ Machine type specs automatically included
- ✅ Statistical summaries (P99, std_dev, etc.)

## 💾 Storage Considerations

**Before**: 1 file per run (JSON + CSV)
```
~20KB per run
```

**After**: 4 files per run (JSON + 3 CSVs)
```
~50-100KB per run (depending on pod count)
```

For 100 benchmark runs: ~5-10MB total (negligible)

## 🆘 Troubleshooting

### "My existing scripts are broken!"

If you were accessing metrics directly:

```python
# If this fails
avg_cpu = artifact['metrics']['avg_cpu_util_pct']

# Try this (cluster-level aggregate)
avg_cpu = artifact['metrics']['cluster']['avg_cpu_utilization']

# Or this (new structure)
avg_cpu = artifact['metrics']['cpu']['avg_utilization_pct']
```

### "I don't see the new CSV files"

Make sure you're running the updated code:

```bash
cd /home/andresgomez31/DevOpsAIUseCase
git pull  # or copy the new files
cd automation
python main.py --cloud gcp --machine-type n2-standard-4 --duration 300
ls -lh ../benchmarks/  # Check for *_pods.csv and *_nodes.csv
```

### "CSV has too many columns now"

The main summary CSV (`cluster_summary.csv`) has additional columns but retains all old ones. To view only old columns:

```bash
csvcut -c run_id,timestamp,machine_type,cpu_avg_util_pct,cpu_throttled_seconds \
  benchmarks/cluster_summary.csv | csvlook
```

## 📚 Further Reading

- [ENHANCED_METRICS.md](ENHANCED_METRICS.md) - Full documentation of new features
- [ENHANCEMENT_SUMMARY.md](ENHANCEMENT_SUMMARY.md) - Technical implementation details
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Overall project documentation

## ✅ Quick Test

Test that everything works:

```bash
cd automation

# Run a short test (5 minutes)
python main.py --cloud gcp --machine-type n2-standard-4 --duration 300 --cleanup

# Verify outputs
ls -lh ../benchmarks/

# Expected files:
# - {run_id}.json (enhanced JSON)
# - cluster_summary.csv (all runs)
# - {run_id}_pods.csv (this run's pods)
# - {run_id}_nodes.csv (this run's nodes)
```

If all 4 files are generated, you're good to go! 🎉
