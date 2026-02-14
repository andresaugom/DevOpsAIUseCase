# Terraform Infrastructure

This directory contains Terraform configurations for provisioning Kubernetes clusters across different cloud providers for the Online Boutique benchmarking pipeline.

## ⚠️ Important: How Terraform is Used in This Project

**For most users:** You don't need to run Terraform commands directly. The **Python orchestrator** (`automation/main.py`) manages Terraform automatically:

```bash
# This is the recommended way to use this project:
python automation/main.py --cloud gcp --machine-type n2-standard-4 --duration 600
```

The orchestrator will:
1. Auto-generate `terraform.tfvars` from your CLI arguments
2. Run `terraform init/plan/apply` automatically
3. Deploy applications and collect metrics
4. Destroy infrastructure when done (with `--cleanup`)

**Why this design?**
- Ensures configuration consistency (CLI args → Terraform vars)
- Simplifies user experience (one interface instead of two)
- Enables end-to-end automation (provision → benchmark → collect → cleanup)
- Guarantees reproducible benchmarks

**When to use Terraform directly:**
- You need custom network configurations
- You require advanced security settings
- You're building a long-running development cluster
- You need integration with existing infrastructure

**Trade-off:** Running Terraform manually gives you more infrastructure control but loses the automated benchmarking pipeline. See [README.md](../README.md#usage-patterns) for details.

---

## Direct Terraform Usage (Advanced)

If you've decided you need direct Terraform control (see warning above), follow these instructions:

## Prerequisites

Before using Terraform to provision infrastructure, ensure you have:

1. **Terraform installed** (>= 1.0)
   ```bash
   terraform --version
   ```

2. **Cloud provider CLI configured** (for GCP: gcloud)
   ```bash
   gcloud --version
   ```

3. **Valid cloud credentials** with appropriate permissions

## Minimum Configuration Requirements

### Local Machine Setup

#### 1. Install Terraform

**macOS (using Homebrew):**
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

**Linux (Ubuntu/Debian):**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

**Windows (using Chocolatey):**
```bash
choco install terraform
```

**Verify installation:**
```bash
terraform --version
# Should show: Terraform v1.x.x or later
```

#### 2. Configure Cloud Provider Authentication

**For Google Cloud Platform (GCP):**

1. Create or use existing GCP project:
   ```bash
   export GCP_PROJECT_ID="your-project-id"
   gcloud config set project $GCP_PROJECT_ID
   ```

2. Enable required APIs:
   ```bash
   gcloud services enable container.googleapis.com
   gcloud services enable compute.googleapis.com
   ```

3. Create service account with necessary permissions:
   ```bash
   # Create service account
   gcloud iam service-accounts create terraform-sa \
     --display-name="Terraform Service Account"
   
   # Grant necessary roles
   gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
     --member="serviceAccount:terraform-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/container.admin"
   
   gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
     --member="serviceAccount:terraform-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/compute.admin"
   
   gcloud projects add-iam-policy-binding $GCP_PROJECT_ID \
     --member="serviceAccount:terraform-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com" \
     --role="roles/iam.serviceAccountUser"
   ```

4. Download service account key:
   ```bash
   gcloud iam service-accounts keys create ~/terraform-key.json \
     --iam-account=terraform-sa@${GCP_PROJECT_ID}.iam.gserviceaccount.com
   ```

5. Set environment variable:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=~/terraform-key.json
   ```

#### 3. Initialize Terraform Working Directory

Navigate to the cloud provider directory and initialize:

```bash
cd terraform/gcp
terraform init
```

This command:
- Downloads required provider plugins
- Initializes backend for state storage
- Prepares the directory for Terraform operations

**Expected output:**
```
Initializing the backend...
Initializing provider plugins...
- Finding latest version of hashicorp/google...
- Installing hashicorp/google v5.x.x...
Terraform has been successfully initialized!
```

#### 4. Create Configuration File

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your specific values:

```hcl
# Minimum required configuration
project_id     = "your-gcp-project-id"
region         = "us-central1"
zone           = "us-central1-a"
machine_type   = "n2-standard-4"
cpu_vendor     = "intel"
cpu_generation = "Ice Lake"
node_count     = 3
cluster_name   = "benchmark-cluster"
```

#### 5. Validate Configuration

```bash
# Validate syntax and configuration
terraform validate

# Preview changes without applying
terraform plan
```

### Required Permissions

The service account or user running Terraform needs these IAM roles:

**GCP:**
- `roles/container.admin` - Create and manage GKE clusters
- `roles/compute.admin` - Manage compute resources (nodes, networks)
- `roles/iam.serviceAccountUser` - Use service accounts for node pools

**AWS (Future):**
- `AmazonEKSClusterPolicy`
- `AmazonEKSServicePolicy`
- `AmazonEC2FullAccess`

**Azure (Future):**
- `Contributor` role on the resource group
- `User Access Administrator` for RBAC

### Terraform State Management

**Local State (Default):**
- State stored in `terraform.tfstate` in the working directory
- **Warning**: State files contain sensitive data; keep them secure
- Do not commit state files to version control

**Remote State (Recommended for Production):**

Configure GCS backend by creating a `backend.tf`:

```hcl
terraform {
  backend "gcs" {
    bucket = "your-terraform-state-bucket"
    prefix = "benchmark/state"
  }
}
```

Then re-initialize:
```bash
terraform init -migrate-state
```

### Common Configuration Issues

1. **"Error: Error loading state"**
   - Ensure Terraform is initialized: `terraform init`
   - Check if state file exists and is not corrupted

2. **"Error: could not find default credentials"**
   - Set `GOOGLE_APPLICATION_CREDENTIALS` environment variable
   - Run `gcloud auth application-default login`

3. **"Error: Insufficient permissions"**
   - Verify service account has required IAM roles
   - Check if APIs are enabled in GCP project

4. **"Error: Provider version constraint"**
   - Update Terraform: `brew upgrade terraform` (macOS)
   - Or download latest version from HashiCorp website

5. **"Error: Invalid machine type"**
   - Verify machine type exists in selected region/zone
   - Check GCP documentation for available machine types

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
