#!/usr/bin/env python3
"""
Proxy Chain Daemon Status Manager
Check status, start, stop, and manage the proxy daemon
"""

import json
import os
import sys
import subprocess
import psutil
import time
from datetime import datetime
from banner import print_mini_banner, print_status_header, print_status_footer

class ProxyDaemonManager:
    def __init__(self):
        self.status_file = "daemon_status.json"
        self.pid_file = "daemon.pid"
        
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
        """Check if daemon process is actually running"""
        if not os.path.exists(self.pid_file):
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
                
            # Check if process exists
            return psutil.pid_exists(pid)
        except:
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
    
    def show_status(self):
        """Display detailed status"""
        status = self.get_status()
        is_running = self.is_daemon_running()
        
        print("🔗 Proxy Chain Daemon Status")
        print("=" * 40)
        
        if is_running:
            print("🟢 Status: RUNNING")
        else:
            print("🔴 Status: STOPPED")
            
        if status.get('started'):
            print(f"📅 Started: {status['started']}")
            
        if status.get('last_refresh'):
            print(f"🔄 Last Refresh: {status['last_refresh']}")
            
        print(f"🎯 Working Proxies: {status.get('working_proxies', 0)}")
        print(f"🔢 Total Refreshes: {status.get('total_refreshes', 0)}")
        print(f"📊 Current Status: {status.get('status', 'unknown')}")
        
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
