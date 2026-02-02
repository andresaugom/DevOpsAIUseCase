"""
Prometheus Client Module

Handles querying metrics from Prometheus.
"""

import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class PrometheusClient:
    """Client for querying Prometheus metrics"""
    
    def __init__(self, config):
        self.config = config
        self.base_url = config.get('prometheus_url', 'http://prometheus-operated.monitoring.svc:9090')
        
    def collect_metrics(self, start_time, end_time):
        """Collect benchmark metrics from Prometheus"""
        logger.info("Collecting metrics from Prometheus...")
        
        metrics = {}
        
        # Define metrics to collect
        queries = {
            'avg_cpu_utilization': self._get_avg_cpu_query(),
            'p95_cpu_utilization': self._get_p95_cpu_query(),
            'cpu_throttled': self._get_cpu_throttled_query(),
            'avg_memory': self._get_avg_memory_query(),
            'request_rate': self._get_request_rate_query(),
        }
        
        for metric_name, query in queries.items():
            try:
                result = self._query_range(query, start_time, end_time)
                metrics[metric_name] = self._aggregate_result(result)
                logger.debug(f"Collected {metric_name}: {metrics[metric_name]}")
            except Exception as e:
                logger.warning(f"Failed to collect {metric_name}: {e}")
                metrics[metric_name] = None
        
        return metrics
    
    def _query_range(self, query, start_time, end_time, step='15s'):
        """Execute a Prometheus range query"""
        url = f"{self.base_url}/api/v1/query_range"
        
        params = {
            'query': query,
            'start': start_time.timestamp(),
            'end': end_time.timestamp(),
            'step': step
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'success':
            raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
        
        return data['data']['result']
    
    def _query_instant(self, query, time=None):
        """Execute an instant Prometheus query"""
        url = f"{self.base_url}/api/v1/query"
        
        params = {'query': query}
        if time:
            params['time'] = time.timestamp()
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        if data['status'] != 'success':
            raise ValueError(f"Query failed: {data.get('error', 'Unknown error')}")
        
        return data['data']['result']
    
    def _aggregate_result(self, result):
        """Aggregate Prometheus query result"""
        if not result:
            return None
        
        # For range queries, calculate average across time series
        values = []
        for series in result:
            if 'values' in series:
                for timestamp, value in series['values']:
                    try:
                        values.append(float(value))
                    except (ValueError, TypeError):
                        continue
        
        if not values:
            return None
        
        return sum(values) / len(values)
    
    def _get_avg_cpu_query(self):
        """Get query for average CPU utilization"""
        return '''
            avg(rate(container_cpu_usage_seconds_total{
                namespace="default",
                container!="",
                container!="POD"
            }[5m])) * 100
        '''
    
    def _get_p95_cpu_query(self):
        """Get query for P95 CPU utilization"""
        return '''
            quantile(0.95, rate(container_cpu_usage_seconds_total{
                namespace="default",
                container!="",
                container!="POD"
            }[5m])) * 100
        '''
    
    def _get_cpu_throttled_query(self):
        """Get query for CPU throttling"""
        return '''
            sum(rate(container_cpu_cfs_throttled_seconds_total{
                namespace="default",
                container!="",
                container!="POD"
            }[5m]))
        '''
    
    def _get_avg_memory_query(self):
        """Get query for average memory usage"""
        return '''
            avg(container_memory_working_set_bytes{
                namespace="default",
                container!="",
                container!="POD"
            }) / 1024 / 1024
        '''
    
    def _get_request_rate_query(self):
        """Get query for request rate (if available)"""
        # This assumes the application exposes request metrics
        return '''
            sum(rate(http_requests_total{namespace="default"}[5m]))
        '''
