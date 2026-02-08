# **Updates to Helm Deployer Class:**

This file serves to express quickly the last modifications I did to this class. 

## **Added methods**:
- `configure_kubectl`: Needed to connect to the cluster inside the container.
- `setup_prometheus_access`: Setup port forward to access Prometheus from container.

## **Modified methods**:
- `deploy_online_boutique`: Now using the community-maintained online boutique. The official helm version got removed and replaced with this one. 
- `deploy_monitoring`, `_run_helm_command`, `_run_kubectl_command`: Improved error visibility and logging.  


