#!/usr/bin/env python3
"""
IMPROVED Proxy Chain Daemon Status Manager
Enhanced with better process management, health checks, and error handling
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

class ImprovedProxyDaemonManager:
    def __init__(self):
        self.status_file = "daemon_status.json"
        self.pid_file = "daemon.pid"
        self.lock_file = "daemon.lock"
        self.health_check_url = "http://httpbin.org/ip"
        
    def get_enhanced_status(self):
        """Get detailed daemon status with health checks"""
        base_status = self.get_basic_status()
        
        # Add process health check
        is_running = self.is_daemon_running()
        base_status["process_running"] = is_running
        
        # Add proxy health check
        if is_running:
            proxy_health = self.check_proxy_health()
            base_status["proxy_health"] = proxy_health
            
        # Add system resources
        if is_running:
            resource_usage = self.get_resource_usage()
            base_status["resources"] = resource_usage
            
        return base_status
    
    def get_basic_status(self):
        """Get basic status from file"""
        if not os.path.exists(self.status_file):
            return {
                "status": "not_initialized", 
                "message": "Daemon status file not found",
                "timestamp": datetime.now().isoformat()
            }
            
        try:
            with open(self.status_file, 'r') as f:
                status = json.load(f)
            
            # Validate status structure
            required_fields = ["status", "started"]
            for field in required_fields:
                if field not in status:
                    status[field] = "unknown"
                    
            return status
        except json.JSONDecodeError as e:
            return {
                "status": "corrupted", 
                "message": f"Status file corrupted: {e}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error reading status: {e}",
                "timestamp": datetime.now().isoformat()
            }
    
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
    
    def validate_daemon_integrity(self):
        """Comprehensive daemon integrity check"""
        issues = []
        
        # Check PID file
        if not os.path.exists(self.pid_file):
            issues.append("PID file missing")
        elif not self.is_daemon_running():
            issues.append("Process not running (stale PID)")
        
        # Check status file
        if not os.path.exists(self.status_file):
            issues.append("Status file missing")
        else:
            status = self.get_basic_status()
            if status.get("status") == "corrupted":
                issues.append("Status file corrupted")
        
        # Check proxy files
        if not os.path.exists('working_proxies.txt'):
            issues.append("Proxy file missing")
        elif os.path.getsize('working_proxies.txt') == 0:
            issues.append("No proxies available")
        
        # Check logs directory
        if not os.path.exists('logs'):
            issues.append("Logs directory missing")
        
        return {
            "healthy": len(issues) == 0,
            "issues": issues,
            "issue_count": len(issues)
        }
    
    def repair_daemon_files(self):
        """Attempt to repair common daemon issues"""
        repairs = []
        
        # Remove stale PID file
        if os.path.exists(self.pid_file) and not self.is_daemon_running():
            os.remove(self.pid_file)
            repairs.append("Removed stale PID file")
        
        # Create logs directory
        if not os.path.exists('logs'):
            os.makedirs('logs')
            repairs.append("Created logs directory")
        
        # Reset corrupted status file
        status = self.get_basic_status()
        if status.get("status") == "corrupted":
            default_status = {
                "status": "stopped",
                "started": None,
                "last_refresh": None,
                "working_proxies": 0,
                "total_refreshes": 0,
                "timestamp": datetime.now().isoformat()
            }
            with open(self.status_file, 'w') as f:
                json.dump(default_status, f, indent=2)
            repairs.append("Reset corrupted status file")
        
        return repairs
    
    def start_daemon_enhanced(self, refresh_interval=3600):
        """Enhanced daemon startup with better error handling"""
        if self.is_daemon_running():
            print("🟢 Daemon is already running")
            return {"success": False, "message": "Already running"}
        
        # Pre-flight checks
        repairs = self.repair_daemon_files()
        if repairs:
            print(f"🔧 Applied repairs: {', '.join(repairs)}")
        
        print("🚀 Starting proxy chain daemon...")
        
        try:
            # Start daemon process with better error handling
            process = subprocess.Popen([
                sys.executable, "proxy_chain_daemon.py",
                "--refresh-interval", str(refresh_interval),
                "--daemon"
            ], 
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
            )
            
            # Wait briefly to check if it started successfully
            time.sleep(2)
            
            if process.poll() is None:  # Process is still running
                # Save PID
                self.save_pid(process.pid)
                print(f"✅ Daemon started successfully with PID {process.pid}")
                
                # Update status
                self.update_status({
                    "status": "starting",
                    "started": datetime.now().isoformat(),
                    "pid": process.pid
                })
                
                return {"success": True, "pid": process.pid}
            else:
                # Process died immediately
                stdout, stderr = process.communicate()
                error_msg = stderr.decode() if stderr else "Unknown error"
                print(f"❌ Daemon failed to start: {error_msg}")
                return {"success": False, "message": error_msg}
                
        except Exception as e:
            print(f"❌ Error starting daemon: {e}")
            return {"success": False, "message": str(e)}
    
    def save_pid(self, pid):
        """Save PID with atomic write"""
        temp_file = f"{self.pid_file}.tmp"
        try:
            with open(temp_file, 'w') as f:
                f.write(str(pid))
            os.replace(temp_file, self.pid_file)
        except Exception:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def update_status(self, updates):
        """Update status file with new information"""
        current_status = self.get_basic_status()
        current_status.update(updates)
        current_status["last_updated"] = datetime.now().isoformat()
        
        temp_file = f"{self.status_file}.tmp"
        try:
            with open(temp_file, 'w') as f:
                json.dump(current_status, f, indent=2)
            os.replace(temp_file, self.status_file)
        except Exception:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            raise
    
    def show_enhanced_status(self):
        """Display comprehensive status with health checks"""
        print("🔗 ENHANCED Proxy Chain Daemon Status")
        print("=" * 50)
        
        # Get comprehensive status
        status = self.get_enhanced_status()
        integrity = self.validate_daemon_integrity()
        
        # Process Status
        if status.get("process_running"):
            print("🟢 Process: RUNNING")
        else:
            print("🔴 Process: STOPPED")
        
        # Basic Info
        if status.get('started'):
            started_time = datetime.fromisoformat(status['started'])
            uptime = datetime.now() - started_time
            print(f"📅 Started: {started_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"⏱️  Uptime: {str(uptime).split('.')[0]}")
        
        # Resource Usage
        if "resources" in status:
            res = status["resources"]
            if "error" not in res:
                print(f"💾 Memory: {res['memory_mb']} MB")
                print(f"🖥️  CPU: {res['cpu_percent']}%")
                print(f"🧵 Threads: {res['threads']}")
        
        # Proxy Health
        if "proxy_health" in status:
            health = status["proxy_health"]
            if "error" not in health:
                print(f"🎯 Proxy Health: {health['health'].upper()}")
                print(f"✅ Working: {health['working']}/{health['total']} ({health.get('ratio', 0)}%)")
        
        # System Integrity
        print(f"\n🔍 System Integrity: {'✅ HEALTHY' if integrity['healthy'] else '⚠️ ISSUES DETECTED'}")
        if not integrity['healthy']:
            for issue in integrity['issues']:
                print(f"   ❌ {issue}")
        
        # Configuration
        print(f"\n📊 Status: {status.get('status', 'unknown')}")
        print(f"🔢 Refreshes: {status.get('total_refreshes', 0)}")
        
        if status.get('last_refresh'):
            print(f"🔄 Last Refresh: {status['last_refresh']}")
        
        return status

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Proxy Daemon Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'health', 'repair'], 
                       help='Action to perform')
    parser.add_argument('--refresh-interval', type=int, default=3600,
                       help='Proxy refresh interval in seconds (default: 3600)')
    parser.add_argument('--json', action='store_true', 
                       help='Output status in JSON format')
    
    args = parser.parse_args()
    
    manager = ImprovedProxyDaemonManager()
    
    if args.action == 'start':
        result = manager.start_daemon_enhanced(args.refresh_interval)
        if args.json:
            print(json.dumps(result))
    elif args.action == 'stop':
        # Use the original stop method (it's fine)
        from proxy_status import ProxyDaemonManager
        original_manager = ProxyDaemonManager()
        original_manager.stop_daemon()
    elif args.action == 'restart':
        from proxy_status import ProxyDaemonManager
        original_manager = ProxyDaemonManager()
        original_manager.restart_daemon(args.refresh_interval)
    elif args.action == 'status':
        if args.json:
            status = manager.get_enhanced_status()
            print(json.dumps(status, indent=2))
        else:
            manager.show_enhanced_status()
    elif args.action == 'health':
        integrity = manager.validate_daemon_integrity()
        proxy_health = manager.check_proxy_health()
        print(json.dumps({"integrity": integrity, "proxy_health": proxy_health}, indent=2))
    elif args.action == 'repair':
        repairs = manager.repair_daemon_files()
        print(f"🔧 Applied {len(repairs)} repairs:")
        for repair in repairs:
            print(f"   ✅ {repair}")

if __name__ == "__main__":
    main()
