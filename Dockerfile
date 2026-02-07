# Multi-Cloud DevOps Benchmarking Automation Pipeline
# Supports GCP (implemented), AWS, and Azure (future)

# Use Python 3.11 slim base image for smaller size
FROM python:3.11-slim AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TERRAFORM_VERSION=1.7.5 \
    HELM_VERSION=3.14.0 \
    KUBECTL_VERSION=1.29.2 \
    GCLOUD_VERSION=462.0.1 \
    AWS_CLI_VERSION=2.15.18

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    unzip \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Install Terraform
RUN wget -q https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /usr/local/bin/ && \
    rm terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    terraform --version

# Install Helm (pinned version from official binary)
RUN wget -q https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz && \
    tar -zxf helm-v${HELM_VERSION}-linux-amd64.tar.gz && \
    mv linux-amd64/helm /usr/local/bin/ && \
    rm -rf linux-amd64 helm-v${HELM_VERSION}-linux-amd64.tar.gz && \
    helm version

# Install kubectl (pinned version from official binary)
RUN wget -q "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl && \
    kubectl version --client

# Install Google Cloud SDK (pinned version)
RUN wget -q https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-${GCLOUD_VERSION}-linux-x86_64.tar.gz && \
    tar -xzf google-cloud-cli-${GCLOUD_VERSION}-linux-x86_64.tar.gz && \
    ./google-cloud-sdk/install.sh --quiet --usage-reporting=false --path-update=true && \
    rm -rf google-cloud-cli-${GCLOUD_VERSION}-linux-x86_64.tar.gz && \
    ln -s /google-cloud-sdk/bin/gcloud /usr/local/bin/gcloud && \
    ln -s /google-cloud-sdk/bin/gsutil /usr/local/bin/gsutil && \
    gcloud components install gke-gcloud-auth-plugin --quiet && \
    gcloud --version

# Install AWS CLI v2 (pinned version)
RUN wget -q "https://awscli.amazonaws.com/awscli-exe-linux-x86_64-${AWS_CLI_VERSION}.zip" -O "awscliv2.zip" && \
    unzip -q awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip && \
    aws --version

# Install Azure CLI (for future Azure support)
# Note: Azure CLI is installed via apt, pinning specific version requires additional complexity
# For production use, consider using: az upgrade --version <specific-version>
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash && \
    az --version

# Set working directory
WORKDIR /workspace

# Copy Python requirements first (for better caching)
COPY automation/requirements.txt /workspace/automation/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r automation/requirements.txt

# Copy project files
COPY automation/ /workspace/automation/
COPY terraform/ /workspace/terraform/
COPY kubernetes/ /workspace/kubernetes/
COPY README.md /workspace/
COPY PROJECT_OVERVIEW.md /workspace/

# Create benchmarks directory (will be mounted as volume)
RUN mkdir -p /workspace/benchmarks

# Set up kubectl configuration directory
RUN mkdir -p /root/.kube

# Entry point: run the main.py script with all arguments passed through
ENTRYPOINT ["python", "/workspace/automation/main.py"]

# Default command (can be overridden)
CMD ["--help"]
