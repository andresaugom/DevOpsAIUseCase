"""
Helm Deployer Module

Handles Helm deployments for Online Boutique and monitoring stack.
"""

import logging
import subprocess
import time
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class HelmDeployer:
    """Manages Helm deployments"""
    
    def __init__(self, config):
        self.config = config
        self.kubernetes_dir = Path(__file__).parent.parent.parent / 'kubernetes'
    
    def configure_kubectl(self, cluster_info):
        """Configure kubectl to connect to the cluster"""
        logger.info("Configuring kubectl...")
        
        if self.config['cloud'] == 'gcp':
            if os.path.exists('/root/.gcp/service-account-key.json'):
                logger.info("Authenticating with service account...")
                subprocess.run([
                    'gcloud', 'auth', 'activate-service-account', 
                    '--key-file=/root/.gcp/service-account-key.json'
                ], check=True)

            cmd = [
                'gcloud', 'container', 'clusters', 'get-credentials',
                cluster_info['cluster_name'],
                '--zone', cluster_info['zone'],
                '--project', self.config['gcp_project_id']
            ]
            
            logger.debug(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to configure kubectl")
                logger.error(f"STDOUT:\n{result.stdout}")
                logger.error(f"STDERR:\n{result.stderr}")
                raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
            
            logger.info("kubectl configured successfully")

    def configure_loadgenerator(self, users_count, rps):
        """Configure loadgenerator with specified users and request rate"""
        logger.info(f"Configuring loadgenerator with USERS={users_count}, RATE={rps}...")
        
        try:
            # Patch the loadgenerator deployment with environment variables
            self._run_kubectl_command([
                'set', 'env', 'deployment/loadgenerator',
                f'USERS={users_count}',
                f'RATE={rps}'
            ])
            
            # Wait for the new pod to be ready
            logger.info("Waiting for loadgenerator to restart with new configuration...")
            self._run_kubectl_command([
                'rollout', 'status', 'deployment/loadgenerator',
                '--timeout=2m'
            ])
            
            logger.info(f"Loadgenerator configured successfully: USERS={users_count}, RATE={rps}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to configure loadgenerator: {e}")
            raise

    def setup_prometheus_access(self):
        """Setup port-forward to access Prometheus from outside cluster"""
        import subprocess
        import threading
        
        logger.info("Setting up port-forward to Prometheus...")
        
        # Start port-forward in background
        cmd = [
            'kubectl', 'port-forward',
            '-n', 'monitoring',
            'svc/prometheus-operated',
            '9090:9090'
        ]
        
        # This will run in background
        process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Give it a moment to establish
        import time
        time.sleep(5)
        
        logger.info("Prometheus accessible at http://localhost:9090")
        
        return process
        
    def deploy_online_boutique(self):
        """Deploy Online Boutique application"""
        logger.info("Deploying Online Boutique...")
        
        # Use official Kubernetes manifests (Helm chart is deprecated)
        manifest_url = "https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml"
        
        logger.info("Applying Online Boutique manifests from GitHub...")
        self._run_kubectl_command(['apply', '-f', manifest_url])
        
        # Wait for frontend to be ready as a health check
        logger.info("Waiting for frontend service to be ready...")
        self._run_kubectl_command([
            'wait', '--for=condition=available',
            'deployment/frontend',
            '--timeout=5m',
            '--namespace=default'
        ])
        
        logger.info("Online Boutique deployed successfully")
    
    def deploy_monitoring(self):
        """Deploy Prometheus + Grafana monitoring stack"""
        logger.info("Deploying monitoring stack...")
        
        # Add Helm repository
        logger.info("Adding Helm repository...")
        self._run_helm_command([
            'repo', 'add', 'prometheus-community',
            'https://prometheus-community.github.io/helm-charts'
        ])
        self._run_helm_command(['repo', 'update'])
        logger.info("Helm repository configured")
        
        # Create monitoring namespace
        logger.info("Creating monitoring namespace...")
        try:
            self._run_kubectl_command(['create', 'namespace', 'monitoring'])
            logger.info("Namespace created")
        except subprocess.CalledProcessError:
            logger.info("Namespace already exists, continuing...")
        
        # Verify values file exists
        values_file = self.kubernetes_dir / 'monitoring' / 'prometheus-values.yaml'
        if not values_file.exists():
            raise FileNotFoundError(f"Values file not found: {values_file}")
        
        logger.info(f"Using values file: {values_file}")
        logger.info("Installing Prometheus stack (timeout: 15 minutes)...")
        logger.info("This includes Prometheus Operator, Grafana, and several components...")
        
        # Install with explicit timeout
        import signal
        import threading
        
        # Create a stop event for the progress thread
        stop_event = threading.Event()
        
        # Create a timer to log progress
        def log_progress():
            elapsed = 0
            while not stop_event.is_set() and elapsed < 900:  # 15 minutes
                if stop_event.wait(60):  # Sleep 60s or until stopped
                    break
                elapsed += 60
                logger.info(f"Still installing... ({elapsed//60} minutes elapsed)")
        
        progress_thread = threading.Thread(target=log_progress, daemon=True)
        progress_thread.start()
        
        try:
            # Use upgrade --install for idempotent deployment
            self._run_helm_command([
                'upgrade', '--install', 'prometheus', 'prometheus-community/kube-prometheus-stack',
                '--namespace', 'monitoring',
                '--values', str(values_file),
                '--wait',
                '--timeout', '15m',
                '--debug'
            ])
            logger.info("Prometheus stack installed successfully!")
        except subprocess.CalledProcessError as e:
            logger.error("Helm install failed or timed out!")
            logger.error("Checking deployment status...")
            
            # Check what got deployed
            try:
                result = self._run_kubectl_command(['get', 'pods', '-n', 'monitoring', '-o', 'wide'])
                logger.error(f"Pods in monitoring namespace:\n{result.stdout}")
            except:
                logger.error("No pods found in monitoring namespace")
            
            # Check events
            try:
                result = self._run_kubectl_command(['get', 'events', '-n', 'monitoring', '--sort-by=.lastTimestamp'])
                logger.error(f"Recent events:\n{result.stdout}")
            except:
                pass
            
            raise RuntimeError("Prometheus deployment failed or timed out") from e
        finally:
            # Always stop the progress thread
            stop_event.set()
            progress_thread.join(timeout=2)
        
        # Get Grafana URL
        logger.info("Retrieving Grafana service URL...")
        grafana_url = self._get_service_url('monitoring', 'prometheus-grafana')
        
        logger.info("Monitoring stack deployed successfully")
        
        return {
            'grafana_url': grafana_url,
            'prometheus_url': 'http://prometheus-operated.monitoring.svc:9090'
        }
    
    def wait_for_services(self, timeout=300):
        """Wait for all services to be ready"""
        logger.info("Waiting for services to be ready...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if all pods are running
                result = self._run_kubectl_command([
                    'get', 'pods', '-n', 'default',
                    '-o', 'jsonpath={.items[*].status.phase}'
                ])
                
                phases = result.stdout.strip().split()
                if all(phase == 'Running' for phase in phases):
                    logger.info("All services are ready")
                    return True
                
                logger.debug(f"Waiting... ({len([p for p in phases if p == 'Running'])}/{len(phases)} running)")
                time.sleep(10)
                
            except Exception as e:
                logger.debug(f"Error checking pod status: {e}")
                time.sleep(10)
        
        raise TimeoutError("Services did not become ready in time")
    
    def uninstall_all(self):
        """Uninstall all releases"""
        logger.info("Uninstalling releases...")
        
        # Online Boutique is deployed via kubectl, not Helm
        try:
            manifest_url = "https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml"
            logger.info("Deleting Online Boutique (kubectl)...")
            self._run_kubectl_command(['delete', '-f', manifest_url])
            logger.info("Online Boutique deleted successfully")
        except Exception as e:
            logger.warning(f"Error uninstalling online-boutique: {e}")
        
        # Prometheus is a Helm release
        try:
            logger.info("Uninstalling Prometheus (Helm)...")
            self._run_helm_command(['uninstall', 'prometheus', '-n', 'monitoring'])
            logger.info("Prometheus uninstalled successfully")
        except Exception as e:
            logger.warning(f"Error uninstalling prometheus: {e}")
    
    def _run_helm_command(self, args):
        """Run a Helm command"""
        cmd = ['helm'] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise immediately
        )
        
        if result.stdout:
            logger.debug(result.stdout)
        
        # Log errors before raising
        if result.returncode != 0:
            logger.error(f"Helm command failed: {' '.join(cmd)}")
            logger.error(f"STDOUT:\n{result.stdout}")
            logger.error(f"STDERR:\n{result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result
    
    def _run_kubectl_command(self, args):
        """Run a kubectl command"""
        cmd = ['kubectl'] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False  # Don't raise immediately
        )
        
        if result.stdout:
            logger.debug(result.stdout)
        
        # Log errors before raising
        if result.returncode != 0:
            logger.error(f"kubectl command failed: {' '.join(cmd)}")
            logger.error(f"STDOUT:\n{result.stdout}")
            logger.error(f"STDERR:\n{result.stderr}")
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        
        return result
    
    def _get_service_url(self, namespace, service_name):
        """Get external URL for a LoadBalancer service"""
        try:
            result = self._run_kubectl_command([
                'get', 'service', service_name,
                '-n', namespace,
                '-o', 'jsonpath={.status.loadBalancer.ingress[0].ip}'
            ])
            
            ip = result.stdout.strip()
            if ip:
                return f"http://{ip}"
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not get service URL: {e}")
            return None
