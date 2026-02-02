# Outputs for GCP Kubernetes Cluster

output "cluster_name" {
  description = "Name of the GKE cluster"
  value       = google_container_cluster.benchmark_cluster.name
}

output "cluster_endpoint" {
  description = "Endpoint for the GKE cluster"
  value       = google_container_cluster.benchmark_cluster.endpoint
  sensitive   = true
}

output "cluster_ca_certificate" {
  description = "CA certificate for the GKE cluster"
  value       = google_container_cluster.benchmark_cluster.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

output "region" {
  description = "GCP region"
  value       = var.region
}

output "zone" {
  description = "GCP zone"
  value       = var.zone
}

output "machine_type" {
  description = "Machine type used for nodes"
  value       = var.machine_type
}

output "cpu_vendor" {
  description = "CPU vendor"
  value       = var.cpu_vendor
}

output "cpu_generation" {
  description = "CPU generation"
  value       = var.cpu_generation
}

output "node_count" {
  description = "Number of nodes in the cluster"
  value       = var.node_count
}

output "kubeconfig_command" {
  description = "Command to configure kubectl"
  value       = "gcloud container clusters get-credentials ${google_container_cluster.benchmark_cluster.name} --zone ${var.zone} --project ${var.project_id}"
}
