# Azure AKS Configuration - Template for Future Implementation

# This is a template structure for implementing Azure AKS support.
# The implementation should follow the same principles as the GCP configuration:
# - Fixed VM sizes
# - Disabled autoscaling
# - Node labels for CPU vendor/generation
# - Single availability zone

# TODO: Implement similar to GCP configuration with:
# - AKS cluster resource
# - AKS node pool with fixed VM size
# - Node labels for workload, vm_size, cpu_vendor, cpu_generation
# - Outputs for cluster access

# Example VM sizes to support:
# - Standard_D4s_v3 (Intel Xeon E5-2673 v4 - Broadwell)
# - Standard_D4s_v5 (Intel Xeon Platinum 8370C - Ice Lake)
# - Standard_D4as_v4 (AMD EPYC 7763 - Milan)
# - Standard_D4ps_v5 (ARM-based Ampere Altra)
