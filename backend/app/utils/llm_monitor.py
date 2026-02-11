"""LLM monitoring utilities for tracking API calls and performance."""
import time
from typing import Dict, List
from datetime import datetime
from contextlib import contextmanager


class LLMMonitor:
    """Monitor LLM API calls and performance metrics."""
    
    def __init__(self):
        self.total_calls = 0
        self.total_response_time = 0.0
        self.call_history: List[Dict] = []
        self.start_time = datetime.now()
    
    @contextmanager
    def track_call(self, operation: str = "llm_call"):
        """Context manager to track a single LLM call."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.total_calls += 1
            self.total_response_time += duration
            
            call_info = {
                "operation": operation,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            self.call_history.append(call_info)
            
            # Print to terminal
            avg_time = self.total_response_time / self.total_calls
            print(f"\n{'='*60}")
            print(f"🤖 LLM API Call #{self.total_calls}")
            print(f"   Operation: {operation}")
            print(f"   Response Time: {duration:.2f}s")
            print(f"   Average Response Time: {avg_time:.2f}s")
            print(f"   Total Calls: {self.total_calls}")
            print(f"{'='*60}\n")
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        avg_time = self.total_response_time / self.total_calls if self.total_calls > 0 else 0
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_calls": self.total_calls,
            "total_response_time": round(self.total_response_time, 2),
            "average_response_time": round(avg_time, 2),
            "uptime_seconds": round(uptime, 2),
            "calls_per_minute": round((self.total_calls / uptime) * 60, 2) if uptime > 0 else 0
        }
    
    def print_summary(self):
        """Print a summary of all statistics."""
        stats = self.get_stats()
        print("\n" + "="*60)
        print("📊 LLM API MONITORING SUMMARY")
        print("="*60)
        print(f"Total API Calls:        {stats['total_calls']}")
        print(f"Total Response Time:    {stats['total_response_time']}s")
        print(f"Average Response Time:  {stats['average_response_time']}s")
        print(f"Uptime:                 {stats['uptime_seconds']}s")
        print(f"Calls per Minute:       {stats['calls_per_minute']}")
        print("="*60 + "\n")


# Global monitor instance
llm_monitor = LLMMonitor()
