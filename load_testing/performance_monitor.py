#!/usr/bin/env python3
"""
Real-time Performance Monitor
Monitors the Streamlit app performance during load testing
"""

import time
import psutil
import requests
import threading
import json
import csv
from datetime import datetime
from pathlib import Path
import argparse
import signal
import sys


class PerformanceMonitor:
    def __init__(self, app_url="http://localhost:8515", interval=1.0):
        self.app_url = app_url
        self.interval = interval
        self.monitoring = False
        self.metrics = []
        self.start_time = None
        
        # Create monitoring directory
        self.results_dir = Path("load_testing/performance_monitoring")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print("\n🔴 Stopping performance monitoring...")
        self.stop_monitoring()
        sys.exit(0)
    
    def get_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=None)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_gb = memory.used / (1024**3)
            memory_total_gb = memory.total / (1024**3)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            disk_read_mb = disk_io.read_bytes / (1024**2) if disk_io else 0
            disk_write_mb = disk_io.write_bytes / (1024**2) if disk_io else 0
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_sent_mb = network_io.bytes_sent / (1024**2) if network_io else 0
            network_recv_mb = network_io.bytes_recv / (1024**2) if network_io else 0
            
            # Process-specific metrics (try to find Python/Streamlit process)
            streamlit_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    if 'python' in proc.info['name'].lower() or 'streamlit' in ' '.join(proc.cmdline()).lower():
                        streamlit_processes.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Aggregate Streamlit process metrics
            streamlit_cpu = sum(proc.cpu_percent() for proc in streamlit_processes)
            streamlit_memory = sum(proc.memory_percent() for proc in streamlit_processes)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'elapsed_time': time.time() - self.start_time if self.start_time else 0,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'disk_read_mb': disk_read_mb,
                'disk_write_mb': disk_write_mb,
                'network_sent_mb': network_sent_mb,
                'network_recv_mb': network_recv_mb,
                'streamlit_cpu_percent': streamlit_cpu,
                'streamlit_memory_percent': streamlit_memory,
                'streamlit_process_count': len(streamlit_processes)
            }
        except Exception as e:
            print(f"⚠️ Error collecting system metrics: {e}")
            return None
    
    def test_app_response(self):
        """Test application response time and availability."""
        try:
            start_time = time.time()
            response = requests.get(self.app_url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'app_available': response.status_code == 200,
                'response_time_ms': response_time,
                'status_code': response.status_code,
                'response_size_bytes': len(response.content) if response.content else 0
            }
        except requests.exceptions.Timeout:
            return {
                'app_available': False,
                'response_time_ms': 10000,  # Timeout threshold
                'status_code': 0,
                'response_size_bytes': 0,
                'error': 'timeout'
            }
        except Exception as e:
            return {
                'app_available': False,
                'response_time_ms': 0,
                'status_code': 0,
                'response_size_bytes': 0,
                'error': str(e)
            }
    
    def monitor_performance(self):
        """Main monitoring loop."""
        print(f"🔍 Starting performance monitoring...")
        print(f"📊 Monitoring URL: {self.app_url}")
        print(f"⏱️ Sampling interval: {self.interval} seconds")
        print("📈 Metrics: CPU, Memory, Disk I/O, Network I/O, App Response Time")
        print("🔴 Press Ctrl+C to stop monitoring")
        print("=" * 60)
        
        self.start_time = time.time()
        self.monitoring = True
        
        # Print header
        print(f"{'Time':<8} {'CPU%':<6} {'Mem%':<6} {'App(ms)':<8} {'Status':<8} {'StreamlitCPU%':<12}")
        print("-" * 60)
        
        while self.monitoring:
            try:
                # Collect metrics
                system_metrics = self.get_system_metrics()
                app_metrics = self.test_app_response()
                
                if system_metrics and app_metrics:
                    # Combine metrics
                    combined_metrics = {**system_metrics, **app_metrics}
                    self.metrics.append(combined_metrics)
                    
                    # Real-time display
                    elapsed = int(combined_metrics['elapsed_time'])
                    cpu = combined_metrics['cpu_percent']
                    memory = combined_metrics['memory_percent']
                    response_time = combined_metrics['response_time_ms']
                    status = "✅" if combined_metrics['app_available'] else "❌"
                    streamlit_cpu = combined_metrics['streamlit_cpu_percent']
                    
                    print(f"{elapsed:<8} {cpu:<6.1f} {memory:<6.1f} {response_time:<8.1f} {status:<8} {streamlit_cpu:<12.1f}")
                    
                    # Alert on high metrics
                    if cpu > 80:
                        print(f"⚠️ HIGH CPU: {cpu:.1f}%")
                    if memory > 80:
                        print(f"⚠️ HIGH MEMORY: {memory:.1f}%")
                    if response_time > 5000:
                        print(f"🐌 SLOW RESPONSE: {response_time:.1f}ms")
                    if not combined_metrics['app_available']:
                        print(f"🔥 APP UNAVAILABLE!")
                
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(self.interval)
        
        self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop monitoring and save results."""
        self.monitoring = False
        
        if not self.metrics:
            print("⚠️ No metrics collected")
            return
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save as JSON
        json_file = self.results_dir / f"performance_metrics_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        # Save as CSV
        csv_file = self.results_dir / f"performance_metrics_{timestamp}.csv"
        if self.metrics:
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.metrics[0].keys())
                writer.writeheader()
                writer.writerows(self.metrics)
        
        # Generate summary
        self.generate_summary(timestamp)
        
        print(f"\n📊 Performance monitoring stopped")
        print(f"💾 Results saved:")
        print(f"   JSON: {json_file}")
        print(f"   CSV: {csv_file}")
    
    def generate_summary(self, timestamp):
        """Generate performance summary."""
        if not self.metrics:
            return
        
        # Calculate statistics
        cpu_values = [m['cpu_percent'] for m in self.metrics if m.get('cpu_percent')]
        memory_values = [m['memory_percent'] for m in self.metrics if m.get('memory_percent')]
        response_times = [m['response_time_ms'] for m in self.metrics if m.get('response_time_ms')]
        availability = [m['app_available'] for m in self.metrics if 'app_available' in m]
        
        summary = {
            'test_duration_seconds': self.metrics[-1]['elapsed_time'] if self.metrics else 0,
            'total_samples': len(self.metrics),
            'cpu_stats': {
                'avg': sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                'max': max(cpu_values) if cpu_values else 0,
                'min': min(cpu_values) if cpu_values else 0
            },
            'memory_stats': {
                'avg': sum(memory_values) / len(memory_values) if memory_values else 0,
                'max': max(memory_values) if memory_values else 0,
                'min': min(memory_values) if memory_values else 0
            },
            'response_time_stats': {
                'avg_ms': sum(response_times) / len(response_times) if response_times else 0,
                'max_ms': max(response_times) if response_times else 0,
                'min_ms': min(response_times) if response_times else 0
            },
            'availability_stats': {
                'uptime_percentage': (sum(availability) / len(availability) * 100) if availability else 0,
                'total_downtime_samples': len(availability) - sum(availability) if availability else 0
            }
        }
        
        # Save summary
        summary_file = self.results_dir / f"performance_summary_{timestamp}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print(f"\n📈 Performance Summary:")
        print(f"   Duration: {summary['test_duration_seconds']:.1f} seconds")
        print(f"   Samples: {summary['total_samples']}")
        print(f"   CPU: Avg {summary['cpu_stats']['avg']:.1f}%, Max {summary['cpu_stats']['max']:.1f}%")
        print(f"   Memory: Avg {summary['memory_stats']['avg']:.1f}%, Max {summary['memory_stats']['max']:.1f}%")
        print(f"   Response Time: Avg {summary['response_time_stats']['avg_ms']:.1f}ms, Max {summary['response_time_stats']['max_ms']:.1f}ms")
        print(f"   Uptime: {summary['availability_stats']['uptime_percentage']:.1f}%")
        print(f"   Summary saved: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Monitor Furniture AI app performance during load testing")
    parser.add_argument("--url", default="http://localhost:8515", help="App URL to monitor")
    parser.add_argument("--interval", type=float, default=1.0, help="Monitoring interval in seconds")
    parser.add_argument("--duration", type=int, help="Monitoring duration in seconds (optional)")
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(app_url=args.url, interval=args.interval)
    
    if args.duration:
        # Run for specified duration
        def stop_after_duration():
            time.sleep(args.duration)
            monitor.stop_monitoring()
        
        timer_thread = threading.Thread(target=stop_after_duration)
        timer_thread.daemon = True
        timer_thread.start()
    
    try:
        monitor.monitor_performance()
    except KeyboardInterrupt:
        print("\n🔴 Monitoring stopped by user")


if __name__ == "__main__":
    main()
