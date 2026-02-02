# AWS EKS Configuration - Template for Future Implementation

# This is a template structure for implementing AWS EKS support.
# The implementation should follow the same principles as the GCP configuration:
# - Fixed machine types (instance types)
# - Disabled autoscaling
# - Node labels for CPU vendor/generation
# - Single availability zone

# TODO: Implement similar to GCP configuration with:
# - EKS cluster resource
# - EKS node group with fixed instance type
# - Node labels for workload, machine_type, cpu_vendor, cpu_generation
# - Outputs for cluster access

# Example instance types to support:
# - m5.xlarge (Intel Xeon Platinum 8175M - Skylake)
# - m6i.xlarge (Intel Xeon Ice Lake)
# - m6a.xlarge (AMD EPYC 3rd Gen)
# - m7g.xlarge (AWS Graviton3 - ARM)
