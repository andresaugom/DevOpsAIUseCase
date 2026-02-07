#!/bin/bash
# DevOps Benchmarking Pipeline - Docker Wrapper Script
# Simplifies running the benchmark with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="${DOCKER_IMAGE:-devops-benchmark:latest}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-}"

# Display usage
usage() {
    cat << EOF
${BLUE}DevOps Benchmarking Pipeline - Docker Wrapper${NC}

${GREEN}Usage:${NC}
  $0 <cloud> <machine-type> <duration> [options]

${GREEN}Arguments:${NC}
  cloud           Cloud provider (gcp, aws, azure)
  machine-type    Machine type (e.g., n2-standard-4)
  duration        Benchmark duration in seconds (e.g., 600)

${GREEN}Options:${NC}
  --cleanup              Clean up resources after benchmark
  --skip-provision       Skip infrastructure provisioning
  --cleanup-only         Only perform cleanup
  --cpu-vendor <vendor>  CPU vendor (intel, amd, arm) - default: intel
  --node-count <count>   Number of nodes - default: 3
  --build                Build Docker image before running
  --pull                 Pull Docker image before running
  --shell                Start interactive shell instead of benchmark

${GREEN}Environment Variables:${NC}
  GCP:
    GCP_PROJECT_ID              Google Cloud Project ID
    GOOGLE_APPLICATION_CREDENTIALS  Path to service account JSON (default: ~/.config/gcloud/application_default_credentials.json)
  
  AWS:
    AWS_ACCESS_KEY_ID           AWS Access Key
    AWS_SECRET_ACCESS_KEY       AWS Secret Key
    AWS_DEFAULT_REGION          AWS Region (default: us-west-2)
  
  Azure:
    AZURE_SUBSCRIPTION_ID       Azure Subscription ID
    AZURE_TENANT_ID             Azure Tenant ID
    AZURE_CLIENT_ID             Azure Client ID
    AZURE_CLIENT_SECRET         Azure Client Secret

${GREEN}Examples:${NC}
  # Run GCP benchmark
  $0 gcp n2-standard-4 600 --cleanup

  # Run with custom CPU vendor
  $0 gcp n2d-standard-4 600 --cpu-vendor amd --cleanup

  # Build image first, then run
  $0 gcp n2-standard-4 600 --build --cleanup

  # Interactive shell for debugging
  $0 gcp n2-standard-4 600 --shell

  # Cleanup only
  $0 gcp n2-standard-4 600 --cleanup-only

EOF
    exit 1
}

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: ${IMAGE_NAME}"
    docker build -t "${IMAGE_NAME}" "${SCRIPT_DIR}"
    log_success "Image built successfully"
}

# Pull Docker image
pull_image() {
    if [ -n "${DOCKER_REGISTRY}" ]; then
        log_info "Pulling Docker image: ${DOCKER_REGISTRY}/${IMAGE_NAME}"
        docker pull "${DOCKER_REGISTRY}/${IMAGE_NAME}"
        log_success "Image pulled successfully"
    else
        log_warning "DOCKER_REGISTRY not set, skipping pull"
    fi
}

# Detect and validate credentials
check_credentials() {
    local cloud=$1
    
    case ${cloud} in
        gcp)
            if [ -z "${GCP_PROJECT_ID}" ]; then
                log_error "GCP_PROJECT_ID environment variable is required for GCP"
                exit 1
            fi
            
            # Check for credentials
            if [ -n "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
                if [ ! -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
                    log_error "GOOGLE_APPLICATION_CREDENTIALS file not found: ${GOOGLE_APPLICATION_CREDENTIALS}"
                    exit 1
                fi
                log_info "Using GCP credentials from: ${GOOGLE_APPLICATION_CREDENTIALS}"
            elif [ -d "${HOME}/.config/gcloud" ]; then
                log_info "Using GCP credentials from: ${HOME}/.config/gcloud"
            else
                log_warning "No GCP credentials found. Make sure to authenticate first:"
                log_warning "  gcloud auth application-default login"
            fi
            ;;
        aws)
            if [ -z "${AWS_ACCESS_KEY_ID}" ] || [ -z "${AWS_SECRET_ACCESS_KEY}" ]; then
                log_error "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required for AWS"
                exit 1
            fi
            log_info "Using AWS credentials from environment variables"
            ;;
        azure)
            if [ -z "${AZURE_SUBSCRIPTION_ID}" ]; then
                log_error "AZURE_SUBSCRIPTION_ID is required for Azure"
                exit 1
            fi
            log_info "Using Azure credentials from environment variables"
            ;;
        *)
            log_error "Unknown cloud provider: ${cloud}"
            exit 1
            ;;
    esac
}

