# GCP Kubernetes Cluster for Online Boutique Benchmarking
# This configuration provisions a GKE cluster with fixed machine types for reproducible benchmarks

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# GKE Cluster
resource "google_container_cluster" "benchmark_cluster" {
  name     = var.cluster_name
  location = var.zone

  # Disable autoscaling and use a fixed node pool for reproducibility
  remove_default_node_pool = true
  initial_node_count       = 1

  # Network configuration
  network    = "default"
  subnetwork = "default"

  # Disable features that might interfere with benchmarking
  logging_config {
    enable_components = ["SYSTEM_COMPONENTS"]
  }

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS"]
    managed_prometheus {
      enabled = false # We deploy our own Prometheus
    }
  }
}

# Fixed Node Pool for Benchmarking
resource "google_container_node_pool" "benchmark_nodes" {
  name       = "${var.cluster_name}-node-pool"
  location   = var.zone
  cluster    = google_container_cluster.benchmark_cluster.name
  node_count = var.node_count

  node_config {
    machine_type = var.machine_type
    disk_size_gb = 50
    disk_type    = "pd-standard"

    # Labels for node affinity
    labels = {
      workload      = "benchmark"
      machine_type  = replace(var.machine_type, "-", "_")
      cpu_vendor    = var.cpu_vendor
      cpu_generation = var.cpu_generation
    }

    # Scopes for node permissions
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }
  }

  # Disable autoscaling for reproducible benchmarks
  autoscaling {
    min_node_count = var.node_count
    max_node_count = var.node_count
  }

  management {
    auto_repair  = true
    auto_upgrade = false
  }
}
