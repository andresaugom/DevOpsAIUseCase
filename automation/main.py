"""
Online Boutique Benchmark Orchestrator

This is the main entry point for the benchmarking pipeline.
It orchestrates infrastructure provisioning, application deployment,
load testing, metrics collection, and artifact generation.

Usage:
    python main.py --cloud gcp --machine-type n2-standard-4 --duration 600
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from modules.terraform_executor import TerraformExecutor
from modules.helm_deployer import HelmDeployer
from modules.prometheus_client import PrometheusClient
from modules.benchmark_runner import BenchmarkRunner
from modules.artifact_generator import ArtifactGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BenchmarkOrchestrator:
    """Orchestrates the complete benchmark pipeline"""
    
    def __init__(self, config):
        self.config = config
        self.terraform = TerraformExecutor(config)
        self.helm = HelmDeployer(config)
        self.prometheus = PrometheusClient(config)
        self.benchmark_runner = BenchmarkRunner(config)
        self.artifact_generator = ArtifactGenerator(config)
        
    def run_full_pipeline(self):
        """Execute the complete benchmark pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Online Boutique Benchmark Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 1: Provision infrastructure
            logger.info("Step 1: Provisioning infrastructure...")
            cluster_info = self.terraform.provision_cluster()
            logger.info(f"Cluster provisioned: {cluster_info['cluster_name']}")
            
            # Step 2: Deploy Online Boutique
            logger.info("Step 2: Deploying Online Boutique...")
            self.helm.deploy_online_boutique()
            logger.info("Online Boutique deployed")
            
            # Step 3: Deploy monitoring stack
            logger.info("Step 3: Deploying Prometheus + Grafana...")
            monitoring_info = self.helm.deploy_monitoring()
            logger.info(f"Monitoring deployed. Grafana URL: {monitoring_info.get('grafana_url')}")
            
            # Step 4: Wait for services to be ready
            logger.info("Step 4: Waiting for services to be ready...")
            self.helm.wait_for_services()
            logger.info("All services ready")
            
            # Step 5: Run benchmark
            logger.info(f"Step 5: Running benchmark for {self.config['duration']}s...")
            benchmark_results = self.benchmark_runner.run_benchmark(
                duration=self.config['duration']
            )
            logger.info("Benchmark completed")
            
            # Step 6: Collect metrics from Prometheus
            logger.info("Step 6: Collecting metrics from Prometheus...")
            metrics = self.prometheus.collect_metrics(
                start_time=benchmark_results['start_time'],
                end_time=benchmark_results['end_time']
            )
            logger.info(f"Collected {len(metrics)} metric series")
            
            # Step 7: Generate benchmark artifact
            logger.info("Step 7: Generating benchmark artifact...")
            artifact = self.artifact_generator.generate(
                cluster_info=cluster_info,
                metrics=metrics,
                benchmark_results=benchmark_results
            )
            
            artifact_path = self.artifact_generator.save_artifact(artifact)
            logger.info(f"Artifact saved to: {artifact_path}")
            
            # Summary
            logger.info("=" * 60)
            logger.info("Benchmark Pipeline Completed Successfully!")
            logger.info("=" * 60)
            logger.info(f"Cluster: {cluster_info['cluster_name']}")
            logger.info(f"Machine Type: {cluster_info['machine_type']}")
            logger.info(f"CPU Vendor: {cluster_info['cpu_vendor']}")
            logger.info(f"Duration: {self.config['duration']}s")
            logger.info(f"Artifact: {artifact_path}")
            logger.info(f"Grafana: {monitoring_info.get('grafana_url')}")
            logger.info("=" * 60)
            
            return {
                'success': True,
                'artifact_path': artifact_path,
                'cluster_info': cluster_info,
                'monitoring_info': monitoring_info
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        try:
            self.helm.uninstall_all()
            self.terraform.destroy_cluster()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}", exc_info=True)


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Online Boutique Benchmark Orchestrator'
    )
    
    parser.add_argument(
        '--cloud',
        type=str,
        required=True,
        choices=['gcp', 'aws', 'azure'],
        help='Cloud provider'
    )
    
    parser.add_argument(
        '--machine-type',
        type=str,
        required=True,
        help='Machine type (e.g., n2-standard-4 for GCP)'
    )
    
    parser.add_argument(
        '--cpu-vendor',
        type=str,
        default='intel',
        choices=['intel', 'amd', 'arm'],
        help='CPU vendor'
    )
    
    parser.add_argument(
        '--cpu-generation',
        type=str,
        default='Ice Lake',
        help='CPU generation identifier'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=600,
        help='Benchmark duration in seconds (default: 600)'
    )
    
    parser.add_argument(
        '--node-count',
        type=int,
        default=3,
        help='Number of nodes (default: 3)'
    )
    
    parser.add_argument(
        '--skip-provision',
        action='store_true',
        help='Skip infrastructure provisioning (use existing cluster)'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Clean up resources after benchmark'
    )
    
    parser.add_argument(
        '--cleanup-only',
        action='store_true',
        help='Only perform cleanup (no benchmark)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    
    # Build configuration
    config = {
        'cloud': args.cloud,
        'machine_type': args.machine_type,
        'cpu_vendor': args.cpu_vendor,
        'cpu_generation': args.cpu_generation,
        'duration': args.duration,
        'node_count': args.node_count,
        'skip_provision': args.skip_provision,
        'run_id': f"{args.cloud}-{args.cpu_vendor}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    }
    
    orchestrator = BenchmarkOrchestrator(config)
    
    # Handle cleanup-only mode
    if args.cleanup_only:
        orchestrator.cleanup()
        return 0
    
    # Run the pipeline
    result = orchestrator.run_full_pipeline()
    
    # Optional cleanup
    if args.cleanup:
        orchestrator.cleanup()
    
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