# Main function
main() {
    # Parse arguments
    if [ $# -lt 3 ] && [ "$1" != "--help" ] && [ "$1" != "-h" ]; then
        usage
    fi
    
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        usage
    fi
    
    local cloud=$1
    local machine_type=$2
    local duration=$3
    shift 3
    
    local extra_args=()
    local do_build=false
    local do_pull=false
    local do_shell=false
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                do_build=true
                shift
                ;;
            --pull)
                do_pull=true
                shift
                ;;
            --shell)
                do_shell=true
                shift
                ;;
            *)
                extra_args+=("$1")
                shift
                ;;
        esac
    done
    
    # Build if requested
    if [ "${do_build}" = true ]; then
        build_image
    fi
    
    # Pull if requested
    if [ "${do_pull}" = true ]; then
        pull_image
    fi
    
    # Check credentials
    check_credentials "${cloud}"
    
    # Prepare Docker volumes
    local volumes=(
        "-v" "${SCRIPT_DIR}/benchmarks:/workspace/benchmarks"
    )
    
    # Mount cloud-specific credentials
    case ${cloud} in
        gcp)
            if [ -n "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
                volumes+=("-v" "${GOOGLE_APPLICATION_CREDENTIALS}:${GOOGLE_APPLICATION_CREDENTIALS}:ro")
            fi
            if [ -d "${HOME}/.config/gcloud" ]; then
                volumes+=("-v" "${HOME}/.config/gcloud:/root/.config/gcloud:ro")
            fi
            ;;
        aws)
            if [ -d "${HOME}/.aws" ]; then
                volumes+=("-v" "${HOME}/.aws:/root/.aws:ro")
            fi
            ;;
        azure)
            if [ -d "${HOME}/.azure" ]; then
                volumes+=("-v" "${HOME}/.azure:/root/.azure:ro")
            fi
            ;;
    esac
    
    # Mount Terraform state directories for persistence
    for tf_dir in gcp aws azure; do
        local tf_path="${SCRIPT_DIR}/terraform/${tf_dir}"
        if [ -d "${tf_path}" ]; then
            mkdir -p "${tf_path}/.terraform"
            volumes+=("-v" "${tf_path}/.terraform:/workspace/terraform/${tf_dir}/.terraform")
        fi
    done
    
    # Prepare environment variables
    local env_vars=(
        "-e" "GCP_PROJECT_ID=${GCP_PROJECT_ID}"
        "-e" "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
        "-e" "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
        "-e" "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-west-2}"
        "-e" "AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}"
        "-e" "AZURE_TENANT_ID=${AZURE_TENANT_ID}"
        "-e" "AZURE_CLIENT_ID=${AZURE_CLIENT_ID}"
        "-e" "AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}"
    )
    
    # Only set GOOGLE_APPLICATION_CREDENTIALS if file exists and was mounted
    if [ -n "${GOOGLE_APPLICATION_CREDENTIALS}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
        env_vars+=("-e" "GOOGLE_APPLICATION_CREDENTIALS=${GOOGLE_APPLICATION_CREDENTIALS}")
    fi
    
    # Run Docker container
    log_info "Starting benchmark container..."
    log_info "Cloud: ${cloud}"
    log_info "Machine Type: ${machine_type}"
    log_info "Duration: ${duration}s"
    
    if [ "${do_shell}" = true ]; then
        log_info "Starting interactive shell..."
        docker run --rm -it \
            "${volumes[@]}" \
            "${env_vars[@]}" \
            "${IMAGE_NAME}" \
            /bin/bash
    else
        docker run --rm -it \
            "${volumes[@]}" \
            "${env_vars[@]}" \
            "${IMAGE_NAME}" \
            --cloud "${cloud}" \
            --machine-type "${machine_type}" \
            --duration "${duration}" \
            "${extra_args[@]}"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Benchmark completed successfully!"
        log_info "Results saved to: ${SCRIPT_DIR}/benchmarks/"
    else
        log_error "Benchmark failed!"
        exit 1
    fi
}

# Run main function
main "$@"
