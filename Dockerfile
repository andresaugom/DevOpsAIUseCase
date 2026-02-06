# Multi-Cloud DevOps Benchmarking Automation Pipeline
# Supports GCP (implemented), AWS, and Azure (future)

# Use Python 3.11 slim base image for smaller size
FROM python:3.11-slim AS base

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TERRAFORM_VERSION=1.7.5 \
    HELM_VERSION=3.15.4 \
    KUBECTL_VERSION=1.29.2

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

# Install Helm
RUN curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | tee /usr/share/keyrings/helm.gpg > /dev/null && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | \
    tee /etc/apt/sources.list.d/helm-stable-debian.list && \
    apt-get update && \
    apt-get install -y helm && \
    rm -rf /var/lib/apt/lists/* && \
    helm version

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl && \
    rm kubectl && \
    kubectl version --client

# Install Google Cloud SDK (for GCP)
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | \
    tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
    apt-get update && \
    apt-get install -y google-cloud-sdk google-cloud-sdk-gke-gcloud-auth-plugin && \
    rm -rf /var/lib/apt/lists/* && \
    gcloud --version

# Install AWS CLI v2 (for future AWS support)
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -rf aws awscliv2.zip && \
    aws --version

# Install Azure CLI (for future Azure support)
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
