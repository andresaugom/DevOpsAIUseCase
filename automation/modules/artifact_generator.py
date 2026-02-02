"""
Artifact Generator Module

Generates and saves benchmark artifacts in JSON/CSV format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class ArtifactGenerator:
    """Generates benchmark artifacts"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(__file__).parent.parent.parent / 'benchmarks'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, cluster_info, metrics, benchmark_results):
        """
        Generate benchmark artifact.
        
        Args:
            cluster_info: Information about the cluster
            metrics: Collected metrics from Prometheus
            benchmark_results: Benchmark execution results
            
        Returns:
            Dictionary representing the benchmark artifact
        """
        logger.info("Generating benchmark artifact...")
        
        # Calculate normalized metrics
        request_rate = metrics.get('request_rate') or 0
        cpu_seconds_per_request = None
        memory_per_request = None
        
        if request_rate > 0:
            avg_cpu = metrics.get('avg_cpu_utilization') or 0
            avg_memory = metrics.get('avg_memory') or 0
            
            # CPU seconds per request = (CPU utilization % / 100) * duration / total_requests
            total_requests = request_rate * benchmark_results['duration']
            if total_requests > 0:
                cpu_seconds_per_request = (avg_cpu / 100) * benchmark_results['duration'] / total_requests
                memory_per_request = avg_memory / request_rate
        
        artifact = {
            'run_id': self.config['run_id'],
            'timestamp': datetime.now().isoformat(),
            'cloud': self.config['cloud'],
            'region': cluster_info.get('region', 'unknown'),
            'zone': cluster_info.get('zone', 'unknown'),
            'node_pool': {
                'machine_type': self.config['machine_type'],
                'cpu_vendor': self.config['cpu_vendor'],
                'cpu_generation': self.config['cpu_generation'],
                'node_count': self.config['node_count'],
                'source': 'configuration'
            },
            'load_profile': {
                'duration_seconds': benchmark_results['duration'],
                'start_time': benchmark_results['start_time'].isoformat(),
                'end_time': benchmark_results['end_time'].isoformat(),
            },
            'metrics': {
                'avg_cpu_util_pct': round(metrics.get('avg_cpu_utilization') or 0, 2),
                'p95_cpu_util_pct': round(metrics.get('p95_cpu_utilization') or 0, 2),
                'cpu_throttled_seconds': round(metrics.get('cpu_throttled') or 0, 2),
                'avg_memory_mb': round(metrics.get('avg_memory') or 0, 2),
                'request_rate_rps': round(request_rate, 2),
            },
            'normalized_metrics': {
                'cpu_seconds_per_request': round(cpu_seconds_per_request, 6) if cpu_seconds_per_request else None,
                'memory_mb_per_request': round(memory_per_request, 6) if memory_per_request else None,
            }
        }
        
        return artifact
    
    def save_artifact(self, artifact):
        """
        Save artifact to JSON file.
        
        Args:
            artifact: Benchmark artifact dictionary
            
        Returns:
            Path to saved artifact
        """
        filename = f"{artifact['run_id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(artifact, f, indent=2)
        
        logger.info(f"Artifact saved to {filepath}")
        
        # Also save as CSV for easy comparison
        self._save_as_csv(artifact)
        
        return str(filepath)
    
    def _save_as_csv(self, artifact):
        """Save artifact as CSV for easy spreadsheet import"""
        import csv
        
        csv_file = self.output_dir / f"{artifact['run_id']}.csv"
        
        # Flatten the artifact for CSV
        row = {
            'run_id': artifact['run_id'],
            'timestamp': artifact['timestamp'],
            'cloud': artifact['cloud'],
            'region': artifact['region'],
            'zone': artifact['zone'],
            'machine_type': artifact['node_pool']['machine_type'],
            'cpu_vendor': artifact['node_pool']['cpu_vendor'],
            'cpu_generation': artifact['node_pool']['cpu_generation'],
            'node_count': artifact['node_pool']['node_count'],
            'duration_seconds': artifact['load_profile']['duration_seconds'],
            'avg_cpu_util_pct': artifact['metrics']['avg_cpu_util_pct'],
            'p95_cpu_util_pct': artifact['metrics']['p95_cpu_util_pct'],
            'cpu_throttled_seconds': artifact['metrics']['cpu_throttled_seconds'],
            'avg_memory_mb': artifact['metrics']['avg_memory_mb'],
            'request_rate_rps': artifact['metrics']['request_rate_rps'],
            'cpu_seconds_per_request': artifact['normalized_metrics']['cpu_seconds_per_request'],
            'memory_mb_per_request': artifact['normalized_metrics']['memory_mb_per_request'],
        }
        
        # Check if file exists to determine if we need headers
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(row)
        
        logger.info(f"CSV saved to {csv_file}")
