"""
System Health Monitor
Monitor system performance, resource usage, and health metrics
"""

import psutil
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
import os


class SystemMonitor:
    """Monitor hệ thống real-time performance metrics"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_history = []
        self.max_history = 100  # Keep last 100 metrics
    
    def get_uptime(self) -> timedelta:
        """Tính uptime của hệ thống"""
        return datetime.now() - self.start_time
    
    def get_cpu_usage(self) -> float:
        """CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Memory usage statistics"""
        mem = psutil.virtual_memory()
        return {
            'total_mb': mem.total / (1024 * 1024),
            'available_mb': mem.available / (1024 * 1024),
            'used_mb': mem.used / (1024 * 1024),
            'percent': mem.percent
        }
    
    def get_disk_usage(self, path: str = "data") -> Dict[str, float]:
        """Disk usage for specific path"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        disk = psutil.disk_usage(path)
        return {
            'total_gb': disk.total / (1024 ** 3),
            'used_gb': disk.used / (1024 ** 3),
            'free_gb': disk.free / (1024 ** 3),
            'percent': disk.percent
        }
    
    def get_network_stats(self) -> Dict[str, int]:
        """Network I/O statistics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv
        }
    
    def get_process_info(self) -> Dict[str, float]:
        """Current process resource usage"""
        process = psutil.Process(os.getpid())
        
        return {
            'cpu_percent': process.cpu_percent(interval=0.1),
            'memory_mb': process.memory_info().rss / (1024 * 1024),
            'threads': process.num_threads(),
            'open_files': len(process.open_files()) if hasattr(process, 'open_files') else 0
        }
    
    def get_database_size(self, db_path: str = "data/security.db") -> float:
        """Get database file size in MB"""
        if os.path.exists(db_path):
            return os.path.getsize(db_path) / (1024 * 1024)
        return 0.0
    
    def get_health_status(self) -> Dict[str, any]:
        """Comprehensive health check"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        disk = self.get_disk_usage()
        process = self.get_process_info()
        
        # Determine health status
        health_score = 100
        warnings = []
        
        # CPU check
        if cpu > 80:
            health_score -= 30
            warnings.append(f"High CPU usage: {cpu:.1f}%")
        elif cpu > 50:
            health_score -= 10
            warnings.append(f"Moderate CPU usage: {cpu:.1f}%")
        
        # Memory check
        if memory['percent'] > 85:
            health_score -= 30
            warnings.append(f"High memory usage: {memory['percent']:.1f}%")
        elif memory['percent'] > 70:
            health_score -= 10
            warnings.append(f"Moderate memory usage: {memory['percent']:.1f}%")
        
        # Disk check
        if disk['percent'] > 90:
            health_score -= 20
            warnings.append(f"Low disk space: {disk['free_gb']:.1f}GB free")
        
        # Process check
        if process['memory_mb'] > 500:
            health_score -= 10
            warnings.append(f"High process memory: {process['memory_mb']:.1f}MB")
        
        # Overall status
        if health_score >= 90:
            status = "EXCELLENT"
            status_icon = "🟢"
        elif health_score >= 70:
            status = "GOOD"
            status_icon = "🟡"
        elif health_score >= 50:
            status = "WARNING"
            status_icon = "🟠"
        else:
            status = "CRITICAL"
            status_icon = "🔴"
        
        return {
            'status': status,
            'status_icon': status_icon,
            'health_score': health_score,
            'warnings': warnings,
            'uptime': str(self.get_uptime()).split('.')[0],  # Remove microseconds
            'metrics': {
                'cpu_percent': cpu,
                'memory_percent': memory['percent'],
                'memory_mb': memory['used_mb'],
                'disk_percent': disk['percent'],
                'disk_free_gb': disk['free_gb'],
                'process_memory_mb': process['memory_mb'],
                'process_threads': process['threads']
            }
        }
    
    def log_metrics(self):
        """Log current metrics to history"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage()['percent'],
            'disk': self.get_disk_usage()['percent']
        }
        
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history.pop(0)
    
    def get_metrics_summary(self) -> Dict[str, float]:
        """Get summary statistics from history"""
        if not self.metrics_history:
            return {}
        
        cpu_values = [m['cpu'] for m in self.metrics_history]
        memory_values = [m['memory'] for m in self.metrics_history]
        
        return {
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'max_cpu': max(cpu_values),
            'avg_memory': sum(memory_values) / len(memory_values),
            'max_memory': max(memory_values),
            'samples': len(self.metrics_history)
        }
    
    def print_status(self):
        """Print formatted system status"""
        health = self.get_health_status()
        
        print("\n" + "="*60)
        print(f"{health['status_icon']} SYSTEM HEALTH: {health['status']} ({health['health_score']}/100)")
        print("="*60)
        
        print(f"\n⏱️  Uptime: {health['uptime']}")
        
        metrics = health['metrics']
        print(f"\n📊 Performance Metrics:")
        print(f"  CPU Usage:     {metrics['cpu_percent']:.1f}%")
        print(f"  Memory Usage:  {metrics['memory_percent']:.1f}% ({metrics['memory_mb']:.1f} MB)")
        print(f"  Disk Usage:    {metrics['disk_percent']:.1f}% ({metrics['disk_free_gb']:.1f} GB free)")
        print(f"  Process Mem:   {metrics['process_memory_mb']:.1f} MB")
        print(f"  Threads:       {metrics['process_threads']}")
        
        if health['warnings']:
            print(f"\n⚠️  Warnings:")
            for warning in health['warnings']:
                print(f"  - {warning}")
        
        # Summary statistics
        summary = self.get_metrics_summary()
        if summary:
            print(f"\n📈 Historical Averages ({summary['samples']} samples):")
            print(f"  Avg CPU:       {summary['avg_cpu']:.1f}% (Max: {summary['max_cpu']:.1f}%)")
            print(f"  Avg Memory:    {summary['avg_memory']:.1f}% (Max: {summary['max_memory']:.1f}%)")
        
        print("="*60 + "\n")


# Standalone test
if __name__ == "__main__":
    print("🔍 System Health Monitor - Test")
    print("="*60)
    
    monitor = SystemMonitor()
    
    # Collect metrics for 10 seconds
    print("Collecting metrics for 10 seconds...\n")
    for i in range(10):
        monitor.log_metrics()
        time.sleep(1)
    
    # Print status
    monitor.print_status()
    
    # Database size
    db_size = monitor.get_database_size()
    if db_size > 0:
        print(f"📦 Database Size: {db_size:.2f} MB")
    
    # Network stats
    net = monitor.get_network_stats()
    print(f"\n🌐 Network I/O:")
    print(f"  Sent:     {net['bytes_sent'] / (1024**2):.2f} MB")
    print(f"  Received: {net['bytes_recv'] / (1024**2):.2f} MB")
