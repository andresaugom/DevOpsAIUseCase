# Docker Usage Guide

This guide covers using the containerized DevOps benchmarking automation pipeline. The Docker image includes all necessary dependencies (Terraform, Helm, kubectl, cloud CLIs) to run benchmarks without manual installation.

## Table of Contents

- [Environment Variables Quick Reference](#environment-variables-quick-reference)
- [Setting Up Cloud Credentials](#setting-up-cloud-credentials)
- [Quick Start](#quick-start)
- [Building the Image](#building-the-image)
- [Running Benchmarks](#running-benchmarks)
  - [GCP (Google Cloud Platform)](#gcp-google-cloud-platform)
  - [AWS (Amazon Web Services)](#aws-amazon-web-services)
  - [Azure (Microsoft Azure)](#azure-microsoft-azure)
- [Using the Wrapper Script](#using-the-wrapper-script)
- [Using Docker Compose](#using-docker-compose)
- [Cloud Authentication](#cloud-authentication)
- [Volume Mounts](#volume-mounts)
- [Environment Variables](#environment-variables)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Image Details](#image-details)

---

## Environment Variables Quick Reference

Before running the container, you need to set up the appropriate environment variables for your cloud provider:

### GCP (Google Cloud Platform)

```bash
# Required
export GCP_PROJECT_ID="your-gcp-project-id"

# Optional (if using service account key instead of gcloud auth)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### AWS (Amazon Web Services) - Future Support

```bash
# Required
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Optional (defaults to us-west-2)
export AWS_DEFAULT_REGION="us-west-2"
export AWS_SESSION_TOKEN="..."  # If using temporary credentials
```

### Azure (Microsoft Azure) - Future Support

```bash
# Required
export AZURE_SUBSCRIPTION_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_TENANT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_CLIENT_ID="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
export AZURE_CLIENT_SECRET="your-client-secret"
```

**Complete list of supported environment variables:**

| Variable | Cloud | Required | Default | Description |
|----------|-------|----------|---------|-------------|
| `GCP_PROJECT_ID` | GCP | Yes | - | Google Cloud project identifier |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP | No | - | Path to service account JSON key file |
| `AWS_ACCESS_KEY_ID` | AWS | Yes | - | AWS access key for authentication |
| `AWS_SECRET_ACCESS_KEY` | AWS | Yes | - | AWS secret key for authentication |
| `AWS_DEFAULT_REGION` | AWS | No | `us-west-2` | AWS region for resources |
| `AWS_SESSION_TOKEN` | AWS | No | - | Temporary session token (if using STS) |
| `AZURE_SUBSCRIPTION_ID` | Azure | Yes | - | Azure subscription identifier |
| `AZURE_TENANT_ID` | Azure | Yes | - | Azure Active Directory tenant ID |
| `AZURE_CLIENT_ID` | Azure | Yes | - | Azure service principal client ID |
| `AZURE_CLIENT_SECRET` | Azure | Yes | - | Azure service principal client secret |

---

## Setting Up Cloud Credentials

### GCP Authentication Setup

Before running the container, you must authenticate with Google Cloud:

**Option 1: Using gcloud CLI (Recommended for development)**

```bash
# Install gcloud CLI on your host machine (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate and set up application default credentials
gcloud auth login
gcloud auth application-default login

# Set your default project
gcloud config set project YOUR_PROJECT_ID

# Verify authentication
gcloud auth list
gcloud config list

# The credentials will be stored in ~/.config/gcloud/
# These will be mounted into the container
```

**Option 2: Using Service Account Key (Recommended for production/CI/CD)**

```bash
# 1. Create a service account in GCP Console
#    - Go to IAM & Admin > Service Accounts
#    - Click "Create Service Account"
#    - Name: devops-benchmark-sa
#    - Roles needed:
#      - Kubernetes Engine Admin
#      - Compute Admin
#      - Service Account User
#      - Storage Object Viewer (for pulling images)

# 2. Create and download the JSON key
#    - Click on the service account
#    - Go to "Keys" tab
#    - Click "Add Key" > "Create new key" > JSON
#    - Save the file securely (e.g., ~/gcp-sa-key.json)

# 3. Set environment variables
export GOOGLE_APPLICATION_CREDENTIALS="$HOME/gcp-sa-key.json"
export GCP_PROJECT_ID="your-project-id"

# 4. Verify the service account
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
gcloud config set project "$GCP_PROJECT_ID"
```

### AWS Authentication Setup (Future)

```bash
# Option 1: Using AWS CLI credentials file
# Install AWS CLI: https://aws.amazon.com/cli/
aws configure
# Enter your Access Key ID, Secret Access Key, and default region
# Credentials will be stored in ~/.aws/credentials

# Option 2: Using environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-west-2"

# Option 3: Using IAM role (for EC2 instances)
# No explicit credentials needed, instance profile will be used
```

### Azure Authentication Setup (Future)

```bash
# Option 1: Using Azure CLI
# Install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
az login
az account set --subscription "your-subscription-id"

# Option 2: Using Service Principal
# 1. Create a service principal
az ad sp create-for-rbac --name devops-benchmark-sp \
  --role Contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID

# 2. The output will contain the credentials
# Use them to set environment variables:
export AZURE_SUBSCRIPTION_ID="your-subscription-id"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
```

---

## Quick Start

The fastest way to get started is using the `benchmark.sh` wrapper script:

```bash
# Build the Docker image
./benchmark.sh gcp n2-standard-4 600 --build

# Run a GCP benchmark (requires GCP_PROJECT_ID environment variable)
export GCP_PROJECT_ID="your-project-id"
./benchmark.sh gcp n2-standard-4 600 --cleanup
```

---

## Building the Image

### Build Locally

Build the Docker image from the Dockerfile:

```bash
docker build -t devops-benchmark:latest .
```

> **Note**: The Docker build requires internet access to download pinned versions of tools. Ensure you have access to:
> - `releases.hashicorp.com` (Terraform 1.7.5)
> - `get.helm.sh` (Helm 3.14.0)
> - `dl.k8s.io` (kubectl 1.29.2)
> - `dl.google.com` (Google Cloud SDK 462.0.1)
> - `awscli.amazonaws.com` (AWS CLI 2.15.18)
> - `aka.ms` (Azure CLI latest)
>
> All versions are pinned for reproducible benchmarks across time.

### Multi-architecture Build (Optional)

For multi-platform support (AMD64/ARM64):

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t devops-benchmark:latest .
```

### Check Image Size

```bash
docker images devops-benchmark:latest
# Expected size: ~1.5-2GB
```

---

## Running Benchmarks

### GCP (Google Cloud Platform)

#### Prerequisites

1. **GCP Project**: Active GCP project with billing enabled
2. **Credentials**: One of the following:
   - Application Default Credentials: `~/.config/gcloud/`
   - Service Account Key: JSON file path
3. **Environment Variable**: `GCP_PROJECT_ID`

#### Using Mounted Credentials (Recommended)

```bash
# Set your project ID
export GCP_PROJECT_ID="your-gcp-project-id"

# Run benchmark with mounted gcloud config
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --duration 600 \
  --cleanup
```

#### Using Service Account Key

```bash
export GCP_PROJECT_ID="your-gcp-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

docker run -it --rm \
  -v ${GOOGLE_APPLICATION_CREDENTIALS}:${GOOGLE_APPLICATION_CREDENTIALS}:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  -e GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
  devops-benchmark:latest \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --duration 600 \
  --cleanup
```

#### GCP Machine Type Examples

```bash
# Intel Ice Lake (n2-standard-4)
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp \
  --machine-type n2-standard-4 \
  --cpu-vendor intel \
  --cpu-generation "Ice Lake" \
  --duration 600 \
  --cleanup

# AMD EPYC Milan (n2d-standard-4)
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp \
  --machine-type n2d-standard-4 \
  --cpu-vendor amd \
  --cpu-generation "EPYC Milan" \
  --duration 600 \
  --cleanup

# ARM Ampere Altra (t2a-standard-4)
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp \
  --machine-type t2a-standard-4 \
  --cpu-vendor arm \
  --cpu-generation "Ampere Altra" \
  --duration 600 \
  --cleanup
```

---

### AWS (Amazon Web Services)

> **Note**: AWS support is planned but not yet implemented. The Docker image includes AWS CLI for future use.

#### Prerequisites (Future)

1. **AWS Account**: Active AWS account
2. **Credentials**: AWS Access Key and Secret Key
3. **Environment Variables**: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`

#### Example Usage (Future)

```bash
docker run -it --rm \
  -e AWS_ACCESS_KEY_ID=your-access-key \
  -e AWS_SECRET_ACCESS_KEY=your-secret-key \
  -e AWS_DEFAULT_REGION=us-west-2 \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  devops-benchmark:latest \
  --cloud aws \
  --machine-type m6i.xlarge \
  --duration 600 \
  --cleanup
```

---

### Azure (Microsoft Azure)

> **Note**: Azure support is planned but not yet implemented. The Docker image includes Azure CLI for future use.

#### Prerequisites (Future)

1. **Azure Subscription**: Active Azure subscription
2. **Credentials**: Service Principal credentials
3. **Environment Variables**: `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`

#### Example Usage (Future)

```bash
docker run -it --rm \
  -e AZURE_SUBSCRIPTION_ID=your-subscription-id \
  -e AZURE_TENANT_ID=your-tenant-id \
  -e AZURE_CLIENT_ID=your-client-id \
  -e AZURE_CLIENT_SECRET=your-client-secret \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  devops-benchmark:latest \
  --cloud azure \
  --machine-type Standard_D4s_v5 \
  --duration 600 \
  --cleanup
```

---

## Using the Wrapper Script

The `benchmark.sh` script simplifies Docker usage with automatic credential detection and volume mounting.

### Basic Usage

```bash
./benchmark.sh <cloud> <machine-type> <duration> [options]
```

### Examples

```bash
# Run GCP benchmark
export GCP_PROJECT_ID="your-project-id"
./benchmark.sh gcp n2-standard-4 600 --cleanup

# Build image first, then run
./benchmark.sh gcp n2-standard-4 600 --build --cleanup

# Custom CPU vendor
./benchmark.sh gcp n2d-standard-4 600 --cpu-vendor amd --cleanup

# Skip infrastructure provisioning (use existing cluster)
./benchmark.sh gcp n2-standard-4 600 --skip-provision

# Cleanup only
./benchmark.sh gcp n2-standard-4 600 --cleanup-only

# Interactive shell for debugging
./benchmark.sh gcp n2-standard-4 600 --shell
```

### Script Options

| Option | Description |
|--------|-------------|
| `--cleanup` | Clean up resources after benchmark |
| `--skip-provision` | Skip infrastructure provisioning |
| `--cleanup-only` | Only perform cleanup |
| `--cpu-vendor <vendor>` | CPU vendor (intel, amd, arm) |
| `--node-count <count>` | Number of nodes (default: 3) |
| `--build` | Build Docker image before running |
| `--pull` | Pull Docker image before running |
| `--shell` | Start interactive shell |

---

## Using Docker Compose

For development and testing, use `docker-compose.yml`:

### Run with Default Settings

```bash
docker-compose run --rm devops-benchmark --cloud gcp --machine-type n2-standard-4 --duration 600
```

### Build and Run

```bash
docker-compose build
docker-compose run --rm devops-benchmark --cloud gcp --machine-type n2-standard-4 --duration 600 --cleanup
```

### Interactive Shell

```bash
docker-compose run --rm devops-benchmark /bin/bash
```

### Using .env File

Create a `.env` file:

```bash
# .env
GCP_PROJECT_ID=your-project-id
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_DEFAULT_REGION=us-west-2
```

Then run:

```bash
docker-compose run --rm devops-benchmark --cloud gcp --machine-type n2-standard-4 --duration 600
```

---

## Cloud Authentication

### GCP Authentication

#### Option 1: Application Default Credentials (Recommended)

```bash
# On your host machine
gcloud auth application-default login
gcloud config set project your-project-id

# Run Docker with mounted credentials
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=your-project-id \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600
```

#### Option 2: Service Account Key

```bash
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"
export GCP_PROJECT_ID="your-project-id"

# Run Docker with mounted key
docker run -it --rm \
  -v ${GOOGLE_APPLICATION_CREDENTIALS}:${GOOGLE_APPLICATION_CREDENTIALS}:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS} \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600
```

### AWS Authentication (Future)

```bash
# Export credentials
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_DEFAULT_REGION=us-west-2

# Or mount ~/.aws directory
docker run -it --rm \
  -v ~/.aws:/root/.aws:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  devops-benchmark:latest \
  --cloud aws --machine-type m6i.xlarge --duration 600
```

### Azure Authentication (Future)

```bash
# Set environment variables
export AZURE_SUBSCRIPTION_ID=your-subscription-id
export AZURE_TENANT_ID=your-tenant-id
export AZURE_CLIENT_ID=your-client-id
export AZURE_CLIENT_SECRET=your-client-secret

# Run with environment variables
docker run -it --rm \
  -e AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID} \
  -e AZURE_TENANT_ID=${AZURE_TENANT_ID} \
  -e AZURE_CLIENT_ID=${AZURE_CLIENT_ID} \
  -e AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET} \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  devops-benchmark:latest \
  --cloud azure --machine-type Standard_D4s_v5 --duration 600
```

---

## Volume Mounts

### Required Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `./benchmarks` | `/workspace/benchmarks` | rw | Benchmark output files |

### Credential Mounts (Choose One per Cloud)

#### GCP

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `~/.config/gcloud` | `/root/.config/gcloud` | ro | GCP credentials |
| `/path/to/key.json` | `/path/to/key.json` | ro | Service account key |

#### AWS

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `~/.aws` | `/root/.aws` | ro | AWS credentials |

#### Azure

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `~/.azure` | `/root/.azure` | ro | Azure credentials |

### Optional Mounts

| Host Path | Container Path | Mode | Purpose |
|-----------|---------------|------|---------|
| `./terraform/gcp/.terraform` | `/workspace/terraform/gcp/.terraform` | rw | Terraform state |
| `~/.kube` | `/root/.kube` | rw | kubectl config (generated) |

---

## Environment Variables

### GCP

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `GCP_PROJECT_ID` | Yes | GCP Project ID | `my-project-123` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional | Path to service account key | `/path/to/key.json` |

### AWS (Future)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS Access Key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS Secret Key | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_DEFAULT_REGION` | Optional | AWS Region | `us-west-2` (default) |

### Azure (Future)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AZURE_SUBSCRIPTION_ID` | Yes | Azure Subscription ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_TENANT_ID` | Yes | Azure Tenant ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_CLIENT_ID` | Yes | Azure Client ID | `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` |
| `AZURE_CLIENT_SECRET` | Yes | Azure Client Secret | `your-client-secret` |

---

## Advanced Usage

### Interactive Shell

For debugging or exploration:

```bash
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  /bin/bash
```

Inside the container:

```bash
# Check installed tools
terraform --version
helm version
kubectl version --client
gcloud --version
aws --version
az --version

# Run benchmark manually
cd /workspace
python automation/main.py --cloud gcp --machine-type n2-standard-4 --duration 600
```

### Custom Python Script

Mount your custom automation script:

```bash
docker run -it --rm \
  -v $(pwd)/my_custom_script.py:/workspace/my_custom_script.py \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  python /workspace/my_custom_script.py
```

### Override Terraform Variables

Mount custom `.tfvars` file:

```bash
docker run -it --rm \
  -v $(pwd)/custom.tfvars:/workspace/terraform/gcp/custom.tfvars \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600
```

### Persist Terraform State

To persist Terraform state across runs:

```bash
mkdir -p ./terraform/gcp/.terraform

docker run -it --rm \
  -v $(pwd)/terraform/gcp/.terraform:/workspace/terraform/gcp/.terraform \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600 --skip-provision
```

---

## Troubleshooting

### Image Size Too Large

The image size should be around 1.5-2GB. If larger:

```bash
# Clean up dangling images
docker image prune -f

# Check layer sizes
docker history devops-benchmark:latest
```

### Authentication Errors

#### GCP

```bash
# Verify credentials are mounted correctly
docker run -it --rm \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  gcloud auth list

# Re-authenticate on host
gcloud auth application-default login
gcloud config set project your-project-id
```

#### AWS

```bash
# Verify credentials
docker run -it --rm \
  -v ~/.aws:/root/.aws:ro \
  devops-benchmark:latest \
  aws sts get-caller-identity
```

### Permission Errors

```bash
# Fix benchmarks directory permissions
chmod -R 755 ./benchmarks

# Fix Terraform state directory permissions
chmod -R 755 ./terraform/*/.terraform
```

### Network Issues

```bash
# Use host network mode (Linux only)
docker run -it --rm \
  --network host \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -v $(pwd)/benchmarks:/workspace/benchmarks \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  --cloud gcp --machine-type n2-standard-4 --duration 600
```

### Terraform State Lock

If Terraform state is locked:

```bash
# Force unlock (use with caution)
docker run -it --rm \
  -v $(pwd)/terraform/gcp/.terraform:/workspace/terraform/gcp/.terraform \
  -v ~/.config/gcloud:/root/.config/gcloud:ro \
  -e GCP_PROJECT_ID=${GCP_PROJECT_ID} \
  devops-benchmark:latest \
  /bin/bash -c "cd /workspace/terraform/gcp && terraform force-unlock <lock-id>"
```

### View Container Logs

```bash
# List running containers
docker ps

# View logs
docker logs <container-id>

# Follow logs
docker logs -f <container-id>
```

### Debug Build Issues

```bash
# Build with no cache
docker build --no-cache -t devops-benchmark:latest .

# Build with progress
docker build --progress=plain -t devops-benchmark:latest .
```

---

## Image Details

### Installed Components

All components are pinned to specific versions for reproducible benchmarks:

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Automation scripts |
| Terraform | 1.7.5 | Infrastructure provisioning |
| Helm | 3.14.0 | Kubernetes package manager |
| kubectl | 1.29.2 | Kubernetes CLI |
| Google Cloud SDK | 462.0.1 | GCP CLI and authentication |
| AWS CLI | 2.15.18 | AWS CLI (future support) |
| Azure CLI | Latest* | Azure CLI (future support) |

*Azure CLI version is managed via apt repository. For production use with pinned version, manually specify version after build.

### Python Packages

- `requests` - HTTP client for Prometheus API
- `PyYAML` - YAML parsing
- `pytest` - Testing framework
- Additional packages from `automation/requirements.txt`

### Base Image

- **Base**: `python:3.11-slim`
- **Architecture**: AMD64 (x86_64)
- **OS**: Debian-based

### Build Time

- **Initial build**: ~10-15 minutes (downloads all dependencies)
- **Subsequent builds**: ~1-2 minutes (with Docker cache)

### Image Layers

The image uses multi-stage patterns and cleanup to minimize size:

1. System packages installation
2. Tool downloads and installations (Terraform, Helm, kubectl)
3. Cloud CLI installations (gcloud, aws, az)
4. Python package installation
5. Project file copy

---

## Best Practices

### Security

1. **Never bake credentials into the image**: Always use volume mounts or environment variables
2. **Use read-only mounts**: Mount credential directories as `:ro` (read-only)
3. **Rotate credentials regularly**: Especially for long-running projects
4. **Use service accounts**: Prefer service accounts over user accounts for automation
5. **Review mounted volumes**: Only mount necessary directories

### Performance

1. **Persist Terraform state**: Mount `.terraform` directories to avoid re-initialization
2. **Use local image cache**: Build image once, reuse for multiple benchmarks
3. **Parallel benchmarks**: Run multiple containers for different machine types
4. **Clean up after benchmarks**: Use `--cleanup` flag to avoid resource waste

### Development

1. **Use docker-compose**: Easier configuration management for development
2. **Interactive shell**: Debug issues with `--shell` option
3. **Mount source code**: For rapid development, mount `automation/` directory
4. **Check logs**: Always review benchmark logs for errors

---

## Platform Support

### Tested Platforms

- ✅ **Linux** (Ubuntu 20.04+, Debian 11+, RHEL 8+)
- ✅ **macOS** (10.15+, both Intel and Apple Silicon via Rosetta)
- ✅ **Windows** (WSL2 required)

### Windows WSL2 Notes

```powershell
# In PowerShell, set environment variables
$env:GCP_PROJECT_ID="your-project-id"

# Run benchmark
wsl bash -c "./benchmark.sh gcp n2-standard-4 600 --cleanup"
```

---

## Next Steps

1. **Read the main README**: [../README.md](../README.md)
2. **Check quick reference**: [../QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
3. **Review architecture**: [../PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md)
4. **Run your first benchmark**: Use the examples above

---

## Support and Contributing

For issues, questions, or contributions:

1. Check existing documentation
2. Review troubleshooting section
3. Open an issue on GitHub
4. Submit pull requests for improvements

---

**Happy Benchmarking! 🚀**
