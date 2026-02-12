"""
Prometheus Client Module

Handles querying metrics from Prometheus with enhanced per-pod and per-node collection.
"""

import logging
import requests
from datetime import datetime, timedelta
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Client for querying Prometheus metrics with enhanced granularity"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.get('prometheus_url', 'http://prometheus-operated.monitoring.svc:9090')
        self.namespace = config.get('namespace', 'default')
        
    def collect_metrics(self, start_time, end_time):
        """
        Collect comprehensive benchmark metrics from Prometheus.
        
        This enhanced version collects:
        - Cluster-wide aggregate metrics
        - Per-pod metrics for detailed analysis
        - Per-node metrics for infrastructure insights
        - Service-level metrics
        
        Returns:
            Dictionary with structured metrics including cluster, pod, node, and service levels
        """
        logger.info("Collecting comprehensive metrics from Prometheus...")
        
        metrics = {
            'cluster': {},
            'pods': [],
            'nodes': [],
            'services': {},
            'collection_metadata': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_seconds': (end_time - start_time).total_seconds(),
                'namespace': self.namespace
            }
        }
        
        # Collect cluster-wide aggregate metrics
        logger.info("Collecting cluster-wide metrics...")
        metrics['cluster'] = self._collect_cluster_metrics(start_time, end_time)
        
        # Collect per-pod metrics
        logger.info("Collecting per-pod metrics...")
        metrics['pods'] = self._collect_pod_metrics(start_time, end_time)
        
        # Collect per-node metrics
        logger.info("Collecting per-node metrics...")
        metrics['nodes'] = self._collect_node_metrics(start_time, end_time)
        
        # Collect service-level metrics
        logger.info("Collecting service-level metrics...")
        metrics['services'] = self._collect_service_metrics(start_time, end_time)
        
        # Add summary statistics
        metrics['summary'] = self._generate_summary_stats(metrics)
        
        logger.info(f"Collected metrics for {len(metrics['pods'])} pods and {len(metrics['nodes'])} nodes")
        
        return metrics
    
    def _collect_cluster_metrics(self, start_time, end_time):
        """Collect cluster-wide aggregate metrics"""
        cluster_queries = {
            'avg_cpu_utilization': self._get_avg_cpu_query(),
            'max_cpu_utilization': self._get_max_cpu_query(),
            'p95_cpu_utilization': self._get_p95_cpu_query(),
            'p99_cpu_utilization': self._get_p99_cpu_query(),
            'cpu_throttled_seconds': self._get_cpu_throttled_query(),
            'cpu_throttled_percentage': self._get_cpu_throttled_percentage_query(),
            'avg_memory_mb': self._get_avg_memory_query(),
            'max_memory_mb': self._get_max_memory_query(),
            'avg_memory_utilization_pct': self._get_memory_utilization_query(),
            'request_rate_rps': self._get_request_rate_query(),
            'total_network_received_mb': self._get_network_received_query(),
            'total_network_transmitted_mb': self._get_network_transmitted_query(),
        }
        
        cluster_metrics = {}
        for metric_name, query in cluster_queries.items():
            try:
                result = self._query_range(query, start_time, end_time)
                value = self._aggregate_result(result)
                cluster_metrics[metric_name] = round(value, 4) if value is not None else 0.0
                logger.debug(f"Cluster {metric_name}: {cluster_metrics[metric_name]}")
            except Exception as e:
                logger.warning(f"Failed to collect cluster {metric_name}: {e}")
                cluster_metrics[metric_name] = 0.0
        
        return cluster_metrics
    
    def _collect_pod_metrics(self, start_time, end_time):
        """Collect detailed metrics for each pod"""
        pods_data = []
        
        try:
            # Get list of pods
            pod_list_query = f'''
                count by (pod, container) (
                    container_cpu_usage_seconds_total{{
                        namespace="{self.namespace}",
                        container!="",
                        container!="POD"
                    }}
                )
            '''
            pod_list_result = self._query_instant(pod_list_query)
            
            for pod_info in pod_list_result:
                pod_name = pod_info['metric'].get('pod', 'unknown')
                container_name = pod_info['metric'].get('container', 'unknown')
                
                # Collect comprehensive metrics for this pod
                pod_metrics = self._collect_single_pod_metrics(
                    pod_name, container_name, start_time, end_time
                )
                
                if pod_metrics:
                    pods_data.append(pod_metrics)
                    
        except Exception as e:
            logger.error(f"Failed to collect pod metrics: {e}")
        
        return pods_data
    
    def _collect_single_pod_metrics(self, pod_name, container_name, start_time, end_time):
        """Collect metrics for a single pod"""
        try:
            pod_data = {
                'pod_name': pod_name,
                'container_name': container_name,
                'metrics': {}
            }
            
            # CPU metrics
            cpu_query = f'''
                rate(container_cpu_usage_seconds_total{{
                    namespace="{self.namespace}",
                    pod="{pod_name}",
                    container="{container_name}"
                }}[5m]) * 100
            '''
            cpu_result = self._query_range(cpu_query, start_time, end_time)
            cpu_values = self._extract_all_values(cpu_result)
            
            if cpu_values:
                pod_data['metrics']['cpu'] = {
                    'avg_utilization_pct': round(mean(cpu_values), 4),
                    'max_utilization_pct': round(max(cpu_values), 4),
                    'min_utilization_pct': round(min(cpu_values), 4),
                    'p95_utilization_pct': round(self._percentile(cpu_values, 95), 4),
                    'p99_utilization_pct': round(self._percentile(cpu_values, 99), 4),
                    'std_dev': round(stdev(cpu_values), 4) if len(cpu_values) > 1 else 0.0,
                }
            
            # CPU Throttling
            throttle_query = f'''
                rate(container_cpu_cfs_throttled_seconds_total{{
                    namespace="{self.namespace}",
                    pod="{pod_name}",
                    container="{container_name}"
                }}[5m])
            '''
            throttle_result = self._query_range(throttle_query, start_time, end_time)
            throttle_values = self._extract_all_values(throttle_result)
            
            if throttle_values:
                pod_data['metrics']['cpu_throttling'] = {
                    'avg_throttled_seconds': round(mean(throttle_values), 4),
                    'max_throttled_seconds': round(max(throttle_values), 4),
                    'total_throttled_seconds': round(sum(throttle_values), 4),
                }
            
            # Memory metrics
            memory_query = f'''
                container_memory_working_set_bytes{{
                    namespace="{self.namespace}",
                    pod="{pod_name}",
                    container="{container_name}"
                }} / 1024 / 1024
            '''
            memory_result = self._query_range(memory_query, start_time, end_time)
            memory_values = self._extract_all_values(memory_result)
            
            if memory_values:
                pod_data['metrics']['memory'] = {
                    'avg_usage_mb': round(mean(memory_values), 4),
                    'max_usage_mb': round(max(memory_values), 4),
                    'min_usage_mb': round(min(memory_values), 4),
                    'p95_usage_mb': round(self._percentile(memory_values, 95), 4),
                }
            
            # CPU and Memory limits/requests
            limits_query = f'''
                container_spec_cpu_quota{{
                    namespace="{self.namespace}",
                    pod="{pod_name}",
                    container="{container_name}"
                }} / 100000
            '''
            limits_result = self._query_instant(limits_query)
            if limits_result and limits_result[0].get('value'):
                cpu_limit = float(limits_result[0]['value'][1])
                pod_data['resource_limits'] = {
                    'cpu_limit_cores': round(cpu_limit, 2)
                }
            
            return pod_data
            
        except Exception as e:
            logger.warning(f"Failed to collect metrics for pod {pod_name}: {e}")
            return None
    
    def _collect_node_metrics(self, start_time, end_time):
        """Collect metrics for each node"""
        nodes_data = []
        
        try:
            # Get list of nodes
            node_list_query = 'count by (node) (kube_node_info)'
            node_list_result = self._query_instant(node_list_query)
            
            for node_info in node_list_result:
                node_name = node_info['metric'].get('node', 'unknown')
                
                node_metrics = self._collect_single_node_metrics(
                    node_name, start_time, end_time
                )
                
                if node_metrics:
                    nodes_data.append(node_metrics)
                    
        except Exception as e:
            logger.error(f"Failed to collect node metrics: {e}")
        
        return nodes_data
    
    def _collect_single_node_metrics(self, node_name, start_time, end_time):
        """Collect metrics for a single node"""
        try:
            node_data = {
                'node_name': node_name,
                'metrics': {}
            }
            
            # Node CPU utilization
            node_cpu_query = f'''
                100 - (avg by (instance) (
                    irate(node_cpu_seconds_total{{mode="idle", instance=~".*{node_name}.*"}}[5m]) * 100
                ))
            '''
            cpu_result = self._query_range(node_cpu_query, start_time, end_time)
            cpu_values = self._extract_all_values(cpu_result)
            
            if cpu_values:
                node_data['metrics']['cpu'] = {
                    'avg_utilization_pct': round(mean(cpu_values), 4),
                    'max_utilization_pct': round(max(cpu_values), 4),
                    'min_utilization_pct': round(min(cpu_values), 4),
                }
            
            # Node memory
            node_memory_query = f'''
                (node_memory_MemTotal_bytes{{instance=~".*{node_name}.*"}} - 
                 node_memory_MemAvailable_bytes{{instance=~".*{node_name}.*"}}) / 
                node_memory_MemTotal_bytes{{instance=~".*{node_name}.*"}} * 100
            '''
            memory_result = self._query_range(node_memory_query, start_time, end_time)
            memory_values = self._extract_all_values(memory_result)
            
            if memory_values:
                node_data['metrics']['memory'] = {
                    'avg_utilization_pct': round(mean(memory_values), 4),
                    'max_utilization_pct': round(max(memory_values), 4),
                    'min_utilization_pct': round(min(memory_values), 4),
                }
            
            return node_data
            
        except Exception as e:
            logger.warning(f"Failed to collect metrics for node {node_name}: {e}")
            return None
    
    def _collect_service_metrics(self, start_time, end_time):
        """Collect service-level metrics for Online Boutique microservices"""
        services = [
            'frontend', 'cartservice', 'productcatalogservice', 'currencyservice',
            'paymentservice', 'shippingservice', 'emailservice', 'checkoutservice',
            'recommendationservice', 'adservice'
        ]
        
        services_data = {}
        
        for service in services:
            try:
                service_data = self._collect_single_service_metrics(
                    service, start_time, end_time
                )
                if service_data:
                    services_data[service] = service_data
            except Exception as e:
                logger.warning(f"Failed to collect metrics for service {service}: {e}")
        
        return services_data
    
    def _collect_single_service_metrics(self, service, start_time, end_time):
        """Collect metrics for a single service"""
        try:
            service_data = {}
            
            # Average CPU across all pods for this service
            service_cpu_query = f'''
                avg(rate(container_cpu_usage_seconds_total{{
                    namespace="{self.namespace}",
                    pod=~"{service}-.*",
                    container="{service}"
                }}[5m])) * 100
            '''
            cpu_result = self._query_range(service_cpu_query, start_time, end_time)
            cpu_values = self._extract_all_values(cpu_result)
            
            if cpu_values:
                service_data['cpu_avg_pct'] = round(mean(cpu_values), 4)
                service_data['cpu_max_pct'] = round(max(cpu_values), 4)
            
            # Memory
            service_memory_query = f'''
                avg(container_memory_working_set_bytes{{
                    namespace="{self.namespace}",
                    pod=~"{service}-.*",
                    container="{service}"
                }}) / 1024 / 1024
            '''
            memory_result = self._query_range(service_memory_query, start_time, end_time)
            memory_values = self._extract_all_values(memory_result)
            
            if memory_values:
                service_data['memory_avg_mb'] = round(mean(memory_values), 4)
                service_data['memory_max_mb'] = round(max(memory_values), 4)
            
            return service_data if service_data else None
            
        except Exception as e:
            logger.debug(f"Service {service} metrics not available: {e}")
            return None
    
    def _generate_summary_stats(self, metrics):
        """Generate summary statistics from collected metrics"""
        summary = {
            'total_pods': len(metrics['pods']),
            'total_nodes': len(metrics['nodes']),
            'total_services': len(metrics['services']),
        }
        
        # Calculate pod-level statistics
        if metrics['pods']:
            cpu_avgs = [p['metrics']['cpu']['avg_utilization_pct'] 
                       for p in metrics['pods'] 
                       if 'cpu' in p.get('metrics', {})]
            
            if cpu_avgs:
                summary['pod_cpu_stats'] = {
                    'mean': round(mean(cpu_avgs), 4),
                    'median': round(median(cpu_avgs), 4),
                    'max': round(max(cpu_avgs), 4),
                    'min': round(min(cpu_avgs), 4),
                }
            
            memory_avgs = [p['metrics']['memory']['avg_usage_mb'] 
                          for p in metrics['pods'] 
                          if 'memory' in p.get('metrics', {})]
            
            if memory_avgs:
                summary['pod_memory_stats'] = {
                    'mean_mb': round(mean(memory_avgs), 4),
                    'median_mb': round(median(memory_avgs), 4),
                    'max_mb': round(max(memory_avgs), 4),
                    'min_mb': round(min(memory_avgs), 4),
                }
        
        return summary
    
    def _query_range(self, query, start_time, end_time, step='15s'):
        """Execute a Prometheus range query"""
        url = f"{self.base_url}/api/v1/query_range"
        
        params = {
            'query': query,
            'start': start_time.timestamp(),
            'end': end_time.timestamp(),
            'step': step
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'success':
                raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
            
            return data['data']['result']
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to execute query: {query[:100]}... Error: {e}")
            return []
    
    def _query_instant(self, query, time=None):
        """Execute an instant Prometheus query"""
        url = f"{self.base_url}/api/v1/query"
        
        params = {'query': query}
        if time:
            params['time'] = time.timestamp()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data['status'] != 'success':
                raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
            
            return data['data']['result']
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to execute instant query: {query[:100]}... Error: {e}")
            return []
    
    def _aggregate_result(self, result):
        """Aggregate Prometheus query result (backward compatible)"""
        if not result:
            return None
        
        values = self._extract_all_values(result)
        return mean(values) if values else None
    
    def _extract_all_values(self, result):
        """Extract all numeric values from a Prometheus query result"""
        values = []
        
        if not result:
            return values
        
        for series in result:
            # Handle range query results with 'values'
            if 'values' in series:
                for timestamp, value in series['values']:
                    try:
                        values.append(float(value))
                    except (ValueError, TypeError):
                        continue
            # Handle instant query results with 'value'
            elif 'value' in series:
                try:
                    values.append(float(series['value'][1]))
                except (ValueError, TypeError, IndexError):
                    continue
        
        return values
    
    def _percentile(self, values, percentile):
        """Calculate percentile of a list of values"""
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower = sorted_values[int(index)]
            upper = sorted_values[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    # Query definitions for cluster-wide metrics
    def _get_avg_cpu_query(self):
        """Get query for average CPU utilization"""
        return f'''
            avg(rate(container_cpu_usage_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) * 100
        '''
    
    def _get_max_cpu_query(self):
        """Get query for maximum CPU utilization"""
        return f'''
            max(rate(container_cpu_usage_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) * 100
        '''
    
    def _get_p95_cpu_query(self):
        """Get query for P95 CPU utilization"""
        return f'''
            quantile(0.95, rate(container_cpu_usage_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) * 100
        '''
    
    def _get_p99_cpu_query(self):
        """Get query for P99 CPU utilization"""
        return f'''
            quantile(0.99, rate(container_cpu_usage_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) * 100
        '''
    
    def _get_cpu_throttled_query(self):
        """Get query for CPU throttling"""
        return f'''
            sum(rate(container_cpu_cfs_throttled_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m]))
        '''
    
    def _get_cpu_throttled_percentage_query(self):
        """Get query for CPU throttling percentage"""
        return f'''
            sum(rate(container_cpu_cfs_throttled_seconds_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) / 
            sum(rate(container_cpu_cfs_periods_total{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}[5m])) * 100
        '''
    
    def _get_avg_memory_query(self):
        """Get query for average memory usage"""
        return f'''
            avg(container_memory_working_set_bytes{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}) / 1024 / 1024
        '''
    
    def _get_max_memory_query(self):
        """Get query for maximum memory usage"""
        return f'''
            max(container_memory_working_set_bytes{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}) / 1024 / 1024
        '''
    
    def _get_memory_utilization_query(self):
        """Get query for memory utilization percentage"""
        return f'''
            avg(container_memory_working_set_bytes{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }} / container_spec_memory_limit_bytes{{
                namespace="{self.namespace}",
                container!="",
                container!="POD"
            }}) * 100
        '''
    
    def _get_request_rate_query(self):
        """Get query for request rate (if available)"""
        # This assumes the application exposes request metrics
        return f'''
            sum(rate(http_requests_total{{namespace="{self.namespace}"}}[5m]))
        '''
    
    def _get_network_received_query(self):
        """Get query for total network received"""
        return f'''
            sum(rate(container_network_receive_bytes_total{{
                namespace="{self.namespace}"
            }}[5m])) / 1024 / 1024
        '''
    
    def _get_network_transmitted_query(self):
        """Get query for total network transmitted"""
        return f'''
            sum(rate(container_network_transmit_bytes_total{{
                namespace="{self.namespace}"
            }}[5m])) / 1024 / 1024
        '''
