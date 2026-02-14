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
  --users-count <count>  Number of concurrent users - default: 100
  --rps <rps>            Requests per second - default: 50
  --build                Build Docker image before running
  --shell                Start interactive shell instead of benchmark

${GREEN}Environment Variables:${NC}
  GCP:
    GCP_PROJECT_ID       Google Cloud Project ID (required)
    
  For GCP authentication, place service account key at: ./key.json
  
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
  $0 gcp n2-standard-4 60 --cleanup

  # Run with custom load
  $0 gcp n2-standard-4 300 --users-count 300 --rps 50 --cleanup

  # Build image first, then run
  $0 gcp n2-standard-4 600 --build --cleanup

  # Interactive shell for debugging
  $0 gcp n2-standard-4 600 --shell

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

# Check credentials
check_credentials() {
    local cloud=$1
    
    case ${cloud} in
        gcp)
            if [ -z "${GCP_PROJECT_ID}" ]; then
                log_error "GCP_PROJECT_ID environment variable is required"
                log_error "Export it: export GCP_PROJECT_ID=your-project-id"
                exit 1
            fi
            
            if [ ! -f "${SCRIPT_DIR}/key.json" ]; then
                log_error "GCP service account key not found at: ${SCRIPT_DIR}/key.json"
                log_error "Place your service account key at ./key.json"
                exit 1
            fi
            
            log_info "Using GCP credentials from: ${SCRIPT_DIR}/key.json"
            ;;
        aws)
            if [ -z "${AWS_ACCESS_KEY_ID}" ] || [ -z "${AWS_SECRET_ACCESS_KEY}" ]; then
                log_error "AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are required"
                exit 1
            fi
            log_info "Using AWS credentials from environment"
            ;;
        azure)
            if [ -z "${AZURE_SUBSCRIPTION_ID}" ]; then
                log_error "AZURE_SUBSCRIPTION_ID is required"
                exit 1
            fi
            log_info "Using Azure credentials from environment"
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
    local do_shell=false
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            --build)
                do_build=true
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
    
    # Check credentials
    check_credentials "${cloud}"
    
    # Prepare Docker volumes
    local volumes=(
        "-v" "${SCRIPT_DIR}/key.json:/root/.gcp/service-account-key.json:ro"
        "-v" "${SCRIPT_DIR}/benchmarks:/workspace/benchmarks"
    )
    
    # Prepare environment variables
    local env_vars=(
        "-e" "GCP_PROJECT_ID=${GCP_PROJECT_ID}"
    )
    
    # Add AWS/Azure env vars if needed
    if [ "${cloud}" = "aws" ]; then
        env_vars+=(
            "-e" "AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}"
            "-e" "AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}"
            "-e" "AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-west-2}"
        )
    elif [ "${cloud}" = "azure" ]; then
        env_vars+=(
            "-e" "AZURE_SUBSCRIPTION_ID=${AZURE_SUBSCRIPTION_ID}"
            "-e" "AZURE_TENANT_ID=${AZURE_TENANT_ID}"
            "-e" "AZURE_CLIENT_ID=${AZURE_CLIENT_ID}"
            "-e" "AZURE_CLIENT_SECRET=${AZURE_CLIENT_SECRET}"
        )
    fi
    
    # Run Docker container
    log_info "Starting benchmark container..."
    log_info "Cloud: ${cloud}"
    log_info "Machine Type: ${machine_type}"
    log_info "Duration: ${duration}s"
    echo ""
    
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
    
    local exit_code=$?
    echo ""
    
    if [ ${exit_code} -eq 0 ]; then
        log_success "Benchmark completed successfully!"
        log_info "Results saved to: ${SCRIPT_DIR}/benchmarks/"
    else
        log_error "Benchmark failed with exit code: ${exit_code}"
        exit ${exit_code}
    fi
}

# Run main function
main "$@"
