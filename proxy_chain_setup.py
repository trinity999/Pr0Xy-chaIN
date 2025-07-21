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
        self.proxy_sources = {
            'free-proxy-list': 'https://www.proxy-list.download/api/v1/get?type=http',
            'proxylist-geonode': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
            'proxy-list-github': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'free-proxy-csv': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt'
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
                
            elif source_name in ['proxy-list-github', 'free-proxy-csv']:
                # Text-based proxy lists
                proxies = []
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith('#'):
                        proxies.append(line)
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
    
    def validate_proxies(self, proxy_list, max_workers=50):
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
    
    def create_proxy_chain(self, chain_length=3):
        """Create a proxy chain configuration"""
        if len(self.working_proxies) < chain_length:
            logger.warning(f"Not enough proxies for chain length {chain_length}")
            chain_length = len(self.working_proxies)
        
        chain = random.sample(self.working_proxies, chain_length)
        logger.info(f"Created proxy chain: {' -> '.join(chain)}")
        return chain

def main():
    manager = ProxyChainManager()
    
    print("🔗 Proxy Chain Setup for Security Scanning")
    print("=" * 50)
    
    # Fetch all proxies
    print("📡 Fetching proxies from multiple sources...")
    all_proxies = manager.fetch_all_proxies()
    
    # Validate proxies
    print("🧪 Testing proxy connectivity...")
    working_proxies = manager.validate_proxies(all_proxies[:200])  # Test first 200 for speed
    
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
