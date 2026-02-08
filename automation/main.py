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
import os
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

    def _setup_authentication(self):
        """Setup GCP authentication for Terraform and gcloud"""
        import os
        import subprocess
        
        sa_key_path = '/root/.gcp/service-account-key.json'
        
        if os.path.exists(sa_key_path):
            logger.info("Authenticating with service account...")
            
            # Activate service account for gcloud
            result = subprocess.run(
                ['gcloud', 'auth', 'activate-service-account', '--key-file', sa_key_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to activate service account")
                logger.error(f"STDERR: {result.stderr}")
                raise RuntimeError("Service account activation failed")
            
            # Set environment variable for Terraform
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = sa_key_path
            logger.info("Authentication configured successfully")
        else:
            logger.info("No service account key found, using default credentials")
        
    def run_full_pipeline(self):
        """Execute the complete benchmark pipeline"""
        logger.info("=" * 60)
        logger.info("Starting Online Boutique Benchmark Pipeline")
        logger.info("=" * 60)
        
        try:
            # Step 0: Setup authentication
            logger.info("Step 0: Setting up authentication...")
            self._setup_authentication()
            logger.info("Authentication setup completed")

            # Step 1: Provision infrastructure
            logger.info("Step 1: Provisioning infrastructure...")
            cluster_info = self.terraform.provision_cluster()
            logger.info(f"Cluster provisioned: {cluster_info['cluster_name']}")

            # Step 1.1: Configure kubectl to connect to the cluster
            logger.info("Step 1.5: Configuring kubectl...")
            self.helm.configure_kubectl(cluster_info)
            logger.info("kubectl configured")
            
            # Step 2: Deploy Online Boutique
            logger.info("Step 2: Deploying Online Boutique...")
            self.helm.deploy_online_boutique()
            logger.info("Online Boutique deployed")

            # Step 2.1: Deploy load generator
            logger.info("Step 2.1: Deploying load generator...")
            self.helm.deploy_load_generator(
                users_count=self.config['users_count'],
                rps=self.config['rps']
            )
            logger.info("Load generator deployed")
            
            # Step 3: Deploy monitoring stack
            logger.info("Step 3: Deploying Prometheus + Grafana...")
            monitoring_info = self.helm.deploy_monitoring()

            # Setup port-forward for metrics collection
            prometheus_forward = self.helm.setup_prometheus_access()

            # Update Prometheus URL to use localhost
            self.prometheus = PrometheusClient({
                'prometheus_url': 'http://localhost:9090'
            })
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
            logger.info(f"Region: {self.config['region']}")
            logger.info(f"Zone: {self.config['zone']}")
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
        
        except KeyboardInterrupt:
            logger.warning("=" * 60)
            logger.warning("INTERRUPTED BY USER (Ctrl+C)")
            logger.warning("=" * 60)
            return {
                'success': False,
                'error': 'Interrupted by user'
            }
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("=" * 60)
        logger.info("Cleaning up resources...")
        logger.info("=" * 60)
        
        cleanup_errors = []
        
        # Step 1: Uninstall Helm releases
        try:
            logger.info("Step 1: Uninstalling Helm releases...")
            self.helm.uninstall_all()
            logger.info("Helm releases uninstalled")
        except Exception as e:
            logger.error(f"Helm cleanup failed: {str(e)}")
            cleanup_errors.append(f"Helm: {str(e)}")
        
        # Step 2: Destroy infrastructure
        try:
            logger.info("Step 2: Destroying cluster...")
            self.terraform.destroy_cluster()
            logger.info("Cluster destroyed")
        except Exception as e:
            logger.error(f"Terraform cleanup failed: {str(e)}")
            cleanup_errors.append(f"Terraform: {str(e)}")
        
        if cleanup_errors:
            logger.warning("Cleanup completed with errors:")
            for error in cleanup_errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("=" * 60)
            logger.info("Cleanup completed successfully")
            logger.info("=" * 60)


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

    parser.add_argument(
        '--region',
        type=str,
        default='us-central1',
        help='GCP region (default: us-central1)'
    )

    parser.add_argument(
        '--zone',
        type=str,
        default='us-central1-a',
        help='GCP zone (default: us-central1-a)'
    )

    parser.add_argument(
        '--users-count', 
        type=int,
        default=100,
        help='Number of concurrent users for load testing (default: 100)'
    )

    parser.add_argument(
        '--rps',
        type=int,
        default=50,
        help='Target requests per second for load testing (default: 50)'
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
        'region': args.region,
        'zone': args.zone,
        'duration': args.duration,
        'node_count': args.node_count,
        'skip_provision': args.skip_provision,
        'run_id': f"{args.cloud}-{args.cpu_vendor}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        'gcp_project_id': os.environ.get('GCP_PROJECT_ID'),  # ADD THIS LINE
        'users_count': args.users_count,
        'rps': args.rps
    }
    
    orchestrator = BenchmarkOrchestrator(config)
    
    # Handle cleanup-only mode
    if args.cleanup_only:
        orchestrator.cleanup()
        return 0
    
    # Run the pipeline
    result = orchestrator.run_full_pipeline()
    
    try:
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
    
    except KeyboardInterrupt:
        logger.warning("\n" + "=" * 60)
        logger.warning("Interrupted by user. Starting cleanup...")
        logger.warning("=" * 60)
        
        # Always cleanup on interrupt if --cleanup flag was set
        if args.cleanup:
            try:
                orchestrator.cleanup()
            except Exception as e:
                logger.error(f"Cleanup after interrupt failed: {e}")
        else:
            logger.warning("Cleanup not requested. Cluster may still be running!")
            logger.warning(f"To cleanup manually, run: terraform -chdir=terraform/{args.cloud} destroy")
        
        return 130  # Standard exit code for SIGINT
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
