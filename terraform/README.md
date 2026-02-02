# Terraform Infrastructure

This directory contains Terraform configurations for provisioning Kubernetes clusters across different cloud providers for the Online Boutique benchmarking pipeline.

## Directory Structure

```
terraform/
├── gcp/           # Google Cloud Platform (GKE) - Fully implemented
├── aws/           # Amazon Web Services (EKS) - Template for future implementation
├── azure/         # Microsoft Azure (AKS) - Template for future implementation
└── modules/       # Shared Terraform modules
```

## Cloud Providers

### Google Cloud Platform (GCP) - Implemented

The GCP configuration provisions a Google Kubernetes Engine (GKE) cluster with:
- Fixed machine types for reproducible benchmarks
- Node labels for CPU vendor and generation tracking
- Disabled autoscaling during benchmark runs
- Self-managed Prometheus (not GCP Managed Prometheus)

**Usage:**

```bash
cd gcp
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project details
terraform init
terraform plan
terraform apply
```

**Required Variables:**
- `project_id`: Your GCP project ID
- `machine_type`: Machine type (e.g., `n2-standard-4`, `n2d-standard-4`, `t2a-standard-4`)
- `cpu_vendor`: CPU vendor (`intel`, `amd`, or `arm`)
- `cpu_generation`: CPU generation identifier

**Getting Cluster Access:**

```bash
gcloud container clusters get-credentials benchmark-cluster --zone us-central1-a --project YOUR_PROJECT_ID
```

### AWS (EKS) - Future Implementation

Template structure ready for Amazon Elastic Kubernetes Service implementation.

### Azure (AKS) - Future Implementation

Template structure ready for Azure Kubernetes Service implementation.

## Machine Type Selection Guide

### GCP Machine Types

| Family | CPU Vendor | Generation | Example Types |
|--------|-----------|-----------|---------------|
| N2 | Intel | Ice Lake | n2-standard-4, n2-standard-8 |
| N2D | AMD | EPYC Milan | n2d-standard-4, n2d-standard-8 |
| T2A | ARM | Ampere Altra | t2a-standard-4, t2a-standard-8 |
| N1 | Intel | Skylake/Broadwell | n1-standard-4 (legacy) |

## Benchmark Reproducibility

For reproducible benchmarks:
1. **Fixed machine types** - No autoscaling
2. **Fixed node count** - Consistent across runs
3. **Single zone** - Avoid cross-zone latency variance
4. **Labeled nodes** - Track CPU vendor and generation
5. **Disabled auto-upgrade** - Prevent unexpected changes

## Outputs

After `terraform apply`, the following outputs are available:
- `cluster_name`: Name of the created cluster
- `cluster_endpoint`: API server endpoint
- `machine_type`: Machine type used
- `cpu_vendor`: CPU vendor
- `cpu_generation`: CPU generation
- `kubeconfig_command`: Command to configure kubectl

## Cleanup

To destroy the infrastructure:

```bash
terraform destroy
```

**Warning:** This will delete the entire cluster and all resources.
