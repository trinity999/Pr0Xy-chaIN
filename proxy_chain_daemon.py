#!/usr/bin/env python3
"""
Proxy Chain Background Daemon
Continuously maintains and updates proxy chains in the background
"""

import json
import time
import logging
import threading
import os
import sys
import signal
import atexit
from datetime import datetime, timedelta
from proxy_chain_setup import ProxyChainManager
import requests

class ProxyChainDaemon:
    def __init__(self, refresh_interval=3600):  # 1 hour default
        self.refresh_interval = refresh_interval
        self.running = True
        self.manager = ProxyChainManager()
        self.status = {
            'started': datetime.now().isoformat(),
            'last_refresh': None,
            'working_proxies': 0,
            'total_refreshes': 0,
            'status': 'initializing'
        }
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        atexit.register(self.cleanup)
        
    def setup_logging(self):
        """Setup logging to file and console"""
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Setup file logging
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('logs/proxy_daemon.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
        
    def cleanup(self):
        """Cleanup on exit"""
        self.logger.info("Daemon shutting down...")
        self.status['status'] = 'stopped'
        self.save_status()
        
    def save_status(self):
        """Save daemon status to file"""
        with open('daemon_status.json', 'w') as f:
            json.dump(self.status, f, indent=2)
            
    def load_existing_proxies(self):
        """Load existing proxies if available"""
        if os.path.exists('working_proxies.txt'):
            with open('working_proxies.txt', 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            self.manager.working_proxies = proxies
            self.logger.info(f"Loaded {len(proxies)} existing proxies")
            return True
        return False
        
    def refresh_proxies(self):
        """Refresh proxy list"""
        try:
            self.logger.info("Starting proxy refresh cycle...")
            self.status['status'] = 'refreshing'
            self.save_status()
            
            # Fetch new proxies
            all_proxies = self.manager.fetch_all_proxies()
            
            # Validate proxies (limit to avoid long blocking)
            working_proxies = self.manager.validate_proxies(all_proxies[:100])
            
            if working_proxies:
                # Save results
                self.manager.save_proxies()
                
                # Update configurations
                from proxy_chain_setup import export_configs
                export_configs(working_proxies)
                
                self.status.update({
                    'last_refresh': datetime.now().isoformat(),
                    'working_proxies': len(working_proxies),
                    'total_refreshes': self.status['total_refreshes'] + 1,
                    'status': 'active'
                })
                
                self.logger.info(f"Refresh complete: {len(working_proxies)} working proxies")
            else:
                self.logger.warning("No working proxies found in refresh cycle")
                self.status['status'] = 'no_proxies'
                
        except Exception as e:
            self.logger.error(f"Error during proxy refresh: {e}")
            self.status['status'] = 'error'
            
        self.save_status()
        
    def health_check(self):
        """Perform health check on random proxy"""
        if not self.manager.working_proxies:
            return False
            
        try:
            proxy = self.manager.get_random_proxy()
            if not proxy:
                return False
                
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=10
            )
            
            if response.status_code == 200:
                self.logger.info(f"Health check passed with proxy {proxy}")
                return True
                
        except Exception as e:
            self.logger.debug(f"Health check failed: {e}")
            
        return False
        
    def run(self):
        """Main daemon loop"""
        self.logger.info("Proxy Chain Daemon starting...")
        
        # Load existing proxies or perform initial refresh
        if not self.load_existing_proxies():
            self.refresh_proxies()
        else:
            self.status.update({
                'working_proxies': len(self.manager.working_proxies),
                'status': 'active'
            })
        
        self.save_status()
        
        last_refresh = datetime.now()
        health_check_interval = 300  # 5 minutes
        last_health_check = datetime.now()
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # Perform periodic health checks
                if (current_time - last_health_check).seconds >= health_check_interval:
                    if self.manager.working_proxies:
                        self.health_check()
                    last_health_check = current_time
                
                # Refresh proxies periodically
                if (current_time - last_refresh).seconds >= self.refresh_interval:
                    self.refresh_proxies()
                    last_refresh = current_time
                
                # Sleep for a short interval
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                self.logger.info("Received keyboard interrupt, shutting down...")
                break
            except Exception as e:
                self.logger.error(f"Unexpected error in daemon loop: {e}")
                time.sleep(60)  # Wait a minute before continuing
                
        self.cleanup()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Proxy Chain Background Daemon")
    parser.add_argument('--refresh-interval', type=int, default=3600,
                       help='Proxy refresh interval in seconds (default: 3600)')
    parser.add_argument('--daemon', action='store_true',
                       help='Run as daemon (detached from terminal)')
    
    args = parser.parse_args()
    
    if args.daemon:
        # For Windows, we'll simulate daemon behavior
        import subprocess
        import sys
        
        # Start the process in background
        subprocess.Popen([
            sys.executable, __file__,
            '--refresh-interval', str(args.refresh_interval)
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("🚀 Proxy chain daemon started in background")
        return
    
    daemon = ProxyChainDaemon(refresh_interval=args.refresh_interval)
    daemon.run()

if __name__ == "__main__":
    main()
