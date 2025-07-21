#!/usr/bin/env python3
"""
Proxy Chain Initialization Script
One-command setup and start for proxy chain daemon
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from banner import print_banner, print_success_banner, print_error_banner

class ProxyChainInitializer:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.required_files = [
            'proxy_chain_setup.py',
            'proxy_chain_daemon.py', 
            'proxy_status.py',
            'proxy_scanner.py',
            'requirements.txt'
        ]
        
    def check_dependencies(self):
        """Check if all required files and dependencies exist"""
        print("🔍 Checking dependencies...")
        
        # Check files
        missing_files = []
        for file in self.required_files:
            if not (self.base_dir / file).exists():
                missing_files.append(file)
                
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
            
        # Check Python packages
        try:
            import requests
            import psutil
            print("✅ All dependencies found")
            return True
        except ImportError as e:
            print(f"❌ Missing Python package: {e}")
            print("Run: pip install -r requirements.txt")
            return False
    
    def install_requirements(self):
        """Install required Python packages"""
        print("📦 Installing Python requirements...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
            ], check=True, cwd=self.base_dir)
            
            # Install additional packages for daemon
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'psutil'
            ], check=True, cwd=self.base_dir)
            
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['logs', 'output', 'wordlists']
        for dir_name in directories:
            dir_path = self.base_dir / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ Directory ready: {dir_name}")
    
    def check_daemon_status(self):
        """Check if daemon is already running"""
        try:
            result = subprocess.run([
                sys.executable, 'proxy_status.py', 'status'
            ], capture_output=True, text=True, cwd=self.base_dir)
            
            if 'RUNNING' in result.stdout:
                return True
        except:
            pass
        return False
    
    def start_daemon(self):
        """Start the proxy chain daemon"""
        print("🚀 Starting proxy chain daemon...")
        
        try:
            # Start daemon in background
            subprocess.run([
                sys.executable, 'proxy_status.py', 'start'
            ], cwd=self.base_dir)
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Check status
            if self.check_daemon_status():
                print("✅ Proxy chain daemon started successfully!")
                return True
            else:
                print("⚠️  Daemon may be starting up, check status with: proxy-status")
                return True
                
        except Exception as e:
            print(f"❌ Failed to start daemon: {e}")
            return False
    
    def show_summary(self):
        """Show summary and usage instructions"""
        print("\n" + "="*60)
        print("🎉 PROXY CHAIN INITIALIZATION COMPLETE!")
        print("="*60)
        print("🔧 Available commands:")
        print("  init-proxy-chain-now    - Start/restart the proxy service")
        print("  proxy-status           - Check daemon status")
        print("  proxy-stop             - Stop the daemon") 
        print("  proxy-scan             - Use proxy-enabled scanning")
        print()
        print("📁 Files created:")
        print("  • working_proxies.txt   - List of working proxies")
        print("  • proxychains.conf      - Proxychains configuration")
        print("  • proxy_config.json     - JSON configuration")
        print("  • logs/proxy_daemon.log - Daemon logs")
        print()
        print("🎯 Usage examples:")
        print("  python proxy_scanner.py nmap target.com")
        print("  python proxy_scanner.py curl https://httpbin.org/ip")
        print("  python proxy_scanner.py gobuster https://example.com -w wordlist.txt")
        print()
        print("⚠️  Remember: Use only for authorized testing!")
        print("="*60)

def main():
    # Display the awesome banner
    print_banner()
    
    initializer = ProxyChainInitializer()
    
    # Check if daemon is already running
    if initializer.check_daemon_status():
        print("🟢 Proxy chain daemon is already running!")
        print("Use 'proxy-status' to check details or 'proxy-stop' to stop.")
        return
    
    # Step 1: Check dependencies
    if not initializer.check_dependencies():
        print("📦 Installing missing dependencies...")
        if not initializer.install_requirements():
            print("❌ Failed to install dependencies. Please install manually.")
            return
    
    # Step 2: Setup directories
    initializer.setup_directories()
    
    # Step 3: Start daemon
    if not initializer.start_daemon():
        print("❌ Failed to start daemon")
        return
    
    # Step 4: Show summary
    initializer.show_summary()

if __name__ == "__main__":
    main()
