"""
Artifact Generator Module

Generates and saves enhanced benchmark artifacts in JSON/CSV format with per-pod/node metrics.
"""

import json
import logging
import csv
from datetime import datetime
from pathlib import Path
from modules.machine_specs import enrich_cluster_info

logger = logging.getLogger(__name__)


class ArtifactGenerator:
    """Generates enhanced benchmark artifacts with comprehensive metrics"""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path(__file__).parent.parent.parent / 'benchmarks'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(self, cluster_info, metrics, benchmark_results):
        """
        Generate enhanced benchmark artifact with per-pod and per-node metrics.
        
        Args:
            cluster_info: Information about the cluster
            metrics: Enhanced metrics from Prometheus (with cluster, pods, nodes, services)
            benchmark_results: Benchmark execution results
            
        Returns:
            Dictionary representing the comprehensive benchmark artifact
        """
        logger.info("Generating enhanced benchmark artifact...")
        
        # Enrich cluster info with machine specs
        cluster_info = enrich_cluster_info(cluster_info, self.config)
        
        # Extract cluster-level metrics (backward compatible)
        cluster_metrics = metrics.get('cluster', {})
        
        # Calculate normalized metrics
        request_rate = self._safe_value(cluster_metrics.get('request_rate_rps'), 0.0)
        duration = benchmark_results['duration']
        
        cpu_seconds_per_request = None
        memory_per_request = None
        
        if request_rate > 0:
            avg_cpu = self._safe_value(cluster_metrics.get('avg_cpu_utilization'), 0.0)
            avg_memory = self._safe_value(cluster_metrics.get('avg_memory_mb'), 0.0)
            
            total_requests = request_rate * duration
            if total_requests > 0:
                cpu_seconds_per_request = (avg_cpu / 100) * duration / total_requests
                memory_per_request = avg_memory / request_rate
        
        # Build comprehensive artifact
        artifact = {
            'run_id': self.config['run_id'],
            'timestamp': datetime.now().isoformat(),
            'cloud': self.config['cloud'],
            'region': cluster_info.get('region', 'unknown'),
            'zone': cluster_info.get('zone', 'unknown'),
            
            # Enhanced node pool information with machine specs
            'node_pool': {
                'machine_type': self.config['machine_type'],
                'cpu_vendor': cluster_info.get('cpu_vendor', self.config.get('cpu_vendor', 'unknown')),
                'cpu_generation': cluster_info.get('cpu_generation', self.config.get('cpu_generation', 'unknown')),
                'node_count': self.config.get('node_count', 1),
                'source': 'configuration',
                'machine_specs': cluster_info.get('machine_specs', {
                    'vcpus': 'unknown',
                    'memory_gb': 'unknown',
                    'cpu_platform': 'unknown',
                })
            },
            
            # Load profile
            'load_profile': {
                'duration_seconds': duration,
                'start_time': benchmark_results['start_time'].isoformat(),
                'end_time': benchmark_results['end_time'].isoformat(),
                'users_count': self.config.get('users_count', 'unknown'),
                'rps': self.config.get('rps', 'unknown'),
            },
            
            # Cluster-wide aggregate metrics
            'metrics': {
                'cpu': {
                    'avg_utilization_pct': self._safe_value(cluster_metrics.get('avg_cpu_utilization'), 0.0),
                    'max_utilization_pct': self._safe_value(cluster_metrics.get('max_cpu_utilization'), 0.0),
                    'p95_utilization_pct': self._safe_value(cluster_metrics.get('p95_cpu_utilization'), 0.0),
                    'p99_utilization_pct': self._safe_value(cluster_metrics.get('p99_cpu_utilization'), 0.0),
                    'throttled_seconds': self._safe_value(cluster_metrics.get('cpu_throttled_seconds'), 0.0),
                    'throttled_percentage': self._safe_value(cluster_metrics.get('cpu_throttled_percentage'), 0.0),
                },
                'memory': {
                    'avg_usage_mb': self._safe_value(cluster_metrics.get('avg_memory_mb'), 0.0),
                    'max_usage_mb': self._safe_value(cluster_metrics.get('max_memory_mb'), 0.0),
                    'avg_utilization_pct': self._safe_value(cluster_metrics.get('avg_memory_utilization_pct'), 0.0),
                },
                'network': {
                    'received_mb_per_sec': self._safe_value(cluster_metrics.get('total_network_received_mb'), 0.0),
                    'transmitted_mb_per_sec': self._safe_value(cluster_metrics.get('total_network_transmitted_mb'), 0.0),
                },
                'request_rate_rps': self._safe_value(request_rate, 0.0),
            },
            
            # Normalized performance metrics
            'normalized_metrics': {
                'cpu_seconds_per_request': round(cpu_seconds_per_request, 6) if cpu_seconds_per_request else 0.0,
                'memory_mb_per_request': round(memory_per_request, 6) if memory_per_request else 0.0,
            },
            
            # Per-pod detailed metrics
            'pods': self._format_pod_metrics(metrics.get('pods', [])),
            
            # Per-node metrics
            'nodes': metrics.get('nodes', []),
            
            # Service-level metrics
            'services': metrics.get('services', {}),
            
            # Summary statistics
            'summary': metrics.get('summary', {}),
            
            # Collection metadata
            'collection_metadata': metrics.get('collection_metadata', {})
        }
        
        logger.info(f"Artifact generated with {len(artifact['pods'])} pods and {len(artifact['nodes'])} nodes")
        
        return artifact
    
    def _format_pod_metrics(self, pods):
        """Format and validate pod metrics"""
        formatted_pods = []
        
        for pod in pods:
            formatted_pod = {
                'pod_name': pod.get('pod_name', 'unknown'),
                'container_name': pod.get('container_name', 'unknown'),
                'metrics': {}
            }
            
            # Extract and validate metrics
            pod_metrics = pod.get('metrics', {})
            
            if 'cpu' in pod_metrics:
                formatted_pod['metrics']['cpu'] = {
                    'avg_utilization_pct': self._safe_value(pod_metrics['cpu'].get('avg_utilization_pct'), 0.0),
                    'max_utilization_pct': self._safe_value(pod_metrics['cpu'].get('max_utilization_pct'), 0.0),
                    'min_utilization_pct': self._safe_value(pod_metrics['cpu'].get('min_utilization_pct'), 0.0),
                    'p95_utilization_pct': self._safe_value(pod_metrics['cpu'].get('p95_utilization_pct'), 0.0),
                    'p99_utilization_pct': self._safe_value(pod_metrics['cpu'].get('p99_utilization_pct'), 0.0),
                    'std_dev': self._safe_value(pod_metrics['cpu'].get('std_dev'), 0.0),
                }
            
            if 'cpu_throttling' in pod_metrics:
                formatted_pod['metrics']['cpu_throttling'] = {
                    'avg_throttled_seconds': self._safe_value(pod_metrics['cpu_throttling'].get('avg_throttled_seconds'), 0.0),
                    'max_throttled_seconds': self._safe_value(pod_metrics['cpu_throttling'].get('max_throttled_seconds'), 0.0),
                    'total_throttled_seconds': self._safe_value(pod_metrics['cpu_throttling'].get('total_throttled_seconds'), 0.0),
                }
            
            if 'memory' in pod_metrics:
                formatted_pod['metrics']['memory'] = {
                    'avg_usage_mb': self._safe_value(pod_metrics['memory'].get('avg_usage_mb'), 0.0),
                    'max_usage_mb': self._safe_value(pod_metrics['memory'].get('max_usage_mb'), 0.0),
                    'min_usage_mb': self._safe_value(pod_metrics['memory'].get('min_usage_mb'), 0.0),
                    'p95_usage_mb': self._safe_value(pod_metrics['memory'].get('p95_usage_mb'), 0.0),
                }
            
            if 'resource_limits' in pod:
                formatted_pod['resource_limits'] = pod['resource_limits']
            
            formatted_pods.append(formatted_pod)
        
        return formatted_pods
    
    def _safe_value(self, value, default=0.0):
        """Ensure value is not None and round if numeric"""
        if value is None:
            return default
        try:
            return round(float(value), 4)
        except (ValueError, TypeError):
            return default
    
    def save_artifact(self, artifact):
        """
        Save artifact to JSON file.
        
        Args:
            artifact: Comprehensive benchmark artifact dictionary
            
        Returns:
            Path to saved artifact
        """
        filename = f"{artifact['run_id']}.json"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(artifact, f, indent=2)
        
        logger.info(f"Artifact saved to {filepath}")
        
        # Also save as CSV for easy comparison (cluster-level summary)
        self._save_cluster_summary_csv(artifact)
        
        # Save per-pod metrics to separate CSV for detailed analysis
        self._save_pod_metrics_csv(artifact)
        
        # Save per-node metrics to separate CSV
        self._save_node_metrics_csv(artifact)
        
        return str(filepath)
    
    def _save_cluster_summary_csv(self, artifact):
        """Save cluster-level summary as CSV for easy spreadsheet import"""
        csv_file = self.output_dir / 'cluster_summary.csv'
        
        # Flatten the artifact for CSV (cluster-level metrics only)
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
            'vcpus': artifact['node_pool']['machine_specs'].get('vcpus', 'unknown'),
            'memory_gb': artifact['node_pool']['machine_specs'].get('memory_gb', 'unknown'),
            'duration_seconds': artifact['load_profile']['duration_seconds'],
            'users_count': artifact['load_profile'].get('users_count', 'unknown'),
            'rps': artifact['load_profile'].get('rps', 'unknown'),
            
            # CPU metrics
            'cpu_avg_util_pct': artifact['metrics']['cpu']['avg_utilization_pct'],
            'cpu_max_util_pct': artifact['metrics']['cpu']['max_utilization_pct'],
            'cpu_p95_util_pct': artifact['metrics']['cpu']['p95_utilization_pct'],
            'cpu_p99_util_pct': artifact['metrics']['cpu']['p99_utilization_pct'],
            'cpu_throttled_seconds': artifact['metrics']['cpu']['throttled_seconds'],
            'cpu_throttled_pct': artifact['metrics']['cpu']['throttled_percentage'],
            
            # Memory metrics
            'memory_avg_mb': artifact['metrics']['memory']['avg_usage_mb'],
            'memory_max_mb': artifact['metrics']['memory']['max_usage_mb'],
            'memory_avg_util_pct': artifact['metrics']['memory']['avg_utilization_pct'],
            
            # Network metrics
            'network_rx_mb_per_sec': artifact['metrics']['network']['received_mb_per_sec'],
            'network_tx_mb_per_sec': artifact['metrics']['network']['transmitted_mb_per_sec'],
            
            # Request rate
            'request_rate_rps': artifact['metrics']['request_rate_rps'],
            
            # Normalized metrics
            'cpu_seconds_per_request': artifact['normalized_metrics']['cpu_seconds_per_request'],
            'memory_mb_per_request': artifact['normalized_metrics']['memory_mb_per_request'],
            
            # Summary stats
            'total_pods': artifact['summary'].get('total_pods', 0),
            'total_nodes': artifact['summary'].get('total_nodes', 0),
            'total_services': artifact['summary'].get('total_services', 0),
        }
        
        # Check if file exists to determine if we need headers
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(row)
        
        logger.info(f"Cluster summary CSV saved to {csv_file}")
    
    def _save_pod_metrics_csv(self, artifact):
        """Save per-pod metrics to CSV for detailed analysis"""
        csv_file = self.output_dir / f"{artifact['run_id']}_pods.csv"
        
        if not artifact['pods']:
            logger.info("No pod metrics to save")
            return
        
        with open(csv_file, 'w', newline='') as f:
            # Define all possible fields
            fieldnames = [
                'run_id', 'pod_name', 'container_name',
                'cpu_avg_pct', 'cpu_max_pct', 'cpu_min_pct', 'cpu_p95_pct', 'cpu_p99_pct', 'cpu_std_dev',
                'cpu_throttled_avg_sec', 'cpu_throttled_max_sec', 'cpu_throttled_total_sec',
                'memory_avg_mb', 'memory_max_mb', 'memory_min_mb', 'memory_p95_mb',
                'cpu_limit_cores'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for pod in artifact['pods']:
                row = {
                    'run_id': artifact['run_id'],
                    'pod_name': pod['pod_name'],
                    'container_name': pod['container_name'],
                }
                
                # CPU metrics
                if 'cpu' in pod['metrics']:
                    cpu = pod['metrics']['cpu']
                    row.update({
                        'cpu_avg_pct': cpu.get('avg_utilization_pct', 0.0),
                        'cpu_max_pct': cpu.get('max_utilization_pct', 0.0),
                        'cpu_min_pct': cpu.get('min_utilization_pct', 0.0),
                        'cpu_p95_pct': cpu.get('p95_utilization_pct', 0.0),
                        'cpu_p99_pct': cpu.get('p99_utilization_pct', 0.0),
                        'cpu_std_dev': cpu.get('std_dev', 0.0),
                    })
                
                # CPU throttling
                if 'cpu_throttling' in pod['metrics']:
                    throttle = pod['metrics']['cpu_throttling']
                    row.update({
                        'cpu_throttled_avg_sec': throttle.get('avg_throttled_seconds', 0.0),
                        'cpu_throttled_max_sec': throttle.get('max_throttled_seconds', 0.0),
                        'cpu_throttled_total_sec': throttle.get('total_throttled_seconds', 0.0),
                    })
                
                # Memory metrics
                if 'memory' in pod['metrics']:
                    memory = pod['metrics']['memory']
                    row.update({
                        'memory_avg_mb': memory.get('avg_usage_mb', 0.0),
                        'memory_max_mb': memory.get('max_usage_mb', 0.0),
                        'memory_min_mb': memory.get('min_usage_mb', 0.0),
                        'memory_p95_mb': memory.get('p95_usage_mb', 0.0),
                    })
                
                # Resource limits
                if 'resource_limits' in pod:
                    row['cpu_limit_cores'] = pod['resource_limits'].get('cpu_limit_cores', 'N/A')
                
                writer.writerow(row)
        
        logger.info(f"Pod metrics CSV saved to {csv_file}")
    
    def _save_node_metrics_csv(self, artifact):
        """Save per-node metrics to CSV"""
        csv_file = self.output_dir / f"{artifact['run_id']}_nodes.csv"
        
        if not artifact['nodes']:
            logger.info("No node metrics to save")
            return
        
        with open(csv_file, 'w', newline='') as f:
            fieldnames = [
                'run_id', 'node_name',
                'cpu_avg_pct', 'cpu_max_pct', 'cpu_min_pct',
                'memory_avg_util_pct', 'memory_max_util_pct', 'memory_min_util_pct'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for node in artifact['nodes']:
                row = {
                    'run_id': artifact['run_id'],
                    'node_name': node['node_name'],
                }
                
                # CPU metrics
                if 'cpu' in node['metrics']:
                    cpu = node['metrics']['cpu']
                    row.update({
                        'cpu_avg_pct': cpu.get('avg_utilization_pct', 0.0),
                        'cpu_max_pct': cpu.get('max_utilization_pct', 0.0),
                        'cpu_min_pct': cpu.get('min_utilization_pct', 0.0),
                    })
                
                # Memory metrics
                if 'memory' in node['metrics']:
                    memory = node['metrics']['memory']
                    row.update({
                        'memory_avg_util_pct': memory.get('avg_utilization_pct', 0.0),
                        'memory_max_util_pct': memory.get('max_utilization_pct', 0.0),
                        'memory_min_util_pct': memory.get('min_utilization_pct', 0.0),
                    })
                
                writer.writerow(row)
        
        logger.info(f"Node metrics CSV saved to {csv_file}")
