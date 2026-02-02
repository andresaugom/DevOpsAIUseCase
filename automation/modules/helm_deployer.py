"""
Helm Deployer Module

Handles Helm deployments for Online Boutique and monitoring stack.
"""

import logging
import subprocess
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class HelmDeployer:
    """Manages Helm deployments"""
    
    def __init__(self, config):
        self.config = config
        self.kubernetes_dir = Path(__file__).parent.parent.parent / 'kubernetes'
        
    def deploy_online_boutique(self):
        """Deploy Online Boutique application"""
        logger.info("Deploying Online Boutique...")
        
        # Add Helm repository
        self._run_helm_command([
            'repo', 'add', 'google-samples',
            'https://googlecloudplatform.github.io/microservices-demo'
        ])
        self._run_helm_command(['repo', 'update'])
        
        # Install Online Boutique
        values_file = self.kubernetes_dir / 'online-boutique' / 'values.yaml'
        self._run_helm_command([
            'install', 'online-boutique', 'google-samples/online-boutique',
            '--namespace', 'default',
            '--values', str(values_file),
            '--wait',
            '--timeout', '10m'
        ])
        
        logger.info("Online Boutique deployed successfully")
    
    def deploy_monitoring(self):
        """Deploy Prometheus + Grafana monitoring stack"""
        logger.info("Deploying monitoring stack...")
        
        # Add Helm repository
        self._run_helm_command([
            'repo', 'add', 'prometheus-community',
            'https://prometheus-community.github.io/helm-charts'
        ])
        self._run_helm_command(['repo', 'update'])
        
        # Create monitoring namespace
        self._run_kubectl_command([
            'create', 'namespace', 'monitoring', '--dry-run=client', '-o', 'yaml'
        ])
        self._run_kubectl_command(['apply', '-f', '-'])
        
        # Install Prometheus stack
        values_file = self.kubernetes_dir / 'monitoring' / 'prometheus-values.yaml'
        self._run_helm_command([
            'install', 'prometheus', 'prometheus-community/kube-prometheus-stack',
            '--namespace', 'monitoring',
            '--values', str(values_file),
            '--wait',
            '--timeout', '10m'
        ])
        
        # Get Grafana URL
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
        """Uninstall all Helm releases"""
        logger.info("Uninstalling Helm releases...")
        
        try:
            self._run_helm_command(['uninstall', 'online-boutique', '-n', 'default'])
        except Exception as e:
            logger.warning(f"Error uninstalling online-boutique: {e}")
        
        try:
            self._run_helm_command(['uninstall', 'prometheus', '-n', 'monitoring'])
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
            check=True
        )
        
        return result
    
    def _run_kubectl_command(self, args):
        """Run a kubectl command"""
        cmd = ['kubectl'] + args
        logger.debug(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
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
