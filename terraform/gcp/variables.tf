# Variables for GCP Kubernetes Cluster
#
# NOTE: These variables are automatically configured by the Python orchestrator.
# The orchestrator generates terraform.tfvars dynamically based on CLI arguments.
# You typically don't need to modify these unless running Terraform manually.
# For normal benchmarking, use: python automation/main.py --help

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone for cluster"
  type        = string
  default     = "us-central1-a"
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
  default     = "benchmark-cluster"
}

variable "machine_type" {
  description = "Machine type for nodes (defines CPU generation)"
  type        = string
  default     = "n2-standard-4"
  
  validation {
    condition     = can(regex("^[a-z][0-9]+-", var.machine_type))
    error_message = "Machine type must be a valid GCP machine type (e.g., n2-standard-4)."
  }
}

variable "node_count" {
  description = "Number of nodes in the node pool (fixed for benchmarking)"
  type        = number
  default     = 3
  
  validation {
    condition     = var.node_count >= 3
    error_message = "At least 3 nodes are required for a stable benchmark cluster."
  }
}

variable "cpu_vendor" {
  description = "CPU vendor (intel, amd, or arm)"
  type        = string
  default     = "intel"
  
  validation {
    condition     = contains(["intel", "amd", "arm"], var.cpu_vendor)
    error_message = "CPU vendor must be one of: intel, amd, arm."
  }
}

variable "cpu_generation" {
  description = "CPU generation identifier (e.g., 'Cascade Lake', 'Ice Lake')"
  type        = string
  default     = "Ice Lake"
}
