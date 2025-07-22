#!/usr/bin/env python3
"""
Enhanced Proxy Chain Manager with Dead Proxy Removal & Continuous Refresh
Addresses the main reliability issues with automatic cleanup and multiple sources
"""

import requests
import json
import random
import time
import threading
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedProxyManager:
    def __init__(self):
        self.working_proxies = []
        self.dead_proxies = set()
        self.proxy_scores = {}  # Track reliability scores
        self.last_refresh = None
        self.refresh_interval = 300  # 5 minutes
        
        # ✅ ALL RELIABLE PROXY SOURCES - VERIFIED WORKING URLS
        self.proxy_sources = {
            # High-frequency updated sources (every 5-20 minutes)
            'monosans-http': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'monosans-socks4': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt',
            'monosans-socks5': 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt',
            'vakhov-http': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/http.txt',
            'vakhov-https': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/https.txt',
            'vakhov-socks4': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks4.txt',
            'vakhov-socks5': 'https://raw.githubusercontent.com/vakhov/fresh-proxy-list/master/socks5.txt',
            
            # Daily updated sources  
            'clarketm-daily': 'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'speedx-http': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'speedx-socks4': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
            'speedx-socks5': 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt',
            
            # API-based sources
            'geonode-api': 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc',
            'proxy-list-api': 'https://www.proxy-list.download/api/v1/get?type=http',
            
            # Alternative reliable sources
            'openproxy-http': 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt',
            'proxy-daily': 'https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt'
        }

    def fetch_proxies_from_source(self, source_name, url):
        """Enhanced proxy fetching with better error handling"""
        try:
            logger.info(f"🔄 Fetching from {source_name}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=30, headers=headers)
            response.raise_for_status()
            
            if source_name == 'geonode-api':
                data = response.json()
                proxies = []
                for proxy in data.get('data', []):
                    if proxy.get('protocols', []):
                        proxies.append(f"{proxy['ip']}:{proxy['port']}")
                return proxies
            
            else:
                # Text-based proxy lists
                proxies = []
                for line in response.text.strip().split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith(('#', '//')):
                        parts = line.split(':')
                        if len(parts) == 2:
                            try:
                                int(parts[1])  # Validate port
                                if parts[0].count('.') == 3:  # Basic IP validation
                                    proxies.append(line)
                            except ValueError:
                                continue
                
                logger.info(f"✅ Got {len(proxies)} proxies from {source_name}")
                return proxies
                
        except Exception as e:
            logger.error(f"❌ Error fetching {source_name}: {e}")
            return []

    def test_proxy_speed(self, proxy, timeout=8):
        """Test proxy with speed measurement"""
        start_time = time.time()
        
        try:
            proxy_dict = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            
            response = requests.get(
                'http://httpbin.org/ip',
                proxies=proxy_dict,
                timeout=timeout
            )
            
            if response.status_code == 200:
                speed = time.time() - start_time
                logger.info(f"✅ {proxy} works (Speed: {speed:.2f}s)")
                return True, speed
                
        except Exception as e:
            logger.debug(f"❌ {proxy} failed: {e}")
            
        return False, None

    def refresh_proxy_list(self, max_test=300):
        """Continuously refresh and maintain proxy list"""
        logger.info("🔄 Starting proxy refresh cycle...")
        
        # Collect proxies from all sources
        all_proxies = set()
        for source_name, url in self.proxy_sources.items():
            proxies = self.fetch_proxies_from_source(source_name, url)
            all_proxies.update(proxies)
            
        # Remove known dead proxies
        all_proxies = all_proxies - self.dead_proxies
        
        logger.info(f"🎯 Testing {min(len(all_proxies), max_test)} proxies for reliability...")
        
        # Test proxies concurrently
        new_working = []
        proxy_speeds = {}
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            test_proxies = list(all_proxies)[:max_test]
            future_to_proxy = {
                executor.submit(self.test_proxy_speed, proxy): proxy
                for proxy in test_proxies
            }
            
            completed = 0
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                completed += 1
                
                if completed % 20 == 0:
                    logger.info(f"⏳ Tested {completed}/{len(test_proxies)} proxies...")
                
                try:
                    is_working, speed = future.result()
                    if is_working:
                        new_working.append(proxy)
                        proxy_speeds[proxy] = speed
                    else:
                        self.dead_proxies.add(proxy)
                        
                except Exception as e:
                    self.dead_proxies.add(proxy)
        
        # Update working proxies with speed scores
        self.working_proxies = new_working
        self.proxy_scores.update(proxy_speeds)
        self.last_refresh = datetime.now()
        
        logger.info(f"🎉 Found {len(new_working)} working proxies")
        logger.info(f"🗑️  Marked {len(self.dead_proxies)} dead proxies")
        
        return len(new_working)

    def get_best_proxy(self):
        """Get the fastest available proxy"""
        if not self.working_proxies:
            return None
            
        if self.proxy_scores:
            # Return fastest proxy
            best_proxy = min(self.proxy_scores.items(), key=lambda x: x[1])
            return best_proxy[0]
        
        return random.choice(self.working_proxies)

    def remove_dead_proxy(self, proxy):
        """Remove a proxy that's stopped working"""
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
            self.dead_proxies.add(proxy)
            if proxy in self.proxy_scores:
                del self.proxy_scores[proxy]
            logger.info(f"🗑️ Removed dead proxy: {proxy}")

    def should_refresh(self):
        """Check if proxy list needs refreshing"""
        if not self.last_refresh:
            return True
        return datetime.now() - self.last_refresh > timedelta(seconds=self.refresh_interval)

    def auto_maintain(self):
        """Background thread for automatic maintenance"""
        while True:
            try:
                if self.should_refresh() or len(self.working_proxies) < 5:
                    logger.info("🔧 Auto-maintenance: Refreshing proxy list...")
                    self.refresh_proxy_list()
                    
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Auto-maintenance error: {e}")
                time.sleep(120)

    def save_state(self):
        """Save current state to files"""
        # Save working proxies
        with open('enhanced_working_proxies.txt', 'w') as f:
            for proxy in self.working_proxies:
                f.write(f"{proxy}\n")
        
        # Save reliability scores
        with open('proxy_scores.json', 'w') as f:
            json.dump(self.proxy_scores, f, indent=2)
        
        # Save dead proxy list for future reference
        with open('dead_proxies.txt', 'w') as f:
            for proxy in self.dead_proxies:
                f.write(f"{proxy}\n")

    def load_state(self):
        """Load previous state if available"""
        try:
            if os.path.exists('proxy_scores.json'):
                with open('proxy_scores.json', 'r') as f:
                    self.proxy_scores = json.load(f)
            
            if os.path.exists('dead_proxies.txt'):
                with open('dead_proxies.txt', 'r') as f:
                    self.dead_proxies = set(line.strip() for line in f if line.strip())
                    
            logger.info(f"📂 Loaded {len(self.proxy_scores)} scored proxies and {len(self.dead_proxies)} dead proxies")
        except Exception as e:
            logger.error(f"Error loading state: {e}")

def main():
    print("🚀 Enhanced Proxy Chain Manager - Reliability Focus")
    print("=" * 60)
    
    manager = EnhancedProxyManager()
    
    # Load previous state
    manager.load_state()
    
    print("🔄 Performing initial proxy refresh...")
    working_count = manager.refresh_proxy_list(max_test=500)  # Test more initially
    
    if working_count == 0:
        print("❌ No working proxies found. Check your internet connection.")
        return
    
    print(f"\n✅ Successfully found {working_count} working proxies!")
    print(f"🎯 Best proxy: {manager.get_best_proxy()}")
    
    # Save current state
    manager.save_state()
    
    # Ask if user wants continuous maintenance
    print("\n🤖 Start automatic maintenance? (y/n): ", end="")
    if input().lower() == 'y':
        print("🔧 Starting background maintenance thread...")
        maintenance_thread = threading.Thread(target=manager.auto_maintain, daemon=True)
        maintenance_thread.start()
        
        print("✅ Maintenance active! Proxy list will auto-refresh every 5 minutes.")
        print("Press Ctrl+C to stop...")
        
        try:
            while True:
                time.sleep(30)
                print(f"📊 Current status: {len(manager.working_proxies)} working, {len(manager.dead_proxies)} dead")
        except KeyboardInterrupt:
            print("\n👋 Stopping maintenance...")
            manager.save_state()
            
    else:
        print("📁 Files saved:")
        print("  - enhanced_working_proxies.txt")
        print("  - proxy_scores.json") 
        print("  - dead_proxies.txt")

if __name__ == "__main__":
    main()
