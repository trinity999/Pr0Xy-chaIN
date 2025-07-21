#!/usr/bin/env python3
"""
ENHANCED Proxy Chain Daemon Status Manager
Advanced status checking, health monitoring, and auto-repair capabilities
"""

import json
import os
import sys
import subprocess
import psutil
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path
try:
    from banner import print_mini_banner, print_status_header, print_status_footer
except ImportError:
    # Fallback if banner module not available
    def print_mini_banner(): pass
    def print_status_header(): pass
    def print_status_footer(): pass

class ProxyDaemonManager:
    def __init__(self):
        self.status_file = "daemon_status.json"
        self.pid_file = "daemon.pid"
        self.lock_file = "daemon.lock"
        self.health_check_url = "http://httpbin.org/ip"
        
    def get_status(self):
        """Get current daemon status"""
        if not os.path.exists(self.status_file):
            return {"status": "not_running", "message": "Daemon not initialized"}
            
        try:
            with open(self.status_file, 'r') as f:
                status = json.load(f)
            return status
        except Exception as e:
            return {"status": "error", "message": f"Error reading status: {e}"}
    
    def is_daemon_running(self):
        """Enhanced daemon process check with validation"""
        if not os.path.exists(self.pid_file):
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                content = f.read().strip()
                if not content.isdigit():
                    return False
                pid = int(content)
                
            # Check if process exists and is our daemon
            if not psutil.pid_exists(pid):
                return False
                
            process = psutil.Process(pid)
            
            # Verify it's actually our Python daemon process
            cmdline = process.cmdline()
            if any("proxy_chain_daemon.py" in arg for arg in cmdline):
                return True
            else:
                # PID file contains wrong process, clean it up
                os.remove(self.pid_file)
                return False
                
        except (ValueError, psutil.NoSuchProcess, PermissionError):
            # Clean up invalid PID file
            if os.path.exists(self.pid_file):
                os.remove(self.pid_file)
            return False
    
    def save_pid(self, pid):
        """Save daemon PID"""
        with open(self.pid_file, 'w') as f:
            f.write(str(pid))
    
    def start_daemon(self, refresh_interval=3600):
        """Start the proxy daemon"""
        if self.is_daemon_running():
            print("🟢 Daemon is already running")
            return False
            
        print("🚀 Starting proxy chain daemon...")
        
        # Start daemon process
        process = subprocess.Popen([
            sys.executable, "proxy_chain_daemon.py",
            "--refresh-interval", str(refresh_interval),
            "--daemon"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
        
        # Save PID
        self.save_pid(process.pid)
        
        print(f"✅ Daemon started with PID {process.pid}")
        return True
    
    def stop_daemon(self):
        """Stop the proxy daemon"""
        if not os.path.exists(self.pid_file):
            print("🔴 No daemon PID found")
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    print(f"✅ Daemon (PID {pid}) stopped gracefully")
                except psutil.TimeoutExpired:
                    process.kill()
                    print(f"⚠️  Daemon (PID {pid}) force killed")
                    
            # Clean up PID file
            os.remove(self.pid_file)
            return True
            
        except Exception as e:
            print(f"❌ Error stopping daemon: {e}")
            return False
    
    def restart_daemon(self, refresh_interval=3600):
        """Restart the proxy daemon"""
        print("🔄 Restarting proxy daemon...")
        self.stop_daemon()
        time.sleep(2)
        self.start_daemon(refresh_interval)
    
    def check_proxy_health(self):
        """Check if proxies are actually working"""
        try:
            if not os.path.exists('working_proxies.txt'):
                return {"working": 0, "total": 0, "health": "no_proxies"}
            
            with open('working_proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            
            if not proxies:
                return {"working": 0, "total": 0, "health": "no_proxies"}
            
            # Test up to 3 proxies for health check
            test_proxies = proxies[:3]
            working_count = 0
            
            for proxy in test_proxies:
                try:
                    proxy_dict = {
                        'http': f'http://{proxy}',
                        'https': f'http://{proxy}'
                    }
                    response = requests.get(
                        self.health_check_url, 
                        proxies=proxy_dict, 
                        timeout=10
                    )
                    if response.status_code == 200:
                        working_count += 1
                except:
                    pass
            
            health_ratio = working_count / len(test_proxies)
            if health_ratio >= 0.7:
                health = "good"
            elif health_ratio >= 0.3:
                health = "fair"
            else:
                health = "poor"
                
            return {
                "working": working_count,
                "tested": len(test_proxies),
                "total": len(proxies),
                "health": health,
                "ratio": round(health_ratio * 100, 1)
            }
            
        except Exception as e:
            return {"working": 0, "total": 0, "health": "error", "error": str(e)}
    
    def get_resource_usage(self):
        """Get daemon process resource usage"""
        try:
            if not os.path.exists(self.pid_file):
                return {"error": "PID file not found"}
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            
            return {
                "cpu_percent": round(process.cpu_percent(), 2),
                "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
                "threads": process.num_threads(),
                "status": process.status(),
                "uptime_seconds": int(time.time() - process.create_time())
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def show_status(self):
        """Display enhanced status with health monitoring"""
        status = self.get_status()
        is_running = self.is_daemon_running()
        
        print("🔗 ENHANCED Proxy Chain Daemon Status")
        print("=" * 50)
        
        # Process Status
        if is_running:
            print("🟢 Process: RUNNING")
        else:
            print("🔴 Process: STOPPED")
        
        # Basic Info
        if status.get('started'):
            try:
                started_time = datetime.fromisoformat(status['started'])
                uptime = datetime.now() - started_time
                print(f"📅 Started: {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"⏱️  Uptime: {str(uptime).split('.')[0]}")
            except:
                print(f"📅 Started: {status['started']}")
        
        # Resource Usage (if running)
        if is_running:
            resources = self.get_resource_usage()
            if "error" not in resources:
                print(f"💾 Memory: {resources['memory_mb']} MB")
                print(f"🖥️  CPU: {resources['cpu_percent']}%")
                print(f"🧵 Threads: {resources['threads']}")
        
        # Proxy Health Check
        health = self.check_proxy_health()
        if "error" not in health:
            print(f"🎯 Proxy Health: {health['health'].upper()}")
            print(f"✅ Working: {health['working']}/{health['total']} ({health.get('ratio', 0)}%)")
        
        # Configuration Status
        print(f"\n📊 Status: {status.get('status', 'unknown')}")
        print(f"🔢 Refreshes: {status.get('total_refreshes', 0)}")
        
        if status.get('last_refresh'):
            print(f"🔄 Last Refresh: {status['last_refresh']}")
        
        # Show proxy list summary
        if os.path.exists('working_proxies.txt'):
            with open('working_proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            print(f"💾 Proxy File: {len(proxies)} proxies available")
            
            if proxies:
                print("📋 Sample proxies:")
                for proxy in proxies[:3]:
                    print(f"   • {proxy}")
                if len(proxies) > 3:
                    print(f"   ... and {len(proxies) - 3} more")
        
        # Show log file info
        if os.path.exists('logs/proxy_daemon.log'):
            stat = os.stat('logs/proxy_daemon.log')
            size_kb = stat.st_size / 1024
            print(f"📝 Log File: {size_kb:.1f} KB")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Proxy Daemon Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status'], 
                       help='Action to perform')
    parser.add_argument('--refresh-interval', type=int, default=3600,
                       help='Proxy refresh interval in seconds (default: 3600)')
    
    args = parser.parse_args()
    
    manager = ProxyDaemonManager()
    
    if args.action == 'start':
        manager.start_daemon(args.refresh_interval)
    elif args.action == 'stop':
        manager.stop_daemon()
    elif args.action == 'restart':
        manager.restart_daemon(args.refresh_interval)
    elif args.action == 'status':
        manager.show_status()

if __name__ == "__main__":
    main()
