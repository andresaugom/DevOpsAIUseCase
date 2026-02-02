"""
Benchmark Runner Module

Handles benchmark execution and timing.
"""

import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class BenchmarkRunner:
    """Runs the actual benchmark test"""
    
    def __init__(self, config):
        self.config = config
        
    def run_benchmark(self, duration):
        """
        Run benchmark for specified duration.
        
        The load generator is already running (deployed via Helm),
        so this simply waits for the specified duration while
        metrics are being collected.
        
        Args:
            duration: Duration in seconds
            
        Returns:
            Dictionary with start_time and end_time
        """
        logger.info(f"Running benchmark for {duration} seconds...")
        
        start_time = datetime.now()
        
        # Log progress periodically
        elapsed = 0
        log_interval = 60  # Log every minute
        
        while elapsed < duration:
            time.sleep(min(log_interval, duration - elapsed))
            elapsed += log_interval
            
            if elapsed < duration:
                remaining = duration - elapsed
                logger.info(f"Benchmark in progress... {remaining}s remaining")
        
        end_time = datetime.now()
        
        logger.info("Benchmark completed")
        
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration
        }
