#!/usr/bin/env python3
"""
Proxy Chain Setup for Security Scanning
Fetches free proxies from multiple sources and sets up rotation
"""

import requests
import json
import random
import time
import socket
import threading
from urllib.parse import urlparse
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProxyChainManager:
    def __init__(self):
        self.working_proxies = []
        self.dead_proxies = set()
        self.proxy_scores = {}  # Track proxy reliability scores
        self.proxy_sources = {
            # Existing sources
            'free-proxy-list': 'https://www.proxy-list.download/api/v1/get?type=http',
            'proxylist-geonode': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
            'proxy-list-github': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'free-proxy-csv': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            
            # NEW: Additional reliable sources from your research
            'monosans-http': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'monosans-socks4': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
            'monosans-socks5': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
            'proxifly-http': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt',
            'proxifly-https': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/https/data.txt',
            'proxifly-socks4': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks4/data.txt',
            'proxifly-socks5': 'https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/socks5/data.txt',
            'vakhov-fresh-http': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt',
            'vakhov-fresh-https': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt',
            'vakhov-fresh-socks4': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt',
            'vakhov-fresh-socks5': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt',
            'speedx-socks4': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'speedx-socks5': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt'
        }
        
    def fetch_proxies_from_api(self, source_name, url):
        """Fetch proxies from API endpoints"""
        try:
            logger.info(f"Fetching proxies from {source_name}")
            response = requests.get(url, timeout=30)
            
            if source_name == 'proxylist-geonode':
                data = response.json()
                proxies = []
                for proxy in data.get('data', []):
                    if proxy.get('protocols', []):
                        proxies.append(f"{proxy['ip']}:{proxy['port']}")
                return proxies
                
            elif source_name.startswith(('proxy-list-github', 'free-proxy-csv', 'monosans-', 'proxifly-', 'vakhov-', 'speedx-')):
                # Text-based proxy lists from GitHub sources
                proxies = []
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    # Skip comments, empty lines, and invalid formats
                    if ':' in line and not line.startswith('#') and not line.startswith('//') and line:
                        # Validate IP:PORT format
                        parts = line.split(':')
                        if len(parts) == 2:
                            try:
                                # Validate port is numeric
                                int(parts[1])
                                proxies.append(line)
                            except ValueError:
                                continue
                return proxies
                
            else:
                # Default handling for other APIs
                return response.text.strip().split('\n')
                
        except Exception as e:
            logger.error(f"Error fetching from {source_name}: {e}")
            return []
    
    def test_proxy(self, proxy, timeout=10):
        """Test if a proxy is working"""
        try:
            ip_port = proxy.split(':')
            if len(ip_port) != 2:
                return False
                
            ip, port = ip_port[0], int(ip_port[1])
            
            # Test HTTP proxy
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            test_response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=timeout
            )
            
            if test_response.status_code == 200:
                logger.info(f"✓ Proxy {proxy} is working")
                return True
                
        except Exception as e:
            logger.debug(f"✗ Proxy {proxy} failed: {e}")
            
        return False
    
    def fetch_all_proxies(self):
        """Fetch proxies from all sources"""
        all_proxies = set()
        
        for source_name, url in self.proxy_sources.items():
            try:
                proxies = self.fetch_proxies_from_api(source_name, url)
                logger.info(f"Found {len(proxies)} proxies from {source_name}")
                all_proxies.update(proxies)
            except Exception as e:
                logger.error(f"Failed to fetch from {source_name}: {e}")
        
        # Add some reliable public proxies as fallback
        fallback_proxies = [
            "8.8.8.8:3128",
            "1.1.1.1:3128", 
            "208.67.222.222:3128"
        ]
        
        all_proxies.update(fallback_proxies)
        logger.info(f"Total unique proxies collected: {len(all_proxies)}")
        return list(all_proxies)
    
    def validate_proxies(self, proxy_list, max_workers=200):
        """Validate proxies concurrently"""
        logger.info(f"Testing {len(proxy_list)} proxies...")
        working_proxies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxy_list
            }
            
            completed = 0
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                completed += 1
                
                if completed % 10 == 0:
                    logger.info(f"Tested {completed}/{len(proxy_list)} proxies...")
                
                try:
                    if future.result():
                        working_proxies.append(proxy)
                except Exception as e:
                    logger.debug(f"Error testing {proxy}: {e}")
        
        self.working_proxies = working_proxies
        logger.info(f"Found {len(working_proxies)} working proxies")
        return working_proxies
    
    def save_proxies(self, filename="working_proxies.txt"):
        """Save working proxies to file"""
        filepath = os.path.join(os.getcwd(), filename)
        with open(filepath, 'w') as f:
            for proxy in self.working_proxies:
                f.write(f"{proxy}\n")
        logger.info(f"Saved {len(self.working_proxies)} working proxies to {filepath}")
    
    def get_random_proxy(self):
        """Get a random working proxy"""
        if not self.working_proxies:
            logger.warning("No working proxies available")
            return None
        return random.choice(self.working_proxies)
    
    def mark_proxy_dead(self, proxy):
        """Mark a proxy as dead and remove from working list"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.dead_proxies.add(proxy)
            logger.info(f"Marked proxy {proxy} as dead")
    
    def remove_dead_proxies(self):
        """Remove dead proxies from working list"""
        initial_count = len(self.working_proxies)
        self.working_proxies = [p for p in self.working_proxies if p not in self.dead_proxies]
        removed_count = initial_count - len(self.working_proxies)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} dead proxies")
        return removed_count
    
    def score_proxy_reliability(self, proxy, success_rate):
        """Score proxy based on reliability"""
        self.proxy_scores[proxy] = success_rate
    
    def get_best_proxies(self, count=10):
        """Get the most reliable proxies"""
        if not self.proxy_scores:
            return self.working_proxies[:count]
        
        sorted_proxies = sorted(
            self.proxy_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return [proxy for proxy, score in sorted_proxies[:count] if proxy in self.working_proxies]
    
    def create_proxy_chain(self, chain_length=3):
        """Create a proxy chain configuration using best available proxies"""
        if len(self.working_proxies) < chain_length:
            logger.warning(f"Not enough proxies for chain length {chain_length}")
            chain_length = len(self.working_proxies)
        
        # Use best proxies if we have reliability scores
        candidates = self.get_best_proxies(min(chain_length * 2, len(self.working_proxies)))
        if len(candidates) < chain_length:
            candidates = self.working_proxies
            
        chain = random.sample(candidates, chain_length)
        logger.info(f"Created proxy chain: {' -> '.join(chain)}")
        return chain

def main():
    manager = ProxyChainManager()
    
    print("🔗 Proxy Chain Setup for Security Scanning")
    print("=" * 50)
    
    # Fetch all proxies
    print("📡 Fetching proxies from multiple sources...")
    all_proxies = manager.fetch_all_proxies()
    
    # Validate proxies - NOW TESTS ALL PROXIES FOR MAXIMUM RESOURCES!
    print("🚀 MASSIVE TESTING: Scanning ALL proxies for maximum resources...")
    print(f"📊 Testing ALL {len(all_proxies):,} proxies to give you the best possible results!")
    print("⚡ This ensures you get EVERY working proxy available (not just a few)")
    print("⏱️  Please wait 10-20 minutes for complete scanning...")
    print()
    
    # Use ALL proxies instead of limiting to 200
    working_proxies = manager.validate_proxies(all_proxies)  # Test ALL for maximum resources!
    
    if not working_proxies:
        print("❌ No working proxies found. Try running again later.")
        sys.exit(1)
    
    # Save results
    manager.save_proxies()
    
    # Create sample proxy chains
    print("\n🔗 Sample proxy chains:")
    for i in range(3):
        chain = manager.create_proxy_chain(3)
        print(f"Chain {i+1}: {' -> '.join(chain)}")
    
    # Export for use with tools
    export_configs(manager.working_proxies)
    
    print(f"\n✅ Setup complete! {len(working_proxies)} working proxies ready.")
    print("📁 Files created:")
    print("  - working_proxies.txt")
    print("  - proxychains.conf")
    print("  - proxy_config.json")

def export_configs(proxies):
    """Export proxy configurations for various tools"""
    
    # Create proxychains config
    proxychains_config = """# Proxychains config for scanning
strict_chain
proxy_dns
remote_dns_subnet 224
tcp_read_time_out 15000
tcp_connect_time_out 8000

[ProxyList]
"""
    
    # Add random selection of proxies to proxychains
    selected_proxies = random.sample(proxies, min(10, len(proxies)))
    for proxy in selected_proxies:
        ip, port = proxy.split(':')
        proxychains_config += f"http {ip} {port}\n"
    
    with open('proxychains.conf', 'w') as f:
        f.write(proxychains_config)
    
    # Create JSON config for scripts
    config = {
        "working_proxies": proxies,
        "rotation_enabled": True,
        "chain_length": 3,
        "timeout": 10,
        "user_agents": [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
    }
    
    with open('proxy_config.json', 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    main()
