"""
Machine Type Specifications

Provides detailed specifications for cloud machine types across providers.
This helps in normalizing benchmark results and providing context.
"""

# GCP Machine Type Specifications
# Reference: https://cloud.google.com/compute/docs/machine-resource
GCP_MACHINE_SPECS = {
    # N2 Series - Intel Ice Lake
    'n2-standard-2': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 2,
        'memory_gb': 8,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 10,
    },
    'n2-standard-4': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 4,
        'memory_gb': 16,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 10,
    },
    'n2-standard-8': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 8,
        'memory_gb': 32,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 16,
    },
    'n2-standard-16': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 16,
        'memory_gb': 64,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 32,
    },
    'n2-standard-32': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 32,
        'memory_gb': 128,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 32,
    },
    'n2-standard-48': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 48,
        'memory_gb': 192,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 32,
    },
    'n2-standard-64': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 64,
        'memory_gb': 256,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 32,
    },
    'n2-standard-80': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Ice Lake',
        'vcpus': 80,
        'memory_gb': 320,
        'cpu_platform': 'Intel Ice Lake',
        'max_bandwidth_gbps': 32,
    },
    
    # N2D Series - AMD EPYC Milan
    'n2d-standard-2': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 2,
        'memory_gb': 8,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 10,
    },
    'n2d-standard-4': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 4,
        'memory_gb': 16,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 10,
    },
    'n2d-standard-8': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 8,
        'memory_gb': 32,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 16,
    },
    'n2d-standard-16': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 16,
        'memory_gb': 64,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-32': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 32,
        'memory_gb': 128,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-48': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 48,
        'memory_gb': 192,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-64': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 64,
        'memory_gb': 256,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-80': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 80,
        'memory_gb': 320,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-96': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 96,
        'memory_gb': 384,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-128': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 128,
        'memory_gb': 512,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    'n2d-standard-224': {
        'cpu_vendor': 'amd',
        'cpu_generation': 'EPYC Milan',
        'vcpus': 224,
        'memory_gb': 896,
        'cpu_platform': 'AMD EPYC Milan',
        'max_bandwidth_gbps': 32,
    },
    
    # T2A Series - ARM Ampere Altra
    't2a-standard-1': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 1,
        'memory_gb': 4,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 10,
    },
    't2a-standard-2': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 2,
        'memory_gb': 8,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 10,
    },
    't2a-standard-4': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 4,
        'memory_gb': 16,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 10,
    },
    't2a-standard-8': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 8,
        'memory_gb': 32,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 16,
    },
    't2a-standard-16': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 16,
        'memory_gb': 64,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 32,
    },
    't2a-standard-32': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 32,
        'memory_gb': 128,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 32,
    },
    't2a-standard-48': {
        'cpu_vendor': 'arm',
        'cpu_generation': 'Ampere Altra',
        'vcpus': 48,
        'memory_gb': 192,
        'cpu_platform': 'Ampere Altra',
        'max_bandwidth_gbps': 32,
    },
    
    # N1 Series - Intel Skylake/Broadwell/Haswell (Legacy)
    'n1-standard-2': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 2,
        'memory_gb': 7.5,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 10,
    },
    'n1-standard-4': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 4,
        'memory_gb': 15,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 10,
    },
    'n1-standard-8': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 8,
        'memory_gb': 30,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 16,
    },
    'n1-standard-16': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 16,
        'memory_gb': 60,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 32,
    },
    'n1-standard-32': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 32,
        'memory_gb': 120,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 32,
    },
    'n1-standard-64': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 64,
        'memory_gb': 240,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 32,
    },
    'n1-standard-96': {
        'cpu_vendor': 'intel',
        'cpu_generation': 'Skylake/Broadwell/Haswell',
        'vcpus': 96,
        'memory_gb': 360,
        'cpu_platform': 'Intel Skylake/Broadwell/Haswell',
        'max_bandwidth_gbps': 32,
    },
    
    # E2 Series - Shared Core (Cost-Optimized)
    'e2-standard-2': {
        'cpu_vendor': 'intel/amd',
        'cpu_generation': 'Various',
        'vcpus': 2,
        'memory_gb': 8,
        'cpu_platform': 'Intel/AMD (Cost-Optimized)',
        'max_bandwidth_gbps': 4,
    },
    'e2-standard-4': {
        'cpu_vendor': 'intel/amd',
        'cpu_generation': 'Various',
        'vcpus': 4,
        'memory_gb': 16,
        'cpu_platform': 'Intel/AMD (Cost-Optimized)',
        'max_bandwidth_gbps': 8,
    },
    'e2-standard-8': {
        'cpu_vendor': 'intel/amd',
        'cpu_generation': 'Various',
        'vcpus': 8,
        'memory_gb': 32,
        'cpu_platform': 'Intel/AMD (Cost-Optimized)',
        'max_bandwidth_gbps': 16,
    },
    'e2-standard-16': {
        'cpu_vendor': 'intel/amd',
        'cpu_generation': 'Various',
        'vcpus': 16,
        'memory_gb': 64,
        'cpu_platform': 'Intel/AMD (Cost-Optimized)',
        'max_bandwidth_gbps': 16,
    },
    'e2-standard-32': {
        'cpu_vendor': 'intel/amd',
        'cpu_generation': 'Various',
        'vcpus': 32,
        'memory_gb': 128,
        'cpu_platform': 'Intel/AMD (Cost-Optimized)',
        'max_bandwidth_gbps': 16,
    },
}


def get_machine_specs(machine_type, cloud='gcp'):
    """
    Get specifications for a given machine type.
    
    Args:
        machine_type: Machine type identifier (e.g., 'n2-standard-4')
        cloud: Cloud provider ('gcp', 'aws', 'azure')
        
    Returns:
        Dictionary with machine specifications, or None if not found
    """
    if cloud == 'gcp':
        return GCP_MACHINE_SPECS.get(machine_type)
    # Future: Add AWS and Azure mappings
    return None


def enrich_cluster_info(cluster_info, config):
    """
    Enrich cluster info with machine type specifications.
    
    Args:
        cluster_info: Basic cluster information
        config: Pipeline configuration
        
    Returns:
        Enhanced cluster info with machine specs
    """
    machine_type = config.get('machine_type') or cluster_info.get('machine_type')
    cloud = config.get('cloud', 'gcp')
    
    specs = get_machine_specs(machine_type, cloud)
    
    if specs:
        cluster_info['machine_specs'] = {
            'vcpus': specs['vcpus'],
            'memory_gb': specs['memory_gb'],
            'cpu_platform': specs['cpu_platform'],
            'max_bandwidth_gbps': specs['max_bandwidth_gbps'],
        }
        
        # Override CPU vendor/generation if not provided
        if not cluster_info.get('cpu_vendor'):
            cluster_info['cpu_vendor'] = specs['cpu_vendor']
        if not cluster_info.get('cpu_generation'):
            cluster_info['cpu_generation'] = specs['cpu_generation']
    
    return cluster_info
