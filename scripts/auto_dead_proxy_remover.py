#!/usr/bin/env python3
"""
Automatic Dead Proxy Removal System
Real-time monitoring and removal of non-working proxies for optimal load balancing
"""

import json
import time
import requests
import threading
import os
import sys
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutoDeadProxyRemover:
    def __init__(self, config_file="proxy_config.json"):
        self.config_file = config_file
        self.working_proxies = []
        self.dead_proxies = set()
        self.proxy_health = {}  # Track health scores
        self.monitoring_active = False
        self.health_check_interval = 300  # 5 minutes
        self.failure_threshold = 3  # Mark dead after 3 failures
        self.success_threshold = 2  # Mark alive after 2 successes
        
    def load_config(self):
        """Load proxy configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.working_proxies = config.get('working_proxies', [])
                logger.info(f"Loaded {len(self.working_proxies)} proxies from config")
                
                # Initialize health tracking
                for proxy in self.working_proxies:
                    if proxy not in self.proxy_health:
                        self.proxy_health[proxy] = {
                            'failures': 0,
                            'successes': 0,
                            'last_check': None,
                            'response_time': None,
                            'status': 'unknown'
                        }
                return True
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return False
    
    def save_config(self):
        """Save updated proxy configuration"""
        try:
            config = {
                "working_proxies": self.working_proxies,
                "rotation_enabled": True,
                "chain_length": 3,
                "timeout": 10,
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ]
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Also save dead proxies for reference
            with open('auto_removed_dead_proxies.txt', 'w') as f:
                for proxy in self.dead_proxies:
                    f.write(f"{proxy}\n")
            
            logger.info(f"Updated config: {len(self.working_proxies)} working, {len(self.dead_proxies)} dead")
            return True
            
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def test_proxy_health(self, proxy):
        """Test individual proxy health"""
        test_urls = [
            'http://httpbin.org/ip',
            'http://icanhazip.com'
        ]
        
        start_time = time.time()
        
        for url in test_urls:
            try:
                proxy_dict = {
                    'http': f'http://{proxy}',
                    'https': f'http://{proxy}'
                }
                
                response = requests.get(
                    url,
                    proxies=proxy_dict,
                    timeout=8,
                    verify=False
                )
                
                if response.status_code == 200:
                    response_time = time.time() - start_time
                    return True, response_time, "Working"
                    
            except requests.exceptions.ProxyError as e:
                continue
            except requests.exceptions.ConnectTimeout as e:
                continue
            except requests.exceptions.ReadTimeout as e:
                continue
            except Exception as e:
                continue
        
        return False, None, "Failed"
    
    def update_proxy_health(self, proxy, is_working, response_time=None):
        """Update proxy health tracking"""
        if proxy not in self.proxy_health:
            self.proxy_health[proxy] = {
                'failures': 0,
                'successes': 0,
                'last_check': None,
                'response_time': None,
                'status': 'unknown'
            }
        
        health = self.proxy_health[proxy]
        health['last_check'] = datetime.now()
        
        if is_working:
            health['successes'] += 1
            health['failures'] = 0  # Reset failures on success
            health['response_time'] = response_time
            health['status'] = 'healthy'
        else:
            health['failures'] += 1
            health['status'] = 'unhealthy'
        
        # Determine if proxy should be marked dead or alive
        if health['failures'] >= self.failure_threshold:
            if proxy in self.working_proxies:
                logger.warning(f"🗑️ Marking {proxy} as DEAD (failures: {health['failures']})")
                self.working_proxies.remove(proxy)
                self.dead_proxies.add(proxy)
                health['status'] = 'dead'
                return 'REMOVED'
        
        elif health['successes'] >= self.success_threshold and proxy in self.dead_proxies:
            logger.info(f"🔄 Reviving {proxy} as WORKING (successes: {health['successes']})")
            self.dead_proxies.remove(proxy)
            if proxy not in self.working_proxies:
                self.working_proxies.append(proxy)
            health['status'] = 'healthy'
            return 'REVIVED'
        
        return 'UPDATED'
    
    def perform_health_check(self):
        """Perform health check on all proxies"""
        logger.info("🔍 Starting automated health check...")
        
        all_proxies = list(set(self.working_proxies + list(self.dead_proxies)))
        
        if not all_proxies:
            logger.warning("No proxies to check")
            return
        
        removed_count = 0
        revived_count = 0
        healthy_count = 0
        
        # Test proxies in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy_health, proxy): proxy
                for proxy in all_proxies
            }
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    is_working, response_time, status = future.result()
                    action = self.update_proxy_health(proxy, is_working, response_time)
                    
                    if action == 'REMOVED':
                        removed_count += 1
                    elif action == 'REVIVED':
                        revived_count += 1
                    elif is_working:
                        healthy_count += 1
                        
                except Exception as e:
                    logger.error(f"Error testing {proxy}: {e}")
                    self.update_proxy_health(proxy, False)
        
        # Update configuration
        self.save_config()
        
        logger.info(f"🏥 Health check complete:")
        logger.info(f"   ✅ Healthy: {healthy_count}")
        logger.info(f"   🔄 Revived: {revived_count}")
        logger.info(f"   🗑️ Removed: {removed_count}")
        logger.info(f"   📊 Working pool: {len(self.working_proxies)}")
        
        return {
            'healthy': healthy_count,
            'revived': revived_count, 
            'removed': removed_count,
            'working_total': len(self.working_proxies)
        }
    
    def get_health_report(self):
        """Generate detailed health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_proxies': len(self.proxy_health),
            'working_proxies': len(self.working_proxies),
            'dead_proxies': len(self.dead_proxies),
            'health_details': {}
        }
        
        # Categorize proxies by health
        healthy = []
        unhealthy = []
        dead = []
        
        for proxy, health in self.proxy_health.items():
            if health['status'] == 'healthy':
                healthy.append({
                    'proxy': proxy,
                    'response_time': health['response_time'],
                    'successes': health['successes']
                })
            elif health['status'] == 'unhealthy':
                unhealthy.append({
                    'proxy': proxy,
                    'failures': health['failures']
                })
            elif health['status'] == 'dead':
                dead.append({
                    'proxy': proxy,
                    'failures': health['failures'],
                    'last_check': health['last_check'].isoformat() if health['last_check'] else None
                })
        
        # Sort by performance
        healthy.sort(key=lambda x: x['response_time'] or 999)
        
        report['health_details'] = {
            'healthy': healthy,
            'unhealthy': unhealthy,
            'dead': dead
        }
        
        return report
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info("🚀 Starting automatic dead proxy removal monitoring...")
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.perform_health_check()
                    
                    # Wait for next check
                    for i in range(self.health_check_interval):
                        if not self.monitoring_active:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(30)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info(f"✅ Monitoring started (check interval: {self.health_check_interval}s)")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        logger.info("🛑 Stopping monitoring...")
        self.monitoring_active = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        logger.info("✅ Monitoring stopped")
    
    def run_immediate_cleanup(self):
        """Run immediate dead proxy cleanup"""
        logger.info("🧹 Running immediate dead proxy cleanup...")
        
        if not self.load_config():
            return False
        
        # Perform single health check
        results = self.perform_health_check()
        
        # Generate report
        report = self.get_health_report()
        
        # Save detailed report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"auto_cleanup_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print("🧹 AUTOMATIC DEAD PROXY REMOVAL - COMPLETE")
        print("="*60)
        print(f"✅ Healthy Proxies: {results['healthy']}")
        print(f"🔄 Revived Proxies: {results['revived']}")
        print(f"🗑️ Removed Proxies: {results['removed']}")
        print(f"📊 Final Working Pool: {results['working_total']}")
        print(f"📄 Detailed Report: {report_file}")
        print("="*60)
        
        return True

def main():
    remover = AutoDeadProxyRemover()
    
    print("🔧 AUTOMATIC DEAD PROXY REMOVAL SYSTEM")
    print("="*50)
    print("1. Run immediate cleanup")
    print("2. Start continuous monitoring")
    print("3. Generate health report")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            remover.run_immediate_cleanup()
        
        elif choice == '2':
            if not remover.load_config():
                return
            
            remover.start_monitoring()
            print("🔄 Monitoring active. Press Ctrl+C to stop...")
            
            try:
                while True:
                    time.sleep(10)
                    print(f"📊 Status: {len(remover.working_proxies)} working, {len(remover.dead_proxies)} dead")
            except KeyboardInterrupt:
                remover.stop_monitoring()
                print("\n✅ Monitoring stopped.")
        
        elif choice == '3':
            if not remover.load_config():
                return
            
            report = remover.get_health_report()
            print(f"\n📊 PROXY HEALTH REPORT")
            print(f"Total Proxies: {report['total_proxies']}")
            print(f"Working: {report['working_proxies']}")
            print(f"Dead: {report['dead_proxies']}")
            
            # Show top 5 fastest
            healthy = report['health_details']['healthy'][:5]
            if healthy:
                print(f"\n⚡ Top 5 Fastest Proxies:")
                for i, proxy_info in enumerate(healthy, 1):
                    print(f"  {i}. {proxy_info['proxy']} - {proxy_info['response_time']:.2f}s")
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n👋 Exiting...")

if __name__ == "__main__":
    main()
